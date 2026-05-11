# Video Demonstration Script

Target duration: 5 minutes maximum.

## 0:00-2:00 Live Demonstration

Show the terminal:

```bash
python3 -m src.main build
python3 -m src.main load
python3 -m src.main print nonsense
python3 -m src.main find indifference
python3 -m src.main find --ranker tfidf good friends
python3 -m src.main find --ranker bm25 good friends
python3 -m src.main explain good friends
python3 -m src.main benchmark --bm25-grid
python3 -m src.main find
python3 -m src.main find freinds
```

Say:

- `build` crawls the site, waits at least 6 seconds between live requests, builds the index, and saves `data/index.json`.
- `load` restores the saved index.
- `print` displays the inverted index entry for a term.
- `find` supports single-word and multi-word queries.
- Empty and missing queries produce friendly messages.
- Typo suggestions are an extra feature.
- TF-IDF is the default advanced ranking model; BM25 is available as a modern keyword-ranking option.
- `explain` shows why a result is ranked by exposing term contribution details.
- `benchmark --bm25-grid` reports local search timings and compares three BM25 parameter settings.
- The benchmark also compares TF-IDF and BM25 top results and reports timing for word lookup, TF-IDF search, BM25 search, phrase search, and explain.

## 2:00-3:30 Code Walkthrough

Open:

- `src/crawler.py`: `QuoteCrawler`, `PoliteRequester`, pagination, injected sleep.
- `src/indexer.py`: `tokenize`, `build_inverted_index`, frequency and positions.
- `src/search.py`: JSON persistence, multi-word intersection, TF-IDF/BM25 ranking, phrase search, suggestions, explain output.
- `src/main.py`: shell command dispatch.

Say:

- The index maps each word to URLs and stores frequency plus positions.
- TF-IDF and BM25 are computed from the crawled corpus; no training data is required.
- BM25 uses default `k1=1.2` and `b=0.75` because there are no labelled relevance judgments for tuning.
- The benchmark compares nearby BM25 settings to show ranking stability, but does not pretend to train a model.
- The complexity evidence covers four tested search functions: word lookup, TF-IDF search, BM25 search, and phrase search.
- Positions enable exact phrase search.
- JSON is chosen because it is easy to inspect and submit.

## 3:30-4:00 Testing

Run:

```bash
python3 -m pytest --cov=src --cov-report=term-missing
```

Say:

- Tests mock HTTP and sleep, so crawler behavior is tested without waiting.
- Tests cover crawler, indexer, search, persistence, CLI, edge cases, TF-IDF, BM25, explain, and benchmark behavior.
- The current local suite has 48 tests and 100% coverage.
- The CI workflow runs tests and a coverage gate automatically.

## 4:00-4:30 Version Control

Run:

```bash
git log --oneline --graph --decorate --all --max-count=30
```

Say:

- The history shows planning, tests, implementation, docs, and generated index as separate increments.
- Feature branches show workflow evidence: workflow docs, test quality gates, advanced ranking, and release preparation.
- `docs/EVIDENCE_MATRIX.md` maps rubric points to exact commits, tests, and commands.

## 4:30-5:00 GenAI Critical Evaluation

Summarize:

- AI helped structure the project, design the inverted index, and draft tests.
- A key correction was making the index store frequency and positions rather than only page lists.
- AI suggestions were treated as drafts: ranking, environment, and edge-case behavior were checked with TDD, coverage, and manual CLI runs.
- Ethical reflection: AI use must be declared, and I remain responsible for understanding and verifying all submitted code.
