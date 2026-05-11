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

Use `python3 -m pytest` rather than plain `pytest` if multiple Python environments are installed.

## Coverage Areas

The test suite covers:

- crawler pagination;
- text extraction from quote pages;
- 6-second politeness delay using a fake sleep function;
- HTTP failure wrapping;
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

## Why Mock the Crawler

The coursework requires a live crawler, but automated tests should be fast and reliable. The crawler accepts injectable `session` and `sleep` dependencies, so tests can prove that:

- the second request waits 6 seconds;
- pagination is followed;
- network failures become `CrawlError`;
- parsing extracts the expected text.

This avoids repeatedly hitting the live website during every test run.

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
```

Also show:

```bash
python3 -m pytest --cov=src --cov-report=term-missing
git log --oneline --max-count=12
```
