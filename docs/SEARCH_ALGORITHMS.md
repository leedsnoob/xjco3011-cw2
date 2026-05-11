# Search Algorithms and Complexity

## Inverted Index

The project uses an inverted index to avoid scanning every page for every query. Each term maps to the pages where it appears, and each posting stores:

- `frequency`: how many times the term appears on the page.
- `positions`: token offsets inside the page.

This supports the coursework requirement to store word statistics and enables phrase queries.

Complexity:

- Build index: `O(total_tokens)`.
- Print one word: `O(postings(term))`.
- Storage: `O(unique_term_page_pairs + total_positions)`.

## Positional Index and Phrase Search

Phrase search needs word order. A plain word-to-page index can show that `good`, `friends`, and `books` appear on a page. Positions prove that those terms appear consecutively:

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

TF-IDF uses no machine-learning training. It is computed from the crawled corpus:

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

BM25 is a modern keyword ranking function related to TF-IDF. It also uses document frequency and adds term-frequency saturation and document-length normalization:

```text
score = idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * document_length / average_document_length)))
```

The project uses common defaults:

```text
k1 = 1.2
b = 0.75
```

These values remain standard defaults because the coursework provides no labelled relevance judgments for supervised tuning. This choice demonstrates a stronger ranking algorithm while keeping the evidence aligned with the available data.

Complexity:

- Same candidate and scoring order as TF-IDF: `O(candidate_pages * query_terms)`.
- Slightly higher constant cost due to the BM25 formula.

### Parameter Comparison

The benchmark command can compare three common BM25 settings:

```bash
python3 -m src.main benchmark --bm25-grid
```

The comparison currently checks:

```text
k1=0.9, b=0.4
k1=1.2, b=0.75
k1=1.5, b=0.9
```

The project keeps `k1=1.2, b=0.75` as the default because it is a standard information-retrieval baseline and the coursework provides no labelled query relevance data. The parameter comparison is evidence of ranking stability and implementation understanding.

## Query Suggestions

For missing words, the project uses close string matching over the vocabulary. This is useful for small coursework corpora and easy to explain.

Complexity:

- `O(vocabulary_size)` per suggestion lookup with the standard-library matching approach.

## Benchmarking Scope

Benchmarks measure local algorithm performance:

- index load time;
- word lookup time;
- TF-IDF query time;
- BM25 query time;
- phrase query time;
- explain command time;
- TF-IDF scoring time;
- BM25 scoring time.

The benchmark intentionally excludes live crawling delay because the 6-second politeness window is a correctness requirement, not an algorithmic bottleneck to optimize away.

## Four Search Functions: Tests, Complexity, and Optimization

| Function | Test evidence | Time complexity | Optimization |
|---|---|---|---|
| `print <word>` lookup | `test_format_index_entry_prints_frequency_and_positions`, `test_load_print_and_find_commands_use_persisted_index` | `O(postings(term))` | Uses direct dictionary lookup into the inverted index |
| TF-IDF ranked `find` | `test_tfidf_ranker_is_available_as_default`, `test_cli_benchmark_command_reports_timings` | `O(sum postings + candidate_pages * query_terms)` | Intersects candidate pages before scoring |
| BM25 ranked `find --ranker bm25` | `test_bm25_penalises_very_long_documents`, `test_cli_find_accepts_ranker_option` | `O(sum postings + candidate_pages * query_terms)` | Reuses candidates and stored document lengths for normalization |
| Exact phrase search | `test_search_supports_phrase_query_with_positions`, `test_non_adjacent_phrase_query_returns_no_pages` | `O(sum postings + candidate_pages * positions_checked)` | Uses stored positions and avoids raw page scans |

The benchmark command also measures `explain`, which has complexity `O(search + result_count * query_terms)` because it performs the ranking search and then reports each term contribution for each returned result.

## TF-IDF vs BM25 Comparison

The two ranking algorithms are compared in two ways:

- Timing: `tfidf_query_ms` and `bm25_query_ms` are printed by `python3 -m src.main benchmark`.
- Ranking result: the same command prints `tfidf_top=...` and `bm25_top=...`, so the video can show whether the algorithms agree or diverge on the top result.

TF-IDF offers a clear baseline: it rewards terms that are frequent in a document and rare across the corpus. BM25 adds term-frequency saturation and document-length normalization. The implementation keeps both so the coursework can demonstrate a transparent baseline and a stronger modern ranking method.

## What Was Optimized

A naive implementation could store only raw page text and scan every token on every query. That would make each query `O(total_tokens)`. This project instead pays the indexing cost once, then answers queries from posting lists:

- Candidate retrieval uses inverted-index lookups.
- Multi-word queries intersect URL sets before scoring.
- Phrase queries use stored positions and avoid re-tokenizing page text.
- TF-IDF and BM25 score only candidate pages.
- BM25 uses stored document lengths and the precomputed average document length.

The result is a small and scalable design: adding pages increases index size, while common query work grows mainly with posting-list size and candidate count.

## Modern Search Practice: Search Engines and Browser Search Fields

Search-engine research focuses on crawling, indexing, ranking, latency, relevance, quality, usability, and query understanding. Google Search documentation describes the system as an index of web content that is ranked in a fraction of a second. Google also lists query words, page relevance and usability, source expertise, location, and settings as ranking signals. Google Search Central separates crawling and indexing from ranking and search appearance.

Safari and Chrome provide browser search fields that connect users to search engines and suggestions. Safari Search settings allow a regular search engine, a Private Browsing search engine, search engine suggestions, Safari Suggestions, Quick Website Search, and Top Hit preloading. Chrome's address bar combines URL and search input, uses local history plus the default search engine for suggestions, can preconnect to the default search engine, and can send typed text to the default search engine when enhanced suggestions are enabled.

This coursework implements the search-engine side of the problem: crawling, indexing, query processing, ranking, explainability, and benchmarking. It adopts one browser-style practice, query suggestions, using the local vocabulary in the compiled index. It avoids browser-level personalization and remote suggestion APIs to keep the implementation deterministic, private, and suitable for assessment.

Sources:

- Google Search, "How Google Search works": https://www.google.com/intl/en_us/search/howsearchworks/how-search-works/
- Google Search, "Automatically generating and ranking results": https://www.google.com/intl/en_us/search/howsearchworks/how-search-works/ranking-results/
- Google Search Central, "Crawling and indexing": https://developers.google.com/search/docs/crawling-indexing
- Apple Support, "Change Search settings in Safari on Mac": https://support.apple.com/guide/safari/search-sfria1042d31/mac
- Google Chrome Help, "How Chrome keeps your URL & search data private": https://support.google.com/chrome/answer/13730681
