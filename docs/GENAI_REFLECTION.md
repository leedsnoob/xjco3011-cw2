# GenAI Reflection

This coursework is Green Category, so GenAI use is allowed with proper declaration and critical evaluation.

## Declaration

I used OpenAI Codex as an AI programming assistant to help plan, implement, test, review, benchmark, and document the coursework search engine. The video declaration must name the actual tool path used for the submitted work. If any final work is completed through university-provided Copilot access, that tool should be declared separately.

## Where GenAI Helped

- It helped turn the assignment brief into a concrete implementation plan.
- It suggested a modular structure: crawler, indexer, search, and CLI.
- It helped draft test cases before implementation, including crawler politeness, multi-word search, empty queries, and persistence.
- It helped produce documentation for the README, technical design, testing strategy, and video script.
- It helped identify higher-scoring evidence that the implementation should expose: branch strategy, semantic commits, coverage gates, explainable ranking, benchmark results, and synthetic stress evidence.

## Where GenAI Needed Correction

- A simpler inverted index design would only map words to pages. The rubric asks for statistics, so the final design stores both `frequency` and `positions`.
- Environment assumptions needed checking. The plain `pytest` command used a different Python environment from `python3`, which caused missing dependency errors. The final documentation uses `python3 -m pytest` to avoid this mismatch.
- AI-proposed structure required verification through tests and manual command runs.
- AI can suggest impressive algorithms too quickly. I deliberately avoided concurrent crawling because it would undermine the coursework's politeness requirement. Advanced ranking and stress benchmarking are limited to local index/query processing.
- Performance suggestions needed filtering. A live crawler load test would mostly measure the required 6-second delay, so the final stress benchmark uses synthetic local indexes.

## Code Quality Evaluation

The final code uses small modules with clear responsibilities:

- `crawler.py` handles HTTP, politeness, and parsing.
- `indexer.py` handles tokenization and inverted index construction.
- `search.py` handles persistence and retrieval.
- `main.py` handles the user interface.

The most important GenAI-related design decision was to keep crawler dependencies injectable. This makes the crawler testable with fast mocked requests.

Code and suggestion quality was evaluated with:

- failing tests written before new behavior;
- local coverage and branch coverage;
- manual CLI runs for required commands;
- benchmark output for ranking behavior;
- synthetic stress output for scaling behavior;
- documentation review for unclear or template-like phrasing.

## Learning Impact

Using AI made the development process faster, especially for scaffolding and test ideas. The main learning value came from checking and improving the suggestions: understanding why positions matter, why multi-word search should use page-set intersection, why BM25 needs no training claim when relevance labels are unavailable, and why local algorithm timing gives cleaner performance evidence than crawler-delay timing.

For the video, mention one or two specific examples from this file and the evidence table in `docs/GENAI_EVIDENCE_LOG.md`.

## Ethical and Professional Considerations

AI assistance leaves responsibility with the student. I must be able to explain every submitted function, test, and design decision. For this coursework, tests, manual CLI checks, and documentation provide evidence for the submitted code.

There are also privacy and academic integrity considerations:

- AI use must be declared clearly in the video.
- Generated code requires clear declaration.
- Sensitive personal or university data should not be shared with unapproved AI tools.
- AI suggestions should be treated as drafts that require independent verification.
- The coursework brief recommends university-secure Copilot access for privacy and data security. The declaration should match the actual tool used, and no private data or credentials should be placed into prompts.

The main ethical benefit of the final design is transparency. The `explain` command makes ranking decisions visible by showing term-level score contributions, which helps users and markers understand why a result is returned.
