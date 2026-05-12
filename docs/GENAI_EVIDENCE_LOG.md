# GenAI Evidence Log

This log supports the video reflection by linking AI use to human decisions, risks, and verification evidence. It should be read alongside `docs/GENAI_REFLECTION.md`.

## Tool Declaration

Current project record: OpenAI Codex was used as an AI programming assistant for planning, test ideas, implementation review, documentation drafting, and quality review.

Video declaration requirement: state the actual tool path used during the coursework. If university-provided Copilot access is used for any final work, name that tool separately and describe its purpose.

Privacy boundary: prompts and reviews were limited to coursework brief content, local project code, generated test output, and generated benchmark output. No credentials, private personal data, private university records, or deployment secrets were provided.

## Evidence Matrix

| Stage | AI use | Human decision | Risk identified | Verification evidence |
|---|---|---|---|---|
| Planning | Turned the brief into crawler, indexer, search, CLI, testing, and documentation tasks | Kept the scope to a command-line search engine for `quotes.toscrape.com` | Overbuilding a web app or unrelated crawler would weaken coursework alignment | `docs/superpowers/specs/2026-05-11-search-engine-design.md`, `docs/TECHNICAL_DESIGN.md` |
| Index design | Suggested an initial inverted-index structure | Added `frequency`, `positions`, page metadata, and document lengths | A word-to-page list would miss rubric statistics and phrase search evidence | `src/indexer.py`, `tests/test_indexer.py`, `data/index.json` |
| Crawler design | Suggested implementation patterns for fetching and parsing pages | Kept injectable session, sleep, and timeout dependencies | Live crawler tests could become slow or unreliable | `tests/test_crawler.py`, mocked session and sleep tests |
| Politeness | Raised possible crawler performance options | Kept live requests sequential with the 6-second delay | Parallel crawling would conflict with the assignment's politeness requirement | `src/crawler.py`, `docs/BENCHMARKS.md` |
| Ranking | Suggested TF-IDF and BM25 as advanced ranking options | Used TF-IDF as default and BM25 as an optional ranker with standard parameters | Claiming trained relevance without labels would be misleading | `src/search.py`, `docs/SEARCH_ALGORITHMS.md`, `docs/BENCHMARKS.md` |
| Testing | Helped draft initial tests | Added missing edge cases manually: malformed queries, missing index, invalid rankers, empty benchmark grid, EOF handling | Suggested tests did not cover enough failure paths | `tests/test_main.py`, `tests/test_search.py`, 100% coverage report |
| Performance | Helped identify benchmark evidence as a high-band requirement | Added local benchmark and synthetic stress benchmark; kept live crawler outside timing | Measuring live crawling would mainly measure the required wait, not algorithm performance | `python3 -m src.main benchmark --bm25-grid`, `python3 -m src.main benchmark --stress` |
| Documentation | Helped draft README and support docs | Rewrote tone, added source-backed search practice comparison, and recorded documentation review scope | Generic AI-style wording could reduce credibility | `docs/DOCUMENTATION_REVIEW.md`, `README.md`, `docs/SEARCH_ALGORITHMS.md` |
| Debugging | Helped interpret test failures and missing dependency errors | Standardized commands around `python3 -m pytest` | Running plain `pytest` used the wrong Python environment on this machine | `docs/TESTING.md`, `pyproject.toml` |
| Ethics | Helped organize declaration and reflection notes | Kept responsibility with the student and documented privacy boundaries | Misleading declaration or private data exposure would create academic integrity and privacy risks | `docs/GENAI_REFLECTION.md`, video script |

## Video Points

Use two or three concrete examples from the table:

1. AI helped structure the project, but the final module boundaries were checked against the brief.
2. The index design changed from a simple word-to-page map to frequency and positions because the rubric required statistics and phrase search needed token offsets.
3. Performance advice was filtered through the coursework rules: the crawler keeps the 6-second politeness delay, while benchmarking focuses on local index/query algorithms.
4. The test suite shows verification responsibility: AI suggestions became tests, and missing edge cases were added manually.

## Learning Impact

The main learning impact was moving from accepting a suggestion to explaining it. The final submission requires the student to explain the crawler dependency injection, the inverted-index schema, candidate intersection, TF-IDF/BM25 scoring, phrase matching with positions, and the reason benchmark timing excludes live crawling.
