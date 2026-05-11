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
            },
            "friends": {
                "https://quotes.toscrape.com/page/2/": {
                    "frequency": 1,
                    "positions": [1],
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

    results = search_index.find("good friends")

    assert [result.url for result in results] == [
        "https://quotes.toscrape.com/page/2/"
    ]
    assert results[0].score == 3
    assert results[0].matched_terms == ["good", "friends"]


def test_search_supports_phrase_query_with_positions() -> None:
    from src.search import SearchIndex

    search_index = SearchIndex.from_dict(sample_index())

    results = search_index.find('"good friends books"')

    assert [result.url for result in results] == [
        "https://quotes.toscrape.com/page/2/"
    ]


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
    assert format_results([], "zzzz", search_index) == "No pages found."


def test_single_word_phrase_query_behaves_like_word_query() -> None:
    from src.search import SearchIndex

    search_index = SearchIndex.from_dict(sample_index())

    results = search_index.find('"good"')

    assert [result.url for result in results] == [
        "https://quotes.toscrape.com/page/2/",
        "https://quotes.toscrape.com/",
    ]
