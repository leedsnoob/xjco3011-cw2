# Changelog

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
