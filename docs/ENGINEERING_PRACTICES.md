# Engineering Practices

This document records the engineering-quality decisions used to keep the coursework close to release quality.

## Environment and Secrets

The project has no `.env` file requirement because it uses no secrets, API keys, database credentials, or deployment-specific settings. Adding a real `.env` would create unnecessary configuration surface.

Install dependencies from `requirements.txt` in the same Python environment that runs the CLI:

```bash
python3 -m pip install -r requirements.txt
python3 -c "import bs4, requests; print(bs4.__version__, requests.__version__)"
```

`beautifulsoup4` is the package name and `bs4` is the import name. A terminal, IDE, and agent process can each use a different interpreter, so successful tests in one environment do not prove that another local environment has the same packages installed.

The `.gitignore` explicitly ignores:

- `.env` and `.env.*`;
- virtual environments such as `.venv/`, `venv/`, and `env/`;
- Python caches;
- pytest and coverage outputs;
- local OS files such as `.DS_Store`.

If future environment variables become necessary, the safe practice is to commit `.env.example` with placeholder names only, while keeping real `.env` files untracked.

## Project Structure

The production code is separated into focused modules:

| Module | Responsibility |
|---|---|
| `src/crawler.py` | Polite requests, pagination, HTML parsing |
| `src/indexer.py` | Tokenization, inverted index construction, serializable index schema |
| `src/search.py` | Index loading, querying, ranking, suggestions, explanation formatting |
| `src/stress_benchmark.py` | Synthetic stress benchmark generation and timing |
| `src/main.py` | CLI command dispatch, user-facing messages, progress output, benchmark output |

Tests mirror this structure under `tests/`, with deterministic fixtures and temporary files in place of live network dependencies.

## Type Hints and Docstrings

The code uses type hints throughout the public API and core helpers. Structured index payloads are represented with `TypedDict` classes, and command/search results use dataclasses where appropriate.

Docstrings are used for:

- modules;
- public classes;
- public functions;
- important private CLI helpers where the behavior is part of the user-facing command flow.

Short inline comments are reserved for non-obvious implementation decisions, such as intersecting postings before scoring and excluding live crawl delay from benchmark timing.

## Quality Gates

Local verification commands:

```bash
python3 -m pytest --cov=src --cov-report=term-missing
python3 -m compileall src tests
python3 -m src.main benchmark --bm25-grid
python3 -m src.main benchmark --stress
```

The CI workflow runs the test suite and compile check on Python 3.9 and 3.12. Coverage is configured in `pyproject.toml` with branch coverage enabled and a `fail_under = 90` gate. The current local suite reaches 100% coverage.

## Release Practice

The repository uses feature branches, merge commits, semantic commit messages, release tags, and GitHub Releases. The latest release attaches the compiled `index.json` so the index evidence is available from release assets.

The release workflow is intentionally lightweight for coursework scale and still demonstrates professional habits:

- isolated feature branches;
- incremental test-first commits;
- CI before release;
- tagged versions;
- release notes and assets.
