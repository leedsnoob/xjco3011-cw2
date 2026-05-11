# Technical Design

## Overview

This project implements a small search engine for `https://quotes.toscrape.com/`. It has four main modules:

- `src/crawler.py`: fetches HTML pages politely and extracts searchable text.
- `src/indexer.py`: tokenizes text and builds the inverted index.
- `src/search.py`: saves, loads, prints, and searches the index.
- `src/main.py`: exposes the command-line shell.

The design is intentionally modular so each coursework concept can be demonstrated separately in the video.

## Crawler

`QuoteCrawler` starts at the base URL and follows the `li.next a` pagination link until no next page remains. It uses `urljoin` so relative links such as `/page/2/` become absolute URLs.

`PoliteRequester` wraps HTTP access and enforces a 6-second delay before every request after the first one. The delay, HTTP session, and timeout are injectable, which makes the behavior testable without slow live requests.

The crawler extracts:

- page title;
- quote text;
- author names;
- tags;
- next-page URL.

Network and HTTP failures are wrapped in `CrawlError` so the CLI can show a friendly error instead of a raw traceback.

## Indexer

The tokenizer uses this regular expression:

```python
[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?
```

It lowercases all words, so `Good`, `GOOD`, and `good` are treated as the same term. Simple apostrophes are preserved, so `don't` remains one token.

The core index structure is:

```python
dict[str, dict[str, {"frequency": int, "positions": list[int]}]]
```

Example:

```json
{
  "good": {
    "https://quotes.toscrape.com/page/2/": {
      "frequency": 2,
      "positions": [0, 3]
    }
  }
}
```

This stores both required statistics and advanced search data. Frequency supports ranking, while positions support phrase search.

## Persistence

The compiled index is saved to `data/index.json` with three top-level sections:

- `metadata`: base URL, build timestamp, page count, and document lengths.
- `pages`: page titles and word counts.
- `index`: inverted index entries.

JSON was chosen because it is inspectable during marking and easy to explain in the video.

## Search

`find` normalizes query terms with the same tokenizer used during indexing. Multi-word search intersects the page sets for all terms, so `find good friends` returns only pages containing both `good` and `friends`.

Results are ranked by combined term frequency. This is simple, deterministic, and directly explainable:

```text
score = frequency(term1 in page) + frequency(term2 in page) + ...
```

If a query is wrapped in double quotes in the interactive shell, exact phrase search checks adjacent token positions.

When a term is missing, the search layer uses `difflib.get_close_matches` to offer suggestions such as `freinds -> friends`.

## CLI

The CLI supports interactive and one-shot use:

```bash
python3 -m src.main
python3 -m src.main build
python3 -m src.main print nonsense
python3 -m src.main find good friends
```

Interactive commands:

```text
build
load
print <word>
find <query terms>
help
exit
```

`build` leaves the new index loaded in memory and saves it to disk. `print` and `find` automatically load the saved index if needed, which makes one-shot command demonstrations easier.

## Trade-offs

- JSON persistence is not as fast as a database for large corpora, but this website is small and JSON is transparent for assessment.
- Frequency ranking is simpler than full TF-IDF. It is enough to demonstrate ranked retrieval while keeping the code explainable.
- Exact phrase search is only activated for quoted interactive queries. Regular multi-word queries use page intersection, matching the coursework examples.
- Tests mock network and sleep behavior. Live crawling is still supported for generating the submitted index file.
