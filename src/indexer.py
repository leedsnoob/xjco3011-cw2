"""Indexer module for building an inverted index from crawled pages."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TypedDict

from src.crawler import BASE_URL, CrawledPage


WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")


class Posting(TypedDict):
    frequency: int
    positions: list[int]


class PageInfo(TypedDict):
    title: str
    word_count: int


class Metadata(TypedDict):
    base_url: str
    built_at: str
    page_count: int
    document_lengths: dict[str, int]


class SerializableIndex(TypedDict):
    metadata: Metadata
    pages: dict[str, PageInfo]
    index: dict[str, dict[str, Posting]]


@dataclass(frozen=True)
class PageDocument:
    """Page text prepared for indexing."""

    url: str
    title: str
    text: str

    @classmethod
    def from_crawled_page(cls, page: CrawledPage) -> "PageDocument":
        return cls(url=page.url, title=page.title, text=page.text)


def tokenize(text: str) -> list[str]:
    """Return lowercase word tokens while preserving simple apostrophes."""

    return [match.group(0).lower() for match in WORD_RE.finditer(text)]


def build_inverted_index(documents: list[PageDocument]) -> dict[str, dict[str, Posting]]:
    """Build an inverted index with frequency and position statistics."""

    index: dict[str, dict[str, Posting]] = {}

    for document in documents:
        for position, token in enumerate(tokenize(document.text)):
            postings = index.setdefault(token, {})
            posting = postings.setdefault(
                document.url,
                {"frequency": 0, "positions": []},
            )
            posting["frequency"] += 1
            posting["positions"].append(position)

    return index


def build_search_index(
    documents: list[PageDocument],
    base_url: str = BASE_URL,
    built_at: str | None = None,
) -> SerializableIndex:
    """Build the full serializable search index payload."""

    built_at = built_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    pages: dict[str, PageInfo] = {}
    document_lengths: dict[str, int] = {}

    for document in documents:
        tokens = tokenize(document.text)
        pages[document.url] = {
            "title": document.title,
            "word_count": len(tokens),
        }
        document_lengths[document.url] = len(tokens)

    return {
        "metadata": {
            "base_url": base_url,
            "built_at": built_at,
            "page_count": len(documents),
            "document_lengths": document_lengths,
        },
        "pages": pages,
        "index": build_inverted_index(documents),
    }
