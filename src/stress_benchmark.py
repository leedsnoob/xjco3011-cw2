"""Synthetic stress benchmarks for local search algorithms."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from collections.abc import Iterable

from src.indexer import PageDocument, build_search_index
from src.search import SearchIndex


DEFAULT_STRESS_PAGE_COUNTS = (100, 500, 1000)
DEFAULT_TOKENS_PER_PAGE = 80
STRESS_QUERY = "alpha beta"


@dataclass(frozen=True)
class StressBenchmarkResult:
    """One synthetic index benchmark row."""

    page_count: int
    unique_terms: int
    index_bytes: int
    candidate_count: int
    build_ms: float
    tfidf_query_ms: float
    bm25_query_ms: float
    phrase_query_ms: float
    explain_ms: float


def synthetic_documents(
    page_count: int,
    tokens_per_page: int = DEFAULT_TOKENS_PER_PAGE,
) -> list[PageDocument]:
    """Return deterministic synthetic documents for stress benchmarking."""

    if page_count <= 0:
        raise ValueError("page_count must be positive")
    if tokens_per_page < 6:
        raise ValueError("tokens_per_page must be at least 6")

    documents: list[PageDocument] = []
    filler_count = tokens_per_page - 6

    for page_number in range(1, page_count + 1):
        tokens = [
            "alpha",
            "beta" if page_number % 2 == 1 else "gamma",
            "quote",
            f"topic{page_number % 23}",
            f"author{page_number % 17}",
            f"page{page_number}",
        ]
        tokens.extend(f"term{(page_number + offset) % 101}" for offset in range(filler_count))
        documents.append(
            PageDocument(
                url=f"synthetic://page/{page_number}",
                title=f"Synthetic Page {page_number}",
                text=" ".join(tokens),
            )
        )

    return documents


def run_stress_benchmark(
    page_counts: Iterable[int] = DEFAULT_STRESS_PAGE_COUNTS,
    tokens_per_page: int = DEFAULT_TOKENS_PER_PAGE,
) -> list[StressBenchmarkResult]:
    """Benchmark index build and query paths across synthetic corpus sizes."""

    results: list[StressBenchmarkResult] = []

    for page_count in page_counts:
        documents = synthetic_documents(page_count, tokens_per_page=tokens_per_page)

        build_start = time.perf_counter()
        payload = build_search_index(
            documents,
            base_url="synthetic://",
            built_at="synthetic-benchmark",
        )
        index = SearchIndex.from_dict(payload)
        build_ms = (time.perf_counter() - build_start) * 1000

        index_bytes = len(json.dumps(payload, sort_keys=True).encode("utf-8"))

        tfidf_start = time.perf_counter()
        tfidf_results = index.find(STRESS_QUERY, ranker="tfidf")
        tfidf_query_ms = (time.perf_counter() - tfidf_start) * 1000

        bm25_start = time.perf_counter()
        index.find(STRESS_QUERY, ranker="bm25")
        bm25_query_ms = (time.perf_counter() - bm25_start) * 1000

        phrase_start = time.perf_counter()
        index.find(f'"{STRESS_QUERY}"', ranker="tfidf")
        phrase_query_ms = (time.perf_counter() - phrase_start) * 1000

        explain_start = time.perf_counter()
        index.explain(STRESS_QUERY, ranker="bm25")
        explain_ms = (time.perf_counter() - explain_start) * 1000

        results.append(
            StressBenchmarkResult(
                page_count=page_count,
                unique_terms=len(index.index),
                index_bytes=index_bytes,
                candidate_count=len(tfidf_results),
                build_ms=build_ms,
                tfidf_query_ms=tfidf_query_ms,
                bm25_query_ms=bm25_query_ms,
                phrase_query_ms=phrase_query_ms,
                explain_ms=explain_ms,
            )
        )

    return results


def format_stress_benchmark(results: list[StressBenchmarkResult]) -> str:
    """Return a Markdown-style table for CLI and video evidence."""

    lines = [
        "Synthetic stress benchmark:",
        f"- query={STRESS_QUERY}",
        f"- default_tokens_per_page={DEFAULT_TOKENS_PER_PAGE}",
        "| pages | terms | index_kb | candidates | build_ms | tfidf_ms | bm25_ms | phrase_ms | explain_ms |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for result in results:
        lines.append(
            f"| {result.page_count} | {result.unique_terms} | "
            f"{result.index_bytes / 1024:.1f} | {result.candidate_count} | "
            f"{result.build_ms:.3f} | {result.tfidf_query_ms:.3f} | "
            f"{result.bm25_query_ms:.3f} | {result.phrase_query_ms:.3f} | "
            f"{result.explain_ms:.3f} |"
        )

    return "\n".join(lines)
