# GenAI Reflection

This coursework is Green Category, so GenAI use is allowed with proper declaration and critical evaluation.

## Declaration

I used OpenAI Codex as an AI programming assistant to help plan, implement, test, and document the coursework search engine.

## Where GenAI Helped

- It helped turn the assignment brief into a concrete implementation plan.
- It suggested a modular structure: crawler, indexer, search, and CLI.
- It helped draft test cases before implementation, including crawler politeness, multi-word search, empty queries, and persistence.
- It helped produce documentation for the README, technical design, testing strategy, and video script.
- It helped identify higher-scoring evidence that the implementation should expose: branch strategy, semantic commits, coverage gates, explainable ranking, and benchmark results.

## Where GenAI Needed Correction

- A simpler inverted index design would only map words to pages. The rubric asks for statistics, so the final design stores both `frequency` and `positions`.
- Environment assumptions needed checking. The plain `pytest` command used a different Python environment from `python3`, which caused missing dependency errors. The final documentation uses `python3 -m pytest` to avoid this mismatch.
- AI-generated structure is not enough by itself. Each module had to be verified through tests and manual command runs.
- AI can suggest impressive algorithms too quickly. I deliberately avoided concurrent crawling because it would undermine the coursework's politeness requirement. Advanced ranking is limited to local index/query processing instead.

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

## Ethical and Professional Considerations

AI assistance does not transfer responsibility away from the student. I must be able to explain every submitted function, test, and design decision. For this coursework, that means using tests, manual CLI checks, and documentation to verify the code rather than trusting generated output.

There are also privacy and academic integrity considerations:

- AI use must be declared clearly in the video.
- Generated code must not be represented as unaided work.
- Sensitive personal or university data should not be shared with unapproved AI tools.
- AI suggestions should be treated as drafts, not authoritative sources.

The main ethical benefit of the final design is transparency. The planned `explain` command makes ranking decisions visible by showing term-level score contributions, which helps users and markers understand why a result is returned.
