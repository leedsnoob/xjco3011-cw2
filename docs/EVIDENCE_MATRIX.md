# Coursework Evidence Matrix

This file maps high-band marking expectations to concrete repository evidence. It is intended for the video walkthrough and final self-check.

## TDD Evidence Across the Project

TDD is shown as a repeated workflow across several commits.

| Area | Test-first evidence | Implementation evidence | Verification |
|---|---|---|---|
| Core crawler, index, search, CLI | `552f5fc test: define coursework search engine behavior` | `9efe172 feat: implement crawler and inverted index`, `f5d9a1f feat: implement search persistence and CLI` | `tests/test_crawler.py`, `tests/test_indexer.py`, `tests/test_search.py`, `tests/test_main.py` |
| CLI and search edge cases | `d2866ff test: raise coverage for CLI and search edges` | Existing CLI/search behavior hardened before release | `python3 -m pytest --cov=src --cov-report=term-missing` |
| Invalid index file handling | Current invalid-index regression tests in `tests/test_search.py` and `tests/test_main.py` | `InvalidIndexError` converts corrupt JSON into a user-facing rebuild message | `load`, `find`, `explain`, and `benchmark` do not expose JSON tracebacks |
| Mocked crawler and quality gates | `4575075 test: strengthen mocked edge case coverage` | `6b9a21c ci: add automated pytest coverage workflow` | `.github/workflows/tests.yml`, `pyproject.toml` |
| TF-IDF, BM25, explain, benchmark | `23bcd9d test: cover tf-idf bm25 explain and benchmark` | `c2fa7a2 feat: add explainable tf-idf and bm25 ranking` | `python3 -m src.main explain good friends` |
| BM25 parameter comparison | `a8f9f51 test: cover coverage gaps and bm25 parameter comparison` | `a89b4dd feat: add bm25 parameter benchmark comparison` | `python3 -m src.main benchmark --bm25-grid` |
| Remaining edge coverage | `6bf8d73 test: cover interactive and malformed crawler edges` | Existing production behavior verified by new tests | 100% line and branch coverage report |
| Extreme input hardening | `0b105cc test: cover malformed queries and empty benchmark grid` | `b99450f fix: handle malformed queries and empty benchmark candidates` | malformed ranker, unmatched quote, empty benchmark grid tests |
| Algorithm comparison evidence | `9e040da test: require algorithm comparison benchmark evidence` | `15d7efc feat: compare ranking algorithms in benchmark output` | `tfidf_top`, `bm25_top`, and per-function timings |
| Naive versus optimized benchmark evidence | Current benchmark baseline tests in `tests/test_search.py`, `tests/test_main.py`, and `tests/test_stress_benchmark.py` | `SearchIndex.naive_scan_find`, `benchmark`, and `benchmark --stress` report naive scan time, optimized query time, and speedup | `naive_scan_ms`, `optimized_query_ms`, `optimized_vs_naive_speedup` |
| Release-quality hardening | `feature/release-quality-hardening` | docstrings, type hints, `.env` ignore rules, engineering practice notes | `python3 -m compileall src tests` |
| Documentation tone review | `feature/documentation-tone-review` | English-only project docs, direct wording, Safari/Chrome practice comparison, source links | markdown wording scan and local link check |
| Synthetic stress benchmarking | `1d3da13 test: cover synthetic stress benchmark behavior` | `8671eff feat: add synthetic stress benchmark command` | `python3 -m src.main benchmark --stress` |
| CLI progress output | `cff19ea test: require visible CLI progress output` | `0fd64da feat: add progress output to CLI commands` | `python3 -m src.main build`, `python3 -m src.main benchmark --stress` |

The key video command is:

```bash
git log --oneline --graph --decorate --all --max-count=30
```

It shows test commits before the corresponding feature commits on feature branches.

## Testing Evidence

The suite uses unit, integration-style CLI, persistence, and mocked crawler tests.

| Evidence | Location |
|---|---|
| Mocked network responses | `tests/fixtures.py`, `tests/test_crawler.py` |
| Mocked politeness delay | `test_crawler_follows_pagination_and_extracts_quote_text` |
| HTTP error and low-level request exception handling | `tests/test_crawler.py` |
| Duplicate pagination guard | `tests/test_crawler.py` |
| Malformed quote HTML tolerance | `test_parse_page_tolerates_quotes_without_text_or_author` |
| Index tokenization, frequency, positions | `tests/test_indexer.py` |
| Save/load round trip | `tests/test_search.py` |
| TF-IDF, BM25, exact phrase, suggestions | `tests/test_search.py` |
| CLI errors with friendly messages | `tests/test_main.py` |
| Interactive shell EOF and exit behavior | `tests/test_main.py` |
| Malformed `--ranker` usage | `tests/test_main.py` |
| Unmatched quote query handling | `tests/test_main.py`, `tests/test_search.py` |
| Empty-index benchmark grid handling | `tests/test_main.py` |
| Synthetic stress benchmark behavior | `tests/test_stress_benchmark.py`, `tests/test_main.py` |
| CI coverage gate | `.github/workflows/tests.yml`, `pyproject.toml` |

Current local verification:

```text
60 passed
Total coverage: 100.00%
```

## Algorithm and Optimization Evidence

The implementation optimizes the query path. The crawler delay is a correctness requirement, so removing or parallelizing it would weaken the submission.

| Optimization decision | Why it matters | Evidence |
|---|---|---|
| Inverted index | Avoids scanning all page text for every query | `src/indexer.py`, `src/search.py` |
| Positional postings | Enables phrase search from stored token offsets | `positions` in `data/index.json` |
| Candidate intersection before scoring | Scores only pages containing all query terms | `SearchIndex.find` |
| Stored document lengths | BM25 length normalization avoids rereading documents | `metadata.document_lengths` |
| TF-IDF default ranking | Improves raw frequency by weighting rare terms | `SearchIndex.term_contribution` |
| BM25 optional ranking | Adds term saturation and length normalization | `SearchIndex.bm25_contribution` |
| Explain command | Makes ranking transparent and auditable | `python3 -m src.main explain good friends` |
| Benchmark command | Measures local query and ranking costs | `python3 -m src.main benchmark --bm25-grid` |
| Stress benchmark command | Measures synthetic scaling for local index/query work | `python3 -m src.main benchmark --stress` |
| Ranking comparison | Compares TF-IDF and BM25 top results directly | `Ranking comparison:` benchmark output |
| Engineering practice | Records code-structure, `.env`, type-hint, docstring, CI, and release decisions | `docs/ENGINEERING_PRACTICES.md` |

## BM25 Parameter Evidence

The project compares common BM25 settings and makes no supervised-tuning claim because the coursework provides no labelled relevance judgments. The selected default remains the standard `k1=1.2, b=0.75`.

Current local comparison:

```text
BM25 parameter comparison:
- k1=0.9 b=0.4 top=https://quotes.toscrape.com/page/2/ score=5.7377
- k1=1.2 b=0.75 top=https://quotes.toscrape.com/page/2/ score=5.9317
- k1=1.5 b=0.9 top=https://quotes.toscrape.com/page/2/ score=6.1639
```

The top result is stable across these settings for `good friends`, so the implementation uses the standard default and avoids overfitting parameters to one small corpus.
