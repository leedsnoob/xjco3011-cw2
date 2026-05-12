# Benchmarks

Benchmarks measure local index loading and search ranking work. They exclude live crawling time because the 6-second politeness delay is a correctness requirement.

## Command

```bash
python3 -m src.main benchmark
python3 -m src.main benchmark --bm25-grid
python3 -m src.main benchmark --stress
```

## Current Result

Measured on the local generated `data/index.json`:

```text
Benchmark results:
- pages=10
- terms=850
- load_ms=1.661
- word_lookup_ms=0.010
- tfidf_query_ms=0.020
- bm25_query_ms=0.011
- phrase_query_ms=0.011
- explain_ms=0.016
Ranking comparison:
- tfidf_top=https://quotes.toscrape.com/page/2/ score=22.7502
- bm25_top=https://quotes.toscrape.com/page/2/ score=5.9317
BM25 parameter comparison:
- k1=0.9 b=0.4 top=https://quotes.toscrape.com/page/2/ score=5.7377 time_ms=0.005
- k1=1.2 b=0.75 top=https://quotes.toscrape.com/page/2/ score=5.9317 time_ms=0.004
- k1=1.5 b=0.9 top=https://quotes.toscrape.com/page/2/ score=6.1639 time_ms=0.003
```

Exact timings vary by machine, but the command provides reproducible evidence for comparing query processing paths.

## Synthetic Stress Result

The stress benchmark builds deterministic synthetic indexes and measures local query paths at increasing corpus sizes. It does not crawl the live website.

Command:

```bash
python3 -m src.main benchmark --stress
```

Current local result:

```text
Synthetic stress benchmark:
- query=alpha beta
- default_tokens_per_page=80
| pages | terms | index_kb | candidates | build_ms | tfidf_ms | bm25_ms | phrase_ms | explain_ms |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 245 | 479.9 | 50 | 4.995 | 0.194 | 0.144 | 0.171 | 0.224 |
| 500 | 645 | 2427.6 | 250 | 30.074 | 0.755 | 0.724 | 0.723 | 1.253 |
| 1000 | 1145 | 4862.2 | 500 | 73.177 | 1.613 | 1.679 | 2.039 | 3.272 |
```

The row growth is the important evidence: the synthetic index size and candidate count increase with the corpus, while local query timings remain low for this coursework-scale implementation.

## Function Benchmark Matrix

| Function | Benchmark metric | Complexity | Optimization evidence |
|---|---:|---|---|
| Word lookup / `print good` | `word_lookup_ms` | `O(postings(term))` | Direct inverted-index lookup; avoids full document scans |
| TF-IDF multi-term search | `tfidf_query_ms` | `O(sum postings + candidate_pages * query_terms)` | Intersects posting lists before scoring candidates |
| BM25 multi-term search | `bm25_query_ms` | `O(sum postings + candidate_pages * query_terms)` | Reuses candidates and stored document lengths |
| Exact phrase search | `phrase_query_ms` | `O(sum postings + candidate_pages * positions_checked)` | Uses stored token positions and avoids re-tokenizing text |
| Explainable ranking | `explain_ms` | `O(search + result_count * query_terms)` | Reuses ranker contribution calculations |
| Synthetic stress benchmark | `benchmark --stress` | build: `O(total_tokens)`, query: `O(sum postings + candidate_pages * query_terms)` | Scales corpus size without touching the live crawler |

The benchmark also prints a direct TF-IDF versus BM25 top-result comparison. The ranking comparison covers two algorithms; the grid covers BM25 parameter settings.

## Complexity Summary

- Build index: `O(total_tokens)`.
- Print word entry: `O(postings(term))`.
- AND query candidate selection: `O(sum postings for query terms)`.
- Phrase query: `O(candidate_pages * positions_checked)`.
- TF-IDF scoring: `O(candidate_pages * query_terms)`.
- BM25 scoring: `O(candidate_pages * query_terms)`.
- Explain command: `O(search + result_count * query_terms)`.
- Query suggestions: `O(vocabulary_size)`.
- Synthetic stress build: `O(total_tokens)`.

## Optimization Choices

- The crawler keeps live requests sequential because the assignment requires at least 6 seconds between successive live requests.
- The index stores positions at build time, so phrase search can use token offsets already stored in the index.
- Document lengths are stored in metadata, so BM25 can normalize by page length from the saved index.
- TF-IDF and BM25 reuse the same candidate set from the inverted index.
- Synthetic stress tests scale the local index/query path while preserving crawler politeness.

## Optimization Analysis

The main avoidable cost in a search engine is scanning every document for every query. This implementation builds the inverted index once. Query processing starts from posting lists, intersects candidate URLs, and then scores only the surviving candidate pages. That changes query work from a naive `O(total_tokens)` scan to `O(sum postings for query terms + candidate_pages * query_terms)`.

Phrase search is optimized by storing positions during indexing. Position data lets phrase verification check integer offsets already stored in the index.

BM25 uses stored document lengths and average document length, so length normalization is constant-time per candidate. The parameter grid is intentionally small because the corpus is small and no relevance labels are available. The comparison demonstrates ranking stability within the coursework evidence.
