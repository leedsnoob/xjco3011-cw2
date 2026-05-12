# Testing Strategy

## Commands

Run all tests:

```bash
python3 -m pytest -q
```

Run tests with coverage:

```bash
python3 -m pytest --cov=src --cov-report=term-missing
```

Run syntax compilation:

```bash
python3 -m compileall src tests
```

Use `python3 -m pytest` if multiple Python environments are installed.

The project uses `pyproject.toml` to configure pytest and coverage. The coverage gate is set to 90%, while the current suite is expected to remain above that threshold.

Current local result:

```text
48 passed
Total coverage: 100.00%
```

## Coverage Areas

The test suite covers:

- crawler pagination;
- text extraction from quote pages;
- 6-second politeness delay using a fake sleep function;
- HTTP failure wrapping;
- malformed quote HTML missing text and author fields;
- token lowercasing and punctuation handling;
- frequency and position statistics;
- multi-page inverted indexing;
- JSON save/load round trip;
- `print` output formatting;
- single-word search;
- multi-word query intersection;
- exact phrase search;
- empty query handling;
- missing word handling;
- typo suggestions;
- CLI `load`, `print`, `find`, `help`, unknown command, and `exit`.
- CLI `explain`, `benchmark`, invalid ranker, missing index, EOF, and interactive loop handling.
- synthetic stress benchmark generation, formatting, validation, and CLI output.

## Mocking Strategy

The crawler is tested with a `FakeSession` in place of the live website. This makes request order, HTTP failures, and pagination loops deterministic. The sleep dependency is also injected, so tests can assert that the second request waits 6 seconds while the suite stays fast.

The search tests use a small deterministic in-memory index. This avoids coupling ranking and edge-case tests to the live website content.

The CLI tests use temporary index files and subprocess checks. This verifies both direct command dispatch and user-facing command-line behavior.

## Why Mock the Crawler

The coursework requires a live crawler. Automated tests also need fast and reliable execution. The crawler accepts injectable `session` and `sleep` dependencies, so tests can prove that:

- the second request waits 6 seconds;
- pagination is followed;
- network failures become `CrawlError`;
- parsing extracts the expected text.

This keeps repeated test runs off the live website.

## Automated Test Pipeline

The GitHub Actions workflow in `.github/workflows/tests.yml` runs on `main`, feature branches, release branches, and pull requests. It checks:

- dependency installation from `requirements.txt`;
- `python -m pytest --cov=src --cov-report=term-missing`;
- the 90% coverage gate from `pyproject.toml`;
- `python -m compileall src tests`.

The workflow runs on Python 3.9 and 3.12 to show that the code works across the expected supported range.

## Coverage Rationale

The coverage gate remains 90% because CI gates should prevent regressions while discouraging artificial tests. The current suite reaches 100% locally because the remaining uncovered branches were real edge cases:

- malformed quote blocks missing `.text` and `.author`;
- interactive shell EOF;
- interactive shell command loop before exit;
- missing index handling for `print`, `explain`, and `benchmark`;
- invalid ranker handling for both `find` and `explain`;
- no-result formatting for `explain`.
- malformed `--ranker` usage with no query;
- unmatched quote handling for phrase queries;
- empty-index benchmark grid handling.
- synthetic stress benchmark scaling and input validation.

The `if __name__ == "__main__"` entry-point guard is excluded from coverage because it only delegates to the tested `main()` function.

## Manual Verification for Video

After generating `data/index.json`, demonstrate:

```bash
python3 -m src.main build
python3 -m src.main load
python3 -m src.main print nonsense
python3 -m src.main find indifference
python3 -m src.main find good friends
python3 -m src.main find
python3 -m src.main find freinds
python3 -m src.main benchmark --stress
```

Also show:

```bash
python3 -m pytest --cov=src --cov-report=term-missing
git log --oneline --max-count=12
```
