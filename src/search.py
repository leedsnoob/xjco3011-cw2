"""Search module for querying the persisted inverted index."""

from __future__ import annotations

import json
import math
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
    score: float
    matched_terms: list[str]


class SearchIndex:
    """Loaded inverted index with lookup and search helpers."""

    def __init__(self, payload: SerializableIndex) -> None:
        self.metadata = payload["metadata"]
        self.pages = payload["pages"]
        self.index = payload["index"]
        lengths = self.metadata.get("document_lengths", {})
        self.average_document_length = (
            sum(lengths.values()) / len(lengths) if lengths else 0.0
        )

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

    def find(self, query: str, ranker: str = "tfidf") -> list[SearchResult]:
        phrase_mode, terms = normalise_query(query)
        if not terms:
            return []
        validate_ranker(ranker)

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
                score=self.score(url, terms, ranker),
                matched_terms=terms,
            )
            for url in candidate_urls
        ]

        return sorted(results, key=lambda result: (-result.score, result.url))

    def explain(self, query: str, ranker: str = "tfidf") -> list[dict[str, Any]]:
        _, terms = normalise_query(query)
        results = self.find(query, ranker=ranker)
        explanations: list[dict[str, Any]] = []

        for result in results:
            term_details = [
                self.term_contribution(result.url, term, ranker) for term in terms
            ]
            explanations.append(
                {
                    "ranker": ranker,
                    "url": result.url,
                    "title": result.title,
                    "score": result.score,
                    "document_length": self.document_length(result.url),
                    "average_document_length": self.average_document_length,
                    "terms": term_details,
                }
            )
        return explanations

    def score(self, url: str, terms: list[str], ranker: str) -> float:
        return sum(self.term_contribution(url, term, ranker)["contribution"] for term in terms)

    def term_contribution(self, url: str, term: str, ranker: str) -> dict[str, Any]:
        validate_ranker(ranker)
        posting = self.index[term][url]
        tf = posting["frequency"]
        df = len(self.index[term])
        idf = self.idf(term)

        if ranker == "frequency":
            contribution = float(tf)
        elif ranker == "tfidf":
            contribution = tf * idf
        else:
            contribution = self.bm25_contribution(url, tf, idf)

        return {
            "term": term,
            "tf": tf,
            "df": df,
            "idf": idf,
            "contribution": contribution,
        }

    def idf(self, term: str) -> float:
        page_count = self.metadata["page_count"]
        df = len(self.index.get(term, {}))
        return math.log((page_count + 1) / (df + 1)) + 1

    def bm25_contribution(
        self,
        url: str,
        tf: int,
        idf: float,
        k1: float = 1.2,
        b: float = 0.75,
    ) -> float:
        doc_length = self.document_length(url)
        avg_length = self.average_document_length or 1.0
        denominator = tf + k1 * (1 - b + b * (doc_length / avg_length))
        return idf * ((tf * (k1 + 1)) / denominator)

    def bm25_score_with_parameters(
        self,
        url: str,
        terms: list[str],
        k1: float,
        b: float,
    ) -> float:
        return sum(
            self.bm25_contribution(
                url,
                self.index[term][url]["frequency"],
                self.idf(term),
                k1=k1,
                b=b,
            )
            for term in terms
            if url in self.index.get(term, {})
        )

    def document_length(self, url: str) -> int:
        return self.metadata.get("document_lengths", {}).get(
            url,
            self.pages.get(url, {}).get("word_count", 0),
        )

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


def validate_ranker(ranker: str) -> None:
    if ranker not in {"frequency", "tfidf", "bm25"}:
        raise ValueError(f"Unknown ranker: {ranker}")


def format_results(
    results: list[SearchResult],
    query: str,
    index: SearchIndex,
    ranker: str = "tfidf",
) -> str:
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

    lines = [f"Found {len(results)} page(s) for '{query.strip()}' using {ranker}:"]
    for result in results:
        lines.append(
            f"- {result.url} ({result.title}) "
            f"score={result.score:.4f}, terms={', '.join(result.matched_terms)}"
        )
    return "\n".join(lines)


def format_explanations(explanations: list[dict[str, Any]], query: str) -> str:
    if not query.strip():
        return "Usage: explain <query terms>"
    if not explanations:
        return "No pages found."

    lines: list[str] = [f"Explanation for '{query.strip()}':"]
    for explanation in explanations:
        lines.append(
            f"- {explanation['url']} ({explanation['title']}) "
            f"ranker={explanation['ranker']} score={explanation['score']:.4f} "
            f"document_length={explanation['document_length']} "
            f"average_document_length={explanation['average_document_length']:.2f}"
        )
        for term in explanation["terms"]:
            lines.append(
                f"  {term['term']}: tf={term['tf']} df={term['df']} "
                f"idf={term['idf']:.4f} contribution={term['contribution']:.4f}"
            )
    return "\n".join(lines)
