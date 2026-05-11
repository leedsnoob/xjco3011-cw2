"""Search module for querying the persisted inverted index."""

from __future__ import annotations

import json
from dataclasses import dataclass
from difflib import get_close_matches
from pathlib import Path
from typing import Any

from src.indexer import Posting, SerializableIndex, tokenize


DEFAULT_INDEX_PATH = Path("data/index.json")


@dataclass(frozen=True)
class SearchResult:
    """One search hit returned by the query engine."""

    url: str
    title: str
    score: int
    matched_terms: list[str]


class SearchIndex:
    """Loaded inverted index with lookup and search helpers."""

    def __init__(self, payload: SerializableIndex) -> None:
        self.metadata = payload["metadata"]
        self.pages = payload["pages"]
        self.index = payload["index"]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SearchIndex":
        return cls(payload)  # The project owns this JSON shape.

    def to_dict(self) -> SerializableIndex:
        return {
            "metadata": self.metadata,
            "pages": self.pages,
            "index": self.index,
        }

    def format_index_entry(self, word: str) -> str:
        terms = tokenize(word)
        if not terms:
            return "No word supplied."

        term = terms[0]
        postings = self.index.get(term)
        if not postings:
            suggestions = self.suggest(term)
            suffix = f" Suggestions: {', '.join(suggestions)}." if suggestions else ""
            return f"No index entry found for '{term}'.{suffix}"

        lines = [f"Inverted index for '{term}':"]
        for url in sorted(postings):
            posting = postings[url]
            title = self.pages.get(url, {}).get("title", url)
            lines.append(
                f"- {url} ({title}): "
                f"frequency={posting['frequency']}, positions={posting['positions']}"
            )
        return "\n".join(lines)

    def find(self, query: str) -> list[SearchResult]:
        phrase_mode, terms = normalise_query(query)
        if not terms:
            return []

        page_sets = [set(self.index.get(term, {})) for term in terms]
        if any(not pages for pages in page_sets):
            return []

        candidate_urls = set.intersection(*page_sets)
        if phrase_mode:
            candidate_urls = {
                url for url in candidate_urls if self._contains_phrase(url, terms)
            }

        results = [
            SearchResult(
                url=url,
                title=self.pages.get(url, {}).get("title", url),
                score=sum(self.index[term][url]["frequency"] for term in terms),
                matched_terms=terms,
            )
            for url in candidate_urls
        ]

        return sorted(results, key=lambda result: (-result.score, result.url))

    def suggest(self, term: str) -> list[str]:
        return get_close_matches(term.lower(), self.index.keys(), n=3, cutoff=0.72)

    def _contains_phrase(self, url: str, terms: list[str]) -> bool:
        if len(terms) <= 1:
            return bool(terms)

        first_positions = self.index[terms[0]][url]["positions"]
        later_positions = [
            set(self.index[term][url]["positions"]) for term in terms[1:]
        ]

        for start in first_positions:
            if all(start + offset + 1 in positions for offset, positions in enumerate(later_positions)):
                return True
        return False


class IndexStore:
    """Read and write the compiled JSON index file."""

    def __init__(self, path: Path | str = DEFAULT_INDEX_PATH) -> None:
        self.path = Path(path)

    def save(self, index: SearchIndex) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(index.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def load(self) -> SearchIndex:
        if not self.path.exists():
            raise FileNotFoundError(f"Index file not found: {self.path}")
        return SearchIndex.from_dict(json.loads(self.path.read_text(encoding="utf-8")))


def normalise_query(query: str) -> tuple[bool, list[str]]:
    """Return whether query is a phrase and its normalized tokens."""

    stripped = query.strip()
    phrase_mode = len(stripped) >= 2 and stripped[0] == '"' and stripped[-1] == '"'
    if phrase_mode:
        stripped = stripped[1:-1]
    return phrase_mode, tokenize(stripped)


def format_results(results: list[SearchResult], query: str, index: SearchIndex) -> str:
    """Format search results for CLI output."""

    if not query.strip():
        return "Usage: find <query terms>"

    if not results:
        _, terms = normalise_query(query)
        suggestions = {
            term: index.suggest(term)
            for term in terms
            if term not in index.index and index.suggest(term)
        }
        if suggestions:
            hint = "; ".join(
                f"{term}: {', '.join(matches)}" for term, matches in suggestions.items()
            )
            return f"No pages found. Suggestions: {hint}"
        return "No pages found."

    lines = [f"Found {len(results)} page(s) for '{query.strip()}':"]
    for result in results:
        lines.append(
            f"- {result.url} ({result.title}) "
            f"score={result.score}, terms={', '.join(result.matched_terms)}"
        )
    return "\n".join(lines)
