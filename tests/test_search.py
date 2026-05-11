"""Tests for search behavior."""

from __future__ import annotations


def sample_index() -> dict:
    return {
        "metadata": {
            "base_url": "https://quotes.toscrape.com/",
            "built_at": "2026-05-11T00:00:00+00:00",
            "page_count": 2,
            "document_lengths": {
                "https://quotes.toscrape.com/": 6,
                "https://quotes.toscrape.com/page/2/": 5,
                "https://quotes.toscrape.com/page/3/": 120,
            },
        },
        "pages": {
            "https://quotes.toscrape.com/": {
                "title": "First",
                "word_count": 6,
            },
            "https://quotes.toscrape.com/page/2/": {
                "title": "Second",
                "word_count": 5,
            },
            "https://quotes.toscrape.com/page/3/": {
                "title": "Long",
                "word_count": 120,
            },
        },
        "index": {
            "good": {
                "https://quotes.toscrape.com/": {
                    "frequency": 1,
                    "positions": [0],
                },
                "https://quotes.toscrape.com/page/2/": {
                    "frequency": 2,
                    "positions": [0, 3],
                },
                "https://quotes.toscrape.com/page/3/": {
                    "frequency": 10,
                    "positions": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90],
                },
            },
            "friends": {
                "https://quotes.toscrape.com/page/2/": {
                    "frequency": 1,
                    "positions": [1],
                },
                "https://quotes.toscrape.com/page/3/": {
                    "frequency": 1,
                    "positions": [100],
                },
            },
            "books": {
                "https://quotes.toscrape.com/page/2/": {
                    "frequency": 1,
                    "positions": [2],
                },
            },
            "indifference": {
                "https://quotes.toscrape.com/": {
                    "frequency": 1,
                    "positions": [4],
                },
            },
        },
    }


def test_index_store_saves_and_loads_json(tmp_path) -> None:
    from src.search import IndexStore, SearchIndex

    path = tmp_path / "index.json"
    store = IndexStore(path)
    store.save(SearchIndex.from_dict(sample_index()))

    loaded = store.load()

    assert loaded.metadata["page_count"] == 2
    assert loaded.index["good"]["https://quotes.toscrape.com/page/2/"]["frequency"] == 2


def test_format_index_entry_prints_frequency_and_positions() -> None:
    from src.search import SearchIndex

    search_index = SearchIndex.from_dict(sample_index())

    output = search_index.format_index_entry("GOOD")

    assert "good" in output
    assert "frequency=2" in output
    assert "positions=[0, 3]" in output


def test_search_returns_ranked_multi_word_results() -> None:
    from src.search import SearchIndex

    search_index = SearchIndex.from_dict(sample_index())

    results = search_index.find("good friends", ranker="frequency")

    assert [result.url for result in results] == [
        "https://quotes.toscrape.com/page/3/",
        "https://quotes.toscrape.com/page/2/"
    ]
    assert results[0].score == 11
    assert results[0].matched_terms == ["good", "friends"]


def test_search_supports_phrase_query_with_positions() -> None:
    from src.search import SearchIndex

    search_index = SearchIndex.from_dict(sample_index())

    results = search_index.find('"good friends books"')

    assert [result.url for result in results] == [
        "https://quotes.toscrape.com/page/2/"
    ]


def test_non_adjacent_phrase_query_returns_no_pages() -> None:
    from src.search import SearchIndex

    search_index = SearchIndex.from_dict(sample_index())

    assert search_index.find('"good books friends"') == []


def test_search_handles_empty_and_missing_queries() -> None:
    from src.search import SearchIndex

    search_index = SearchIndex.from_dict(sample_index())

    assert search_index.find("") == []
    assert search_index.find("unicorn") == []
    assert search_index.suggest("freinds") == ["friends"]


def test_formatting_handles_missing_words_and_empty_inputs() -> None:
    from src.search import SearchIndex, format_results

    search_index = SearchIndex.from_dict(sample_index())

    assert search_index.format_index_entry("") == "No word supplied."
    assert "Suggestions" in search_index.format_index_entry("freinds")
    assert format_results([], "", search_index) == "Usage: find <query terms>"
    assert "freinds: friends" in format_results([], "freinds", search_index)
    assert format_results([], "zzzz", search_index) == "No pages found."


def test_format_explanations_handles_empty_and_missing_queries() -> None:
    from src.search import format_explanations

    assert format_explanations([], "") == "Usage: explain <query terms>"
    assert format_explanations([], "zzzz") == "No pages found."


def test_single_word_phrase_query_behaves_like_word_query() -> None:
    from src.search import SearchIndex

    search_index = SearchIndex.from_dict(sample_index())

    results = search_index.find('"good"')

    assert [result.url for result in results] == [
        "https://quotes.toscrape.com/page/3/",
        "https://quotes.toscrape.com/page/2/",
        "https://quotes.toscrape.com/",
    ]


def test_tfidf_ranker_is_available_as_default() -> None:
    from src.search import SearchIndex

    search_index = SearchIndex.from_dict(sample_index())

    explicit = search_index.find("good friends", ranker="tfidf")
    default = search_index.find("good friends")

    assert [result.url for result in default] == [result.url for result in explicit]
    assert all(isinstance(result.score, float) for result in default)


def test_bm25_penalises_very_long_documents() -> None:
    from src.search import SearchIndex

    search_index = SearchIndex.from_dict(sample_index())

    results = search_index.find("good friends", ranker="bm25")

    assert [result.url for result in results] == [
        "https://quotes.toscrape.com/page/2/",
        "https://quotes.toscrape.com/page/3/",
    ]


def test_explain_returns_term_contributions_for_ranker() -> None:
    from src.search import SearchIndex

    search_index = SearchIndex.from_dict(sample_index())

    explanations = search_index.explain("good friends", ranker="bm25")

    first = explanations[0]
    assert first["ranker"] == "bm25"
    assert first["url"] == "https://quotes.toscrape.com/page/2/"
    assert first["document_length"] == 5
    assert first["score"] > 0
    assert {"term", "tf", "df", "idf", "contribution"} <= set(first["terms"][0])


def test_bm25_parameter_score_can_be_compared() -> None:
    from src.search import SearchIndex

    search_index = SearchIndex.from_dict(sample_index())

    short_score = search_index.bm25_score_with_parameters(
        "https://quotes.toscrape.com/page/2/",
        ["good", "friends"],
        k1=1.2,
        b=0.75,
    )
    long_score = search_index.bm25_score_with_parameters(
        "https://quotes.toscrape.com/page/3/",
        ["good", "friends"],
        k1=1.2,
        b=0.75,
    )

    assert short_score > long_score


def test_unknown_ranker_is_rejected() -> None:
    import pytest
    from src.search import SearchIndex

    search_index = SearchIndex.from_dict(sample_index())

    with pytest.raises(ValueError, match="Unknown ranker"):
        search_index.find("good", ranker="not-real")
