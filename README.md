# XJCO3011 CW2 Search Engine

[![Tests](https://github.com/leedsnoob/xjco3011-cw2/actions/workflows/tests.yml/badge.svg)](https://github.com/leedsnoob/xjco3011-cw2/actions/workflows/tests.yml)
[![Release](https://img.shields.io/github/v/release/leedsnoob/xjco3011-cw2)](https://github.com/leedsnoob/xjco3011-cw2/releases)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)

A Python command-line search engine for `https://quotes.toscrape.com/`, built for XJCO3011 Coursework 2.

The project crawls the quote website politely, builds a case-insensitive inverted index with word frequencies and token positions, stores the compiled index as JSON, and supports lookup, ranked search, exact phrase search, query suggestions, explainable ranking, and local benchmarks.

## Contents

- [Highlights](#highlights)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Command Reference](#command-reference)
- [Architecture](#architecture)
- [Index Format](#index-format)
- [Ranking and Query Features](#ranking-and-query-features)
- [Performance](#performance)
- [Testing and CI](#testing-and-ci)
- [Project Structure](#project-structure)
- [Coursework Evidence](#coursework-evidence)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)
- [Limitations](#limitations)
- [Academic Use](#academic-use)

## Highlights

- Crawls all paginated quote pages from `https://quotes.toscrape.com/`.
- Enforces a minimum 6-second delay between successive live website requests.
- Builds a deterministic inverted index with lowercase terms, per-page frequency, token positions, document lengths, and page metadata.
- Persists the compiled index to `data/index.json` for repeatable search after a single crawl.
- Provides the required coursework commands: `build`, `load`, `print <word>`, and `find <query>`.
- Adds higher-band search features: TF-IDF ranking, optional BM25 ranking, exact phrase search, typo suggestions, explainable score breakdowns, and benchmark output.
- Adds a synthetic stress benchmark for local index/query scaling evidence.
- Includes 60 automated tests with mocked HTTP responses, mocked politeness delay, CLI checks, persistence checks, edge cases, branch coverage, and a 90% CI coverage gate.
- Documents algorithm choices, complexity, performance evidence, GenAI reflection, and professional Git workflow.

## Quick Start

```bash
git clone https://github.com/leedsnoob/xjco3011-cw2.git
cd xjco3011-cw2

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

python3 -m src.main load
python3 -m src.main find good friends
python3 -m src.main explain --ranker bm25 good friends
```

`load`, `print`, `find`, `explain`, and `benchmark` use the committed `data/index.json` when it is present. Run `build` when you want to recrawl the live site.

## Installation

Use Python 3.9 or later.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -c "import bs4, requests; print(bs4.__version__, requests.__version__)"
```

No `.env` file is required. The application has no secrets and no external API keys. Environment files are ignored by `.gitignore` so local settings cannot be committed accidentally.

Use `python3 -m pip` from the same interpreter that runs the project. IDEs and terminal shells can point at different Python environments; a package installed in one environment may still be missing in another.

## Usage

### Interactive Shell

```bash
python3 -m src.main
```

Required coursework commands inside the shell:

```text
build
load
print nonsense
find indifference
find good friends
```

Advanced commands inside the shell:

```text
find --ranker tfidf good friends
find --ranker bm25 good friends
find "good friends"
find freinds
explain good friends
explain --ranker bm25 good friends
benchmark
benchmark --bm25-grid
benchmark --stress
help
exit
```

### One-Shot Commands

```bash
python3 -m src.main build
python3 -m src.main load
python3 -m src.main print nonsense
python3 -m src.main find indifference
python3 -m src.main find --ranker tfidf good friends
python3 -m src.main find --ranker bm25 good friends
python3 -m src.main find '"good friends"'
python3 -m src.main explain good friends
python3 -m src.main benchmark --bm25-grid
python3 -m src.main benchmark --stress
```

`build` performs live HTTP requests and intentionally waits between requests to satisfy the politeness requirement. The other commands load the saved index and run locally.
The CLI prints progress bars for crawl, load, search, explanation, benchmark, and stress benchmark phases so long-running work is visible in the terminal.

## Command Reference

| Command | Purpose | Example |
|---|---|---|
| `build` | Crawl the website with progress output and write `data/index.json` | `python3 -m src.main build` |
| `load` | Load the saved index and print a summary | `python3 -m src.main load` |
| `print <word>` | Show indexed pages and frequencies for one word | `python3 -m src.main print nonsense` |
| `find <query>` | Search pages containing all query terms | `python3 -m src.main find good friends` |
| `find --ranker tfidf <query>` | Rank matches with TF-IDF | `python3 -m src.main find --ranker tfidf good friends` |
| `find --ranker bm25 <query>` | Rank matches with BM25 | `python3 -m src.main find --ranker bm25 good friends` |
| `find "<phrase>"` | Search for adjacent token positions | `python3 -m src.main find '"good friends"'` |
| `explain <query>` | Show per-term score contributions | `python3 -m src.main explain good friends` |
| `benchmark` | Time local lookup and ranking paths | `python3 -m src.main benchmark` |
| `benchmark --bm25-grid` | Compare BM25 parameter settings | `python3 -m src.main benchmark --bm25-grid` |
| `benchmark --stress` | Measure synthetic local index/query scaling | `python3 -m src.main benchmark --stress` |

## Architecture

```text
quotes.toscrape.com
        |
        v
src/crawler.py
  - fetch pages with timeout, user agent, pagination handling, and 6-second delay
  - parse quote text, author, tags, and next-page links
        |
        v
src/indexer.py
  - tokenize text
  - normalize terms to lowercase
  - store frequency and token positions per URL
        |
        v
src/search.py
  - save/load JSON index
  - lookup words and intersect posting lists
  - score results with TF-IDF or BM25
  - support phrase search, suggestions, explanations, and benchmarks
        |
        v
src/main.py
  - interactive shell
  - one-shot command dispatcher
  - graceful user-facing errors
```

The design keeps network crawling, indexing, query processing, persistence, and CLI handling in separate modules so each part can be tested directly.

## Index Format

The saved index is JSON so it can be inspected with ordinary text tools. Each term maps to one or more page postings:

```json
{
  "good": {
    "https://quotes.toscrape.com/page/2/": {
      "frequency": 2,
      "positions": [0, 3]
    }
  }
}
```

The metadata section stores page count, document lengths, average document length, build timestamp, source URL, and page summaries. Frequencies support ranking, positions support exact phrase search, and document lengths support BM25 length normalization.

## Ranking and Query Features

TF-IDF is the default advanced ranker. It rewards pages that contain all query terms while giving more weight to rarer terms in the corpus. BM25 is available with the standard default parameters `k1=1.2` and `b=0.75`; it adds term saturation and document-length normalization.

The rankers use established information retrieval formulas because the coursework corpus provides no labelled relevance judgments. A small BM25 parameter comparison records why the selected default is deliberate.

Query behavior:

- Multi-word queries use posting-list intersection, so every returned page contains all query terms.
- Quoted queries such as `"good friends"` require adjacent token positions.
- Misspelled or missing terms trigger suggestions from the indexed vocabulary.
- `explain` reports term frequency, document frequency, inverse document frequency, document length, score, and contribution.
- Malformed queries and invalid rankers return controlled messages and hide tracebacks.

## Performance

Benchmarking measures local search algorithms. Live crawling keeps the required politeness delay, so the implementation keeps live requests sequential.

```bash
python3 -m src.main benchmark --bm25-grid
```

Example benchmark areas:

| Function | Reported metric | Complexity |
|---|---:|---|
| Naive scan baseline | `naive_scan_ms` | `O(total_tokens * query_terms)` |
| Optimized query path | `optimized_query_ms` | `O(sum postings + candidate_pages * query_terms)` |
| Word lookup | `word_lookup_ms` | `O(postings(term))` |
| TF-IDF search | `tfidf_query_ms` | `O(sum postings + candidate_pages * query_terms)` |
| BM25 search | `bm25_query_ms` | `O(sum postings + candidate_pages * query_terms)` |
| Phrase search | `phrase_query_ms` | `O(sum postings + candidate_pages * positions_checked)` |
| Explainable ranking | `explain_ms` | `O(search + result_count * query_terms)` |
| Suggestions | outside default timing | `O(vocabulary_size)` |
| Synthetic stress build | `build_ms` in `benchmark --stress` | `O(total_tokens)` |

Current benchmark evidence and the TF-IDF versus BM25 comparison are recorded in [docs/BENCHMARKS.md](docs/BENCHMARKS.md). The detailed algorithm discussion is in [docs/SEARCH_ALGORITHMS.md](docs/SEARCH_ALGORITHMS.md).

## Testing and CI

Run the full suite:

```bash
python3 -m pytest --cov=src --cov-report=term-missing
python3 -m compileall src tests
```

Current local verification:

```text
60 passed
Total coverage: 100.00%
```

The test suite covers:

- crawler pagination, duplicate-page guards, malformed HTML, HTTP errors, request exceptions, and the 6-second politeness rule with mocks;
- tokenization, case normalization, empty text, frequencies, positions, and save/load behavior;
- single-word search, multi-word search, phrase search, TF-IDF, BM25, suggestions, explanation output, and benchmarks;
- CLI one-shot commands, interactive shell behavior, help output, invalid commands, malformed ranker usage, unmatched quotes, and no-index handling.

GitHub Actions runs the same checks on Python 3.9 and 3.12 with a configured coverage gate. The workflow is defined in [.github/workflows/tests.yml](.github/workflows/tests.yml), and the local pytest configuration is in [pyproject.toml](pyproject.toml).

## Project Structure

```text
.
|-- src/
|   |-- crawler.py       # polite crawler and HTML parser
|   |-- indexer.py       # tokenizer and inverted index builder
|   |-- search.py        # persisted index, lookup, ranking, suggestions
|   |-- stress_benchmark.py
|   `-- main.py          # interactive shell and one-shot CLI commands
|-- tests/
|   |-- fixtures.py
|   |-- test_crawler.py
|   |-- test_indexer.py
|   |-- test_main.py
|   |-- test_search.py
|   `-- test_stress_benchmark.py
|-- data/
|   `-- index.json       # generated compiled index
|-- docs/
|   |-- BENCHMARKS.md
|   |-- DEVELOPMENT_WORKFLOW.md
|   |-- DOCUMENTATION_REVIEW.md
|   |-- ENGINEERING_PRACTICES.md
|   |-- EVIDENCE_MATRIX.md
|   |-- GENAI_EVIDENCE_LOG.md
|   |-- GENAI_REFLECTION.md
|   |-- SEARCH_ALGORITHMS.md
|   |-- TECHNICAL_DESIGN.md
|   |-- TESTING.md
|   |-- VIDEO_SCRIPT.md
|   `-- superpowers/    # planning/specification evidence
|-- .github/workflows/tests.yml
|-- CHANGELOG.md
|-- pyproject.toml
|-- requirements.txt
`-- README.md
```

## Coursework Evidence

This repository is structured so that the main marking evidence is easy to find:

| Evidence area | Where to look |
|---|---|
| Technical design and trade-offs | [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md) |
| Search algorithms, complexity, and optimization | [docs/SEARCH_ALGORITHMS.md](docs/SEARCH_ALGORITHMS.md) |
| Benchmark results and BM25 comparison | [docs/BENCHMARKS.md](docs/BENCHMARKS.md) |
| Documentation review and tone audit | [docs/DOCUMENTATION_REVIEW.md](docs/DOCUMENTATION_REVIEW.md) |
| GenAI evidence log | [docs/GENAI_EVIDENCE_LOG.md](docs/GENAI_EVIDENCE_LOG.md) |
| Testing strategy, mocks, coverage, and CI | [docs/TESTING.md](docs/TESTING.md) |
| Git workflow, semantic commits, branches, and release process | [docs/DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md) |
| Planning and implementation-plan evidence | [docs/superpowers/specs/2026-05-11-search-engine-design.md](docs/superpowers/specs/2026-05-11-search-engine-design.md), [docs/superpowers/plans/2026-05-11-search-engine-implementation.md](docs/superpowers/plans/2026-05-11-search-engine-implementation.md) |
| Engineering practices, type hints, docstrings, and environment policy | [docs/ENGINEERING_PRACTICES.md](docs/ENGINEERING_PRACTICES.md) |
| GenAI use, verification responsibility, ethics, and learning impact | [docs/GENAI_REFLECTION.md](docs/GENAI_REFLECTION.md) |
| Marker-facing evidence checklist | [docs/EVIDENCE_MATRIX.md](docs/EVIDENCE_MATRIX.md) |
| Five-minute demonstration script | [docs/VIDEO_SCRIPT.md](docs/VIDEO_SCRIPT.md) |
| Original coursework brief copy | [docs/cw2.md](docs/cw2.md) |

The latest release is available from [GitHub Releases](https://github.com/leedsnoob/xjco3011-cw2/releases). The compiled `index.json` is included in the repository and attached to release assets.

## Development Workflow

Development uses short-lived feature branches and semantic commit messages:

```text
main
feature/high-score-workflow
feature/test-quality-gates
feature/advanced-ranking
feature/evidence-and-coverage
feature/extreme-case-hardening
feature/algorithm-comparison-evidence
feature/release-quality-hardening
feature/readme-open-source-polish
feature/documentation-tone-review
release/v1.0.0
```

Test-first work is documented across multiple features. The evidence matrix maps test commits to implementation commits and verification commands. To inspect the history:

```bash
git log --oneline --graph --decorate --all --max-count=40
```

## Troubleshooting

| Problem | Resolution |
|---|---|
| `No saved index found` | Run `python3 -m src.main build`, or confirm `data/index.json` exists. |
| `ModuleNotFoundError: No module named 'bs4'` | Run `python3 -m pip install -r requirements.txt` in the same Python environment used to run `python3 -m src.main`. The package name is `beautifulsoup4`, and the import name is `bs4`. |
| `build` appears slow | This is expected because the crawler waits at least 6 seconds between live requests. The target site has multiple pages, so a fresh live build can take close to a minute; progress bars show each fetched page. |
| No results for a query | Try `print <word>` to inspect a single term, or check suggestions from `find <word>`. |
| Invalid ranker error | Use `--ranker tfidf` or `--ranker bm25`. |
| Shell keeps running | Use `exit`, `quit`, or `Ctrl-D`. |

## Limitations

- The crawler targets `quotes.toscrape.com` only.
- The corpus is small, so BM25 parameters are compared with unsupervised ranking evidence.
- The index is stored as a single JSON file for transparency over storage efficiency.
- Query suggestions use vocabulary distance checks, which are acceptable for this small corpus but would need a faster structure for a large index.

## Academic Use

This repository was prepared for XJCO3011 Coursework 2. The documentation includes a GenAI reflection because the coursework requires critical evaluation of AI-assisted development. No license file is currently included; reuse outside assessment should follow the module rules, university academic integrity guidance, and any license the repository owner later adds.
