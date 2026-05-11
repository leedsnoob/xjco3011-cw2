# GenAI Reflection

This coursework is Green Category, so GenAI use is allowed with proper declaration and critical evaluation.

## Declaration

I used OpenAI Codex as an AI programming assistant to help plan, implement, test, and document the coursework search engine.

## Where GenAI Helped

- It helped turn the assignment brief into a concrete implementation plan.
- It suggested a modular structure: crawler, indexer, search, and CLI.
- It helped draft test cases before implementation, including crawler politeness, multi-word search, empty queries, and persistence.
- It helped produce documentation for the README, technical design, testing strategy, and video script.

## Where GenAI Needed Correction

- A simpler inverted index design would only map words to pages. The rubric asks for statistics, so the final design stores both `frequency` and `positions`.
- Environment assumptions needed checking. The plain `pytest` command used a different Python environment from `python3`, which caused missing dependency errors. The final documentation uses `python3 -m pytest` to avoid this mismatch.
- AI-generated structure is not enough by itself. Each module had to be verified through tests and manual command runs.

## Code Quality Evaluation

The final code uses small modules with clear responsibilities:

- `crawler.py` handles HTTP, politeness, and parsing.
- `indexer.py` handles tokenization and inverted index construction.
- `search.py` handles persistence and retrieval.
- `main.py` handles the user interface.

The most important AI-assisted design decision was to keep crawler dependencies injectable. This makes the crawler testable without slow live requests.

## Learning Impact

Using AI made the development process faster, especially for scaffolding and test ideas. The main learning value came from checking and improving the suggestions: understanding why positions matter, why multi-word search should use page-set intersection, and why tests should mock network and sleep behavior.

For the video, mention one or two specific examples from this file rather than saying only that AI was useful.
