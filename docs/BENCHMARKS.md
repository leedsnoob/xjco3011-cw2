# Benchmarks

Benchmarks measure local index loading and search ranking work. They intentionally exclude live crawling time because the 6-second politeness delay is a correctness requirement rather than an algorithmic bottleneck.

## Command

```bash
python3 -m src.main benchmark
```

## Current Result

Measured on the local generated `data/index.json`:

```text
Benchmark results:
- pages=10
- terms=850
- load_ms=1.505
- tfidf_query_ms=0.023
- bm25_query_ms=0.012
- phrase_query_ms=0.011
```

Exact timings vary by machine, but the command provides reproducible evidence for comparing query processing paths.

## Complexity Summary

- Build index: `O(total_tokens)`.
- Print word entry: `O(postings(term))`.
- AND query candidate selection: `O(sum postings for query terms)`.
- Phrase query: `O(candidate_pages * positions_checked)`.
- TF-IDF scoring: `O(candidate_pages * query_terms)`.
- BM25 scoring: `O(candidate_pages * query_terms)`.
- Query suggestions: `O(vocabulary_size)`.

## Optimization Choices

- The crawler is not parallelized because the assignment requires at least 6 seconds between successive live requests.
- The index stores positions at build time, so phrase search does not need to re-tokenize page text.
- Document lengths are stored in metadata, so BM25 can normalize by page length without rereading documents.
- TF-IDF and BM25 reuse the same candidate set from the inverted index.
