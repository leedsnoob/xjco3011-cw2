# XJCO3011 Coursework 2: Search Engine Tool

Python command-line search engine for `https://quotes.toscrape.com/`.

The tool crawls the quote website, observes a 6-second politeness window between live requests, builds a case-insensitive inverted index with frequency and position statistics, saves the compiled index to disk, and supports searching from a command-line shell.

## Features

- Crawls paginated quote pages from `https://quotes.toscrape.com/`.
- Uses `requests` for HTTP and `BeautifulSoup` for HTML parsing.
- Enforces a minimum 6-second delay between successive live requests.
- Builds an inverted index with:
  - lowercase terms;
  - per-page frequency;
  - per-page token positions;
  - page metadata and document lengths.
- Saves and loads the compiled index as JSON.
- Supports required commands: `build`, `load`, `print`, and `find`.
- Supports multi-word queries, TF-IDF/BM25 ranked results, exact phrase search, typo suggestions, explainable ranking, and benchmark output.
- Includes tests for crawler, indexer, search, persistence, and CLI behavior.

## Project Structure

```text
src/
  crawler.py       # polite crawler and HTML parser
  indexer.py       # tokenizer and inverted index builder
  search.py        # persisted index, lookup, ranking, suggestions
  main.py          # interactive shell and one-shot CLI commands
tests/
  fixtures.py
  test_crawler.py
  test_indexer.py
  test_search.py
  test_main.py
data/
  index.json       # generated compiled index after build
docs/
  TECHNICAL_DESIGN.md
  TESTING.md
  VIDEO_SCRIPT.md
  GENAI_REFLECTION.md
requirements.txt
```

## Setup

Use Python 3.9 or later.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

If you do not use a virtual environment, run commands with `python3 -m ...` so tests use the same Python environment that has the dependencies installed.

## Usage

Start the interactive shell:

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

Additional examples:

```text
find --ranker tfidf good friends
find --ranker bm25 good friends
find "good friends"
explain good friends
explain --ranker bm25 good friends
benchmark
benchmark --bm25-grid
find freinds
help
exit
```

One-shot command mode is also supported:

```bash
python3 -m src.main build
python3 -m src.main load
python3 -m src.main print nonsense
python3 -m src.main find --ranker tfidf good friends
python3 -m src.main find --ranker bm25 good friends
python3 -m src.main explain good friends
python3 -m src.main benchmark
python3 -m src.main benchmark --bm25-grid
```

`print` and `find` automatically load `data/index.json` if it already exists.

## Testing

Run the full test suite:

```bash
python3 -m pytest -q
```

Run with coverage:

```bash
python3 -m pytest --cov=src --cov-report=term-missing
```

The tests use fake HTTP sessions and fake sleep functions for crawler behavior, so they verify the politeness window without making the test suite wait 6 seconds per request.

Current local verification is 48 tests with 100% coverage:

```bash
python3 -m pytest --cov=src --cov-report=term-missing
```

## Design Summary

The inverted index uses this structure:

```python
{
    "good": {
        "https://quotes.toscrape.com/page/2/": {
            "frequency": 2,
            "positions": [0, 3],
        }
    }
}
```

This directly supports the coursework requirement to store word statistics. Frequencies are used by TF-IDF and BM25 ranking; positions support exact phrase search. The benchmark command reports per-function timing for word lookup, TF-IDF search, BM25 search, phrase search, and explainable ranking, and compares the TF-IDF and BM25 top-ranked result.

See [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md) for the detailed architecture and trade-offs.

## Coursework Evidence

- Technical design: [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md)
- Testing strategy: [docs/TESTING.md](docs/TESTING.md)
- Video script: [docs/VIDEO_SCRIPT.md](docs/VIDEO_SCRIPT.md)
- GenAI reflection notes: [docs/GENAI_REFLECTION.md](docs/GENAI_REFLECTION.md)
- Search algorithms and complexity: [docs/SEARCH_ALGORITHMS.md](docs/SEARCH_ALGORITHMS.md)
- Benchmarks: [docs/BENCHMARKS.md](docs/BENCHMARKS.md)
- Development workflow: [docs/DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md)
- Evidence matrix: [docs/EVIDENCE_MATRIX.md](docs/EVIDENCE_MATRIX.md)
- Assignment brief: [docs/cw2.md](docs/cw2.md)
