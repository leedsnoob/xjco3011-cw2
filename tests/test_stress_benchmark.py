from __future__ import annotations

import pytest

from src.stress_benchmark import (
    format_stress_benchmark,
    run_stress_benchmark,
    synthetic_documents,
)


def test_synthetic_documents_scale_deterministically() -> None:
    documents = synthetic_documents(page_count=3, tokens_per_page=12)

    assert [document.url for document in documents] == [
        "synthetic://page/1",
        "synthetic://page/2",
        "synthetic://page/3",
    ]
    assert all("alpha" in document.text for document in documents)
    assert "beta" in documents[0].text


def test_stress_benchmark_reports_growth_across_synthetic_sizes() -> None:
    results = run_stress_benchmark(page_counts=(5, 10), tokens_per_page=20)

    assert [result.page_count for result in results] == [5, 10]
    assert results[1].index_bytes > results[0].index_bytes
    assert results[1].unique_terms >= results[0].unique_terms

    for result in results:
        assert result.candidate_count > 0
        assert result.build_ms >= 0
        assert result.naive_scan_ms >= 0
        assert result.optimized_query_ms >= 0
        assert result.optimized_vs_naive_speedup >= 0
        assert result.tfidf_query_ms >= 0
        assert result.bm25_query_ms >= 0
        assert result.phrase_query_ms >= 0
        assert result.explain_ms >= 0


def test_format_stress_benchmark_is_video_ready() -> None:
    results = run_stress_benchmark(page_counts=(4,), tokens_per_page=16)

    output = format_stress_benchmark(results)

    assert "Synthetic stress benchmark:" in output
    assert "| pages | terms | index_kb | candidates | build_ms | naive_ms | optimized_ms | speedup |" in output
    assert "| 4 |" in output


def test_synthetic_stress_benchmark_validates_input() -> None:
    with pytest.raises(ValueError, match="page_count must be positive"):
        synthetic_documents(page_count=0, tokens_per_page=10)

    with pytest.raises(ValueError, match="tokens_per_page must be at least 6"):
        synthetic_documents(page_count=1, tokens_per_page=5)
