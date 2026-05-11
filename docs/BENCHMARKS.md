# Benchmarks

Benchmarks measure local index loading and search ranking work. They intentionally exclude live crawling time because the 6-second politeness delay is a correctness requirement rather than an algorithmic bottleneck.

## Command

```bash
python3 -m src.main benchmark
python3 -m src.main benchmark --bm25-grid
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

## Function Benchmark Matrix

| Function | Benchmark metric | Complexity | Optimization evidence |
|---|---:|---|---|
| Word lookup / `print good` | `word_lookup_ms` | `O(postings(term))` | Direct inverted-index lookup; no full document scan |
| TF-IDF multi-term search | `tfidf_query_ms` | `O(sum postings + candidate_pages * query_terms)` | Intersects posting lists before scoring candidates |
| BM25 multi-term search | `bm25_query_ms` | `O(sum postings + candidate_pages * query_terms)` | Reuses candidates and stored document lengths |
| Exact phrase search | `phrase_query_ms` | `O(sum postings + candidate_pages * positions_checked)` | Uses stored token positions instead of re-tokenizing text |
| Explainable ranking | `explain_ms` | `O(search + result_count * query_terms)` | Reuses ranker contribution calculations |

The benchmark also prints a direct TF-IDF versus BM25 top-result comparison. This is separate from the BM25 parameter grid: the ranking comparison compares two ranking algorithms, while the grid compares BM25 parameter settings.

## Complexity Summary

- Build index: `O(total_tokens)`.
- Print word entry: `O(postings(term))`.
- AND query candidate selection: `O(sum postings for query terms)`.
- Phrase query: `O(candidate_pages * positions_checked)`.
- TF-IDF scoring: `O(candidate_pages * query_terms)`.
- BM25 scoring: `O(candidate_pages * query_terms)`.
- Explain command: `O(search + result_count * query_terms)`.
- Query suggestions: `O(vocabulary_size)`.

## Optimization Choices

- The crawler is not parallelized because the assignment requires at least 6 seconds between successive live requests.
- The index stores positions at build time, so phrase search does not need to re-tokenize page text.
- Document lengths are stored in metadata, so BM25 can normalize by page length without rereading documents.
- TF-IDF and BM25 reuse the same candidate set from the inverted index.

## Optimization Analysis

The main avoidable cost in a search engine is scanning every document for every query. This implementation avoids that by building the inverted index once. Query processing starts from posting lists, intersects candidate URLs, and then scores only the surviving candidate pages. That changes query work from a naive `O(total_tokens)` scan to `O(sum postings for query terms + candidate_pages * query_terms)`.

Phrase search is optimized by storing positions during indexing. Without positions, phrase queries would need to reload or re-tokenize each candidate page. With positions, phrase verification checks integer offsets already stored in the index.

BM25 uses stored document lengths and average document length, so length normalization is constant-time per candidate. The parameter grid is intentionally small because the corpus is small and no relevance labels are available. The comparison demonstrates ranking stability rather than claiming a trained optimum.
