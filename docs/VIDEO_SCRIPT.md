# Video Demonstration Script

Target duration: 5 minutes maximum.

## 0:00-2:00 Live Demonstration

Show the terminal:

```bash
python3 -m src.main build
python3 -m src.main load
python3 -m src.main print nonsense
python3 -m src.main find indifference
python3 -m src.main find good friends
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

## 2:00-3:30 Code Walkthrough

Open:

- `src/crawler.py`: `QuoteCrawler`, `PoliteRequester`, pagination, injected sleep.
- `src/indexer.py`: `tokenize`, `build_inverted_index`, frequency and positions.
- `src/search.py`: JSON persistence, multi-word intersection, ranking, phrase search, suggestions.
- `src/main.py`: shell command dispatch.

Say:

- The index maps each word to URLs and stores frequency plus positions.
- Frequency ranking is simple and explainable.
- Positions enable exact phrase search.
- JSON is chosen because it is easy to inspect and submit.

## 3:30-4:00 Testing

Run:

```bash
python3 -m pytest --cov=src --cov-report=term-missing
```

Say:

- Tests mock HTTP and sleep, so crawler behavior is tested without waiting.
- Tests cover crawler, indexer, search, persistence, CLI, and edge cases.

## 4:00-4:30 Version Control

Run:

```bash
git log --oneline --max-count=12
```

Say:

- The history shows planning, tests, implementation, docs, and generated index as separate increments.

## 4:30-5:00 GenAI Critical Evaluation

Summarize:

- AI helped structure the project, design the inverted index, and draft tests.
- A key correction was making the index store frequency and positions rather than only page lists.
- Another issue was the Python environment mismatch between `pytest` and `python3 -m pytest`; it was diagnosed and documented.
- AI accelerated boilerplate, but every behavior was verified with tests and manual commands.
