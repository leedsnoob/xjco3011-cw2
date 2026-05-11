# Search Engine Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete Python command-line search engine for `https://quotes.toscrape.com/` with strong tests, documentation, generated index data, and video-ready evidence.

**Architecture:** The project is split into crawler, indexer, search/persistence, and CLI modules. Tests drive behavior with mocked HTTP and sleep dependencies, keeping the suite fast while preserving live-build support for the final index.

**Tech Stack:** Python 3.10+, `requests`, `beautifulsoup4`, `pytest`, `pytest-cov`, standard-library `json`, `dataclasses`, `argparse`, and `difflib`.

---

## File Map

- `src/crawler.py`: HTTP fetching, politeness enforcement, HTML parsing, pagination.
- `src/indexer.py`: tokenization and inverted index construction.
- `src/search.py`: serializable index model, persistence, lookup, ranked query execution.
- `src/main.py`: interactive shell and one-shot command dispatch.
- `tests/fixtures.py`: reusable fake HTML and fake HTTP sessions.
- `tests/test_crawler.py`: crawler behavior.
- `tests/test_indexer.py`: tokenization and index statistics.
- `tests/test_search.py`: persistence, print, find, ranking, suggestions, phrase search.
- `tests/test_main.py`: CLI command dispatch and edge cases.
- `docs/TECHNICAL_DESIGN.md`: architecture and data structure explanation.
- `docs/TESTING.md`: test strategy and coverage guidance.
- `docs/VIDEO_SCRIPT.md`: 5-minute demonstration script.
- `docs/GENAI_REFLECTION.md`: critical GenAI reflection notes.
- `README.md`: installation, usage, testing, and repository overview.

## Task 1: Test Crawler Behavior

**Files:**
- Create: `tests/fixtures.py`
- Modify: `tests/test_crawler.py`

- [ ] Write tests for pagination, page text extraction, politeness sleep, and request failure handling.
- [ ] Run `pytest tests/test_crawler.py -v` and verify tests fail because crawler functions are still pending.
- [ ] Implement crawler behavior in Task 2.
- [ ] Run `pytest tests/test_crawler.py -v` and verify tests pass.
- [ ] Commit with `test: cover crawler behavior`.

## Task 2: Implement Crawler

**Files:**
- Modify: `src/crawler.py`

- [ ] Define `CrawlError`, `CrawledPage`, `PoliteRequester`, and `QuoteCrawler`.
- [ ] Parse quote text, authors, tags, title, and next-page links using BeautifulSoup.
- [ ] Normalize pagination links with `urljoin`.
- [ ] Enforce six-second politeness between successive live requests.
- [ ] Preserve injectable `session`, `sleep`, and clock dependencies for tests.
- [ ] Run crawler tests and commit with `feat: implement polite quote crawler`.

## Task 3: Test Indexing Behavior

**Files:**
- Modify: `tests/test_indexer.py`

- [ ] Write tests for token normalization, punctuation handling, word frequency, positions, and multi-page indexing.
- [ ] Run `pytest tests/test_indexer.py -v` and verify tests fail because indexer functions are still pending.
- [ ] Implement indexing behavior in Task 4.
- [ ] Run `pytest tests/test_indexer.py -v` and verify tests pass.
- [ ] Commit with `test: cover inverted index statistics`.

## Task 4: Implement Indexer

**Files:**
- Modify: `src/indexer.py`

- [ ] Define `WORD_RE`, `PageDocument`, `tokenize`, `build_inverted_index`, and `build_search_index`.
- [ ] Store lowercase terms with `frequency` and `positions` per URL.
- [ ] Store page metadata and document lengths.
- [ ] Run indexer tests and commit with `feat: implement inverted index builder`.

## Task 5: Test Search and Persistence

**Files:**
- Modify: `tests/test_search.py`

- [ ] Write tests for save/load round trip, word printing, single-word search, multi-word intersection, phrase search, empty queries, absent words, and suggestions.
- [ ] Run `pytest tests/test_search.py -v` and verify tests fail because search functions are still pending.
- [ ] Implement search behavior in Task 6.
- [ ] Run `pytest tests/test_search.py -v` and verify tests pass.
- [ ] Commit with `test: cover search and persistence behavior`.

## Task 6: Implement Search and Persistence

**Files:**
- Modify: `src/search.py`

- [ ] Define `SearchIndex`, `SearchResult`, `IndexStore`, `normalise_query`, `format_index_entry`, and search methods.
- [ ] Persist JSON with metadata, pages, and index.
- [ ] Rank by combined term frequency, with optional phrase filtering using positions.
- [ ] Provide close-match suggestions for missing terms.
- [ ] Run search tests and commit with `feat: implement search and persistence`.

## Task 7: Test CLI

**Files:**
- Create: `tests/test_main.py`
- Modify: `tests/test_search.py` if needed for reusable fixtures.

- [ ] Write tests for `build`, `load`, `print`, `find`, empty query, missing index, `help`, and `exit` command handling.
- [ ] Run `pytest tests/test_main.py -v` and verify tests fail because CLI behavior is incomplete.
- [ ] Implement CLI behavior in Task 8.
- [ ] Run `pytest tests/test_main.py -v` and verify tests pass.
- [ ] Commit with `test: cover command line interface`.

## Task 8: Implement CLI

**Files:**
- Modify: `src/main.py`

- [ ] Provide one-shot command mode from `sys.argv`.
- [ ] Provide interactive shell mode when no command is supplied.
- [ ] Keep command output readable for video demonstration.
- [ ] Catch expected user errors and print friendly messages.
- [ ] Run CLI tests and commit with `feat: implement search shell commands`.

## Task 9: Documentation and Coursework Evidence

**Files:**
- Modify: `README.md`
- Add: `docs/TECHNICAL_DESIGN.md`
- Add: `docs/TESTING.md`
- Add: `docs/VIDEO_SCRIPT.md`
- Add: `docs/GENAI_REFLECTION.md`

- [ ] Document installation and dependencies.
- [ ] Document all four required commands with examples.
- [ ] Document architecture, index structure, ranking, phrase search, and politeness.
- [ ] Document test strategy and coverage command.
- [ ] Write a video script covering live demo, code walkthrough, tests, Git, and GenAI reflection.
- [ ] Commit with `docs: add coursework evidence guides`.

## Task 10: Generate Index and Verify

**Files:**
- Add or modify: `data/index.json`

- [ ] Run `python -m src.main build` to create the compiled index file.
- [ ] Run `python -m src.main load`.
- [ ] Run `python -m src.main print nonsense`.
- [ ] Run `python -m src.main find indifference`.
- [ ] Run `python -m src.main find good friends`.
- [ ] Run `pytest --cov=src`.
- [ ] Run `python3 -m compileall src tests`.
- [ ] Commit with `data: add generated search index`.

## Task 11: Final Review and Push

**Files:**
- Modify only if verification finds gaps.

- [ ] Review against the highest-score rubric.
- [ ] Run `git log --oneline --max-count=12` for video evidence.
- [ ] Run `git status -sb` and ensure intended changes are committed.
- [ ] Attempt `git push`; if it hangs, stop waiting and report local commit state.
