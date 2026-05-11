# XJCO3011 Coursework 2: Search Engine Tool

Python command-line search engine for `https://quotes.toscrape.com/`.

## Project Structure

```text
src/
  crawler.py
  indexer.py
  search.py
  main.py
tests/
  test_crawler.py
  test_indexer.py
  test_search.py
data/
  .gitkeep
docs/
  cw2.md
  XJCO3011_Coursework2_Brief__2025_2026.pdf
requirements.txt
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Planned Usage

```bash
python -m src.main
```

Required commands:

```text
build
load
print nonsense
find indifference
find good friends
```

## Testing

```bash
pytest
pytest --cov=src
```

## Notes

The implementation should respect a politeness window of at least 6 seconds between live requests, build a case-insensitive inverted index, and store word statistics such as frequency and positions.
