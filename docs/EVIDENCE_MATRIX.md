# Coursework Evidence Matrix

This file maps high-band marking expectations to concrete repository evidence. It is intended for the video walkthrough and final self-check.

## TDD Evidence Across the Project

TDD is shown as a repeated workflow, not a single isolated commit.

| Area | Test-first evidence | Implementation evidence | Verification |
|---|---|---|---|
| Core crawler, index, search, CLI | `552f5fc test: define coursework search engine behavior` | `9efe172 feat: implement crawler and inverted index`, `f5d9a1f feat: implement search persistence and CLI` | `tests/test_crawler.py`, `tests/test_indexer.py`, `tests/test_search.py`, `tests/test_main.py` |
| CLI and search edge cases | `d2866ff test: raise coverage for CLI and search edges` | Existing CLI/search behavior hardened before release | `python3 -m pytest --cov=src --cov-report=term-missing` |
| Mocked crawler and quality gates | `4575075 test: strengthen mocked edge case coverage` | `6b9a21c ci: add automated pytest coverage workflow` | `.github/workflows/tests.yml`, `pyproject.toml` |
| TF-IDF, BM25, explain, benchmark | `23bcd9d test: cover tf-idf bm25 explain and benchmark` | `c2fa7a2 feat: add explainable tf-idf and bm25 ranking` | `python3 -m src.main explain good friends` |
| BM25 parameter comparison | `a8f9f51 test: cover coverage gaps and bm25 parameter comparison` | `a89b4dd feat: add bm25 parameter benchmark comparison` | `python3 -m src.main benchmark --bm25-grid` |
| Remaining edge coverage | `6bf8d73 test: cover interactive and malformed crawler edges` | Existing production behavior verified by new tests | 100% line and branch coverage report |

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
| CLI errors without traceback | `tests/test_main.py` |
| Interactive shell EOF and exit behavior | `tests/test_main.py` |
| CI coverage gate | `.github/workflows/tests.yml`, `pyproject.toml` |

Current local verification:

```text
44 passed
Total coverage: 100.00%
```

## Algorithm and Optimization Evidence

The implementation optimizes the query path rather than the crawler wait time. The crawler delay is a correctness requirement, so removing or parallelizing it would weaken the submission.

| Optimization decision | Why it matters | Evidence |
|---|---|---|
| Inverted index | Avoids scanning all page text for every query | `src/indexer.py`, `src/search.py` |
| Positional postings | Enables phrase search without re-tokenizing page text | `positions` in `data/index.json` |
| Candidate intersection before scoring | Scores only pages containing all query terms | `SearchIndex.find` |
| Stored document lengths | BM25 length normalization avoids rereading documents | `metadata.document_lengths` |
| TF-IDF default ranking | Improves raw frequency by weighting rare terms | `SearchIndex.term_contribution` |
| BM25 optional ranking | Adds term saturation and length normalization | `SearchIndex.bm25_contribution` |
| Explain command | Makes ranking transparent and auditable | `python3 -m src.main explain good friends` |
| Benchmark command | Measures local query and ranking costs | `python3 -m src.main benchmark --bm25-grid` |

## BM25 Parameter Evidence

The project compares common BM25 settings but does not claim supervised tuning because the coursework provides no labelled relevance judgments. The selected default remains the standard `k1=1.2, b=0.75`.

Current local comparison:

```text
BM25 parameter comparison:
- k1=0.9 b=0.4 top=https://quotes.toscrape.com/page/2/ score=5.7377
- k1=1.2 b=0.75 top=https://quotes.toscrape.com/page/2/ score=5.9317
- k1=1.5 b=0.9 top=https://quotes.toscrape.com/page/2/ score=6.1639
```

The top result is stable across these settings for `good friends`, so the implementation uses the standard default rather than overfitting parameters to one small corpus.
