"""Tests for inverted index behavior."""

from __future__ import annotations


def test_tokenize_lowercases_and_keeps_apostrophes() -> None:
    from src.indexer import tokenize

    assert tokenize("Good, GOOD! Don't stop.") == [
        "good",
        "good",
        "don't",
        "stop",
    ]


def test_build_search_index_records_frequency_and_positions() -> None:
    from src.indexer import PageDocument, build_search_index

    documents = [
        PageDocument(
            url="https://quotes.toscrape.com/",
            title="First",
            text="Good friends are good.",
        ),
        PageDocument(
            url="https://quotes.toscrape.com/page/2/",
            title="Second",
            text="Friends choose books.",
        ),
    ]

    search_index = build_search_index(documents)

    assert search_index["index"]["good"]["https://quotes.toscrape.com/"] == {
        "frequency": 2,
        "positions": [0, 3],
    }
    assert search_index["index"]["friends"][
        "https://quotes.toscrape.com/page/2/"
    ] == {"frequency": 1, "positions": [0]}
    assert search_index["metadata"]["page_count"] == 2
    assert search_index["metadata"]["document_lengths"][
        "https://quotes.toscrape.com/"
    ] == 4
    assert search_index["pages"]["https://quotes.toscrape.com/"]["title"] == "First"
