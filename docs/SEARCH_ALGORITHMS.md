# Search Algorithms and Complexity

## Inverted Index

The project uses an inverted index rather than scanning every page for every query. Each term maps to the pages where it appears, and each posting stores:

- `frequency`: how many times the term appears on the page.
- `positions`: token offsets inside the page.

This supports the coursework requirement to store word statistics and enables phrase queries.

Complexity:

- Build index: `O(total_tokens)`.
- Print one word: `O(postings(term))`.
- Storage: `O(unique_term_page_pairs + total_positions)`.

## Positional Index and Phrase Search

Phrase search needs word order. A plain word-to-page index can show that `good`, `friends`, and `books` appear on a page, but it cannot prove that they appear consecutively. Positions solve that:

```text
good:    positions [10]
friends: positions [11]
books:   positions [12]
```

For `"good friends books"`, the search checks whether each later term appears at `start + offset`.

Complexity:

- Candidate selection: `O(sum postings for query terms)`.
- Phrase verification: `O(candidate_pages * positions_checked)`.

## Boolean Query Processing

Multi-word unquoted queries use AND semantics. `find good friends` returns pages that contain both terms. The implementation intersects the page sets for the query terms.

Complexity:

- `O(sum postings for query terms)` to gather and intersect candidates.
- `O(candidate_pages * query_terms)` to score results.

## TF-IDF Ranking

TF-IDF does not require machine-learning training. It is computed from the crawled corpus:

```text
tf(term, page) = frequency of term in page
df(term) = number of pages containing term
idf(term) = log((N + 1) / (df(term) + 1)) + 1
score(page, query) = sum(tf * idf for each query term)
```

TF-IDF improves on raw frequency because rare, more discriminative terms receive more weight than common terms.

Complexity:

- Document frequency lookup: `O(query_terms)`.
- Scoring: `O(candidate_pages * query_terms)`.

## BM25 Ranking

BM25 is a modern keyword ranking function related to TF-IDF. It also uses document frequency but adds term-frequency saturation and document-length normalization:

```text
score = idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * document_length / average_document_length)))
```

The project uses common defaults:

```text
k1 = 1.2
b = 0.75
```

These values are not trained because the coursework does not provide labelled relevance judgments. Using standard defaults is a deliberate trade-off: it demonstrates a stronger ranking algorithm without pretending to tune parameters from unavailable data.

Complexity:

- Same candidate and scoring order as TF-IDF: `O(candidate_pages * query_terms)`.
- Slightly higher constant cost due to the BM25 formula.

## Query Suggestions

For missing words, the project uses close string matching over the vocabulary. This is useful for small coursework corpora and easy to explain.

Complexity:

- `O(vocabulary_size)` per suggestion lookup with the standard-library matching approach.

## Benchmarking Scope

Benchmarks measure local algorithm performance:

- index load time;
- query time;
- phrase query time;
- TF-IDF scoring time;
- BM25 scoring time.

The benchmark intentionally excludes live crawling delay because the 6-second politeness window is a correctness requirement, not an algorithmic bottleneck to optimize away.
