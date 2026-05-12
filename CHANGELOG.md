# Changelog

## v1.0.9 - Review Readiness Polish

### Changed

- Corrected README testing evidence from 48 to 55 automated tests.
- Added the stress benchmark test file to the README project structure.

## v1.0.8 - CLI Progress and Environment Clarity

### Added

- Progress output for build, load, print, find, explain, benchmark, BM25 grid, and synthetic stress benchmark command paths.
- Documentation explaining why live `build` takes noticeable time under the 6-second politeness rule.
- Environment troubleshooting for `beautifulsoup4` versus the `bs4` import name.
- Documentation links explaining the `docs/superpowers/` planning artifacts.

## v1.0.7 - Stress Benchmark and GenAI Evidence

### Added

- `benchmark --stress` command for deterministic synthetic index/query scaling evidence.
- `src/stress_benchmark.py` with local stress benchmark generation, timing, and formatting.
- Tests for synthetic stress benchmark behavior and CLI output.
- `docs/GENAI_EVIDENCE_LOG.md` linking AI use to human decisions, risks, and verification evidence.

### Changed

- Expanded benchmark, search algorithm, testing, engineering, README, video script, and GenAI documentation to cover stress benchmarking and stronger GenAI reflection evidence.

## v1.0.6 - Documentation Tone Review

### Changed

- Reviewed project-authored documentation for English clarity, direct wording, and reduced template-like AI phrasing.
- Added a modern search practice section comparing search-engine algorithms with Safari and Chrome browser search fields.
- Added `docs/DOCUMENTATION_REVIEW.md` to record the documentation audit scope and verification commands.
- Updated README and evidence documentation to reflect the documentation tone review branch.

## v1.0.5 - README Documentation Polish

### Changed

- Reworked `README.md` into an open-source-style project entrypoint with badges, quick start, command reference, architecture, index format, ranking notes, performance summary, testing/CI evidence, troubleshooting, limitations, and coursework evidence links.
- Clarified academic-use and environment-file expectations with no unnecessary project configuration.

## v1.0.4 - Release Quality Hardening

### Added

- Engineering practices documentation covering environment files, structure, type hints, docstrings, CI, and releases.
- `.env` and `.env.*` ignore rules while allowing a future `.env.example`.
- Docstrings for remaining source classes and helpers.
- Small explanatory comments for non-obvious search and benchmark decisions.

### Changed

- Cleaned up a redundant import and split long expressions for readability.

## v1.0.0 - Coursework Submission

Planned final release for COMP/XJCO3011 Coursework 2.

### Added

- Polite crawler for `https://quotes.toscrape.com/`.
- Case-insensitive inverted index with frequency and positions.
- JSON index persistence in `data/index.json`.
- CLI commands: `build`, `load`, `print`, and `find`.
- Multi-word search, phrase search, and typo suggestions.
- Professional workflow documentation, testing evidence, and GenAI reflection.

### Advanced Evidence

- Automated CI workflow and coverage gate.
- TF-IDF ranking as the default advanced ranking model.
- BM25 ranking with standard default parameters.
- Explainable ranking output with term-level contributions.
- Local benchmark command and benchmark documentation.
