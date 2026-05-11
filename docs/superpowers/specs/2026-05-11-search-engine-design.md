# Search Engine Tool Design

## Goal

Build a Python command-line search engine for `https://quotes.toscrape.com/` that satisfies the COMP/XJCO3011 Coursework 2 requirements and provides enough implementation, testing, documentation, and reflection evidence for the highest marking band.

## Scope

The tool will crawl the quote website, build a case-insensitive inverted index with word statistics, persist the index to `data/index.json`, reload it, and answer `print` and `find` commands from an interactive shell or one-shot command invocation.

Out of scope: a web UI, distributed crawling, crawling external domains, and using a database server. These would add complexity while adding little coursework evidence.

## Architecture

The implementation is split into small modules with stable interfaces:

- `src/crawler.py`: fetches pages, enforces politeness, follows pagination, extracts visible quote-page text.
- `src/indexer.py`: tokenizes text and builds the inverted index.
- `src/search.py`: owns index persistence, index lookup, multi-term search, ranking, and query suggestions.
- `src/main.py`: provides the command-line shell and output formatting.

The modules communicate with plain Python data structures and dataclasses. This keeps the code easy to explain in the video and easy to test with deterministic fixtures.

## Data Model

The persisted JSON file will use this shape:

```json
{
  "metadata": {
    "base_url": "https://quotes.toscrape.com/",
    "built_at": "2026-05-11T00:00:00+00:00",
    "page_count": 10,
    "document_lengths": {
      "https://quotes.toscrape.com/": 120
    }
  },
  "pages": {
    "https://quotes.toscrape.com/": {
      "title": "Quotes to Scrape",
      "word_count": 120
    }
  },
  "index": {
    "good": {
      "https://quotes.toscrape.com/": {
        "frequency": 2,
        "positions": [10, 44]
      }
    }
  }
}
```

This design directly supports the rubric requirement for word statistics and enables ranked search. `frequency` gives a simple score, while `positions` allow exact phrase search as an advanced feature.

## Crawling Behavior

The crawler starts at the base URL, fetches the current page, extracts quote text, author names, tags, and page title, then follows the `li.next > a` pagination link. It normalizes links with `urljoin`, ignores already-visited pages, and stops when no next link exists.

For live requests, it enforces at least six seconds between successive requests. Tests will inject a fake sleep function and fake HTTP session so politeness can be verified quickly.

Network errors become clear `CrawlError` exceptions that the CLI can display in normal use.

## Indexing Behavior

Tokenization will be case-insensitive and based on words containing letters, digits, and apostrophes. Each token is stored under its lowercase form. For each page, the index stores both frequency and token positions. Positions are page-local token offsets.

The indexer will keep document lengths so the search layer can rank results by term frequency and optionally normalize by document size.

## Search Behavior

`print <word>` prints the index entry for one normalized word, including URLs, frequencies, and positions.

`find <terms>` supports:

- single-word search;
- multi-word search using intersection of pages containing every term;
- ranked results using combined term frequency;
- optional exact phrase search when the query is wrapped in double quotes;
- graceful messages for empty queries and missing words;
- suggestions for missing terms using close word matching.

## CLI Contract

The command-line interface supports both interactive and one-shot use:

```bash
python -m src.main
python -m src.main build
python -m src.main load
python -m src.main print nonsense
python -m src.main find good friends
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

`build` crawls the website, builds the index, saves it, and keeps it loaded in memory. `load` loads `data/index.json`. `print` and `find` require a loaded index and display a helpful message if no index is available.

## Testing Strategy

Tests will avoid repeated live website calls. Unit tests use HTML fixtures and fake sessions to cover:

- pagination parsing;
- politeness sleep behavior;
- network failure handling;
- token normalization;
- frequency and position recording;
- save/load round trips;
- single-word, multi-word, phrase, empty, and absent query search;
- CLI command dispatch and user-facing messages.

The target is above 85% coverage. A live build can still be run manually for the video and final index file.

## Documentation Strategy

The repository will include:

- `README.md`: setup, usage, architecture, commands, testing, and design rationale.
- `docs/TECHNICAL_DESIGN.md`: implementation details and data structure explanation.
- `docs/TESTING.md`: test strategy, coverage command, and edge cases.
- `docs/VIDEO_SCRIPT.md`: 5-minute recording outline.
- `docs/GENAI_REFLECTION.md`: honest declaration and critical evaluation points.

## Commit Strategy

Use multiple meaningful commits:

1. design/spec documentation;
2. implementation plan;
3. tests;
4. crawler/indexer implementation;
5. search/CLI implementation;
6. documentation and generated index;
7. verification fixes if needed.

This creates visible incremental development evidence for the video.
