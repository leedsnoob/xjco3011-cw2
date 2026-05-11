"""Command-line entry point for the coursework search tool."""

from __future__ import annotations

import sys
import time
from collections.abc import Iterable
from pathlib import Path

from src.crawler import CrawlError, QuoteCrawler
from src.indexer import PageDocument, build_search_index
from src.search import (
    DEFAULT_INDEX_PATH,
    IndexStore,
    SearchIndex,
    format_explanations,
    format_results,
)


BM25_PARAMETER_GRID = [(0.9, 0.4), (1.2, 0.75), (1.5, 0.9)]
BENCHMARK_QUERY = "good friends"


class SearchShell:
    """Command dispatcher for interactive and one-shot CLI usage."""

    def __init__(
        self,
        index_path: Path | str = DEFAULT_INDEX_PATH,
        crawler: QuoteCrawler | None = None,
    ) -> None:
        self.index_store = IndexStore(index_path)
        self.crawler = crawler or QuoteCrawler()
        self.index: SearchIndex | None = None

    def execute(self, command_line: str) -> bool:
        """Execute one command. Return False when the shell should exit."""

        stripped = command_line.strip()
        if not stripped:
            return True

        command, _, rest = stripped.partition(" ")
        command = command.lower()
        rest = rest.strip()

        if command in {"exit", "quit"}:
            print("Goodbye.")
            return False
        if command == "help":
            print(help_text())
            return True
        if command == "build":
            self._build()
            return True
        if command == "load":
            self._load()
            return True
        if command == "print":
            self._print(rest)
            return True
        if command == "find":
            self._find(rest)
            return True
        if command == "explain":
            self._explain(rest)
            return True
        if command == "benchmark":
            self._benchmark(include_bm25_grid=rest == "--bm25-grid")
            return True

        print(f"Unknown command: {command}. Type 'help' for available commands.")
        return True

    def run(self) -> None:
        print("XJCO3011 search shell. Type 'help' for commands.")
        while True:
            try:
                if not self.execute(input("> ")):
                    break
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye.")
                break

    def _build(self) -> None:
        try:
            pages = list(self.crawler.crawl())
        except CrawlError as exc:
            print(str(exc))
            return

        documents = [PageDocument.from_crawled_page(page) for page in pages]
        self.index = SearchIndex.from_dict(build_search_index(documents))
        self.index_store.save(self.index)
        print(f"Built index for {len(pages)} page(s) at {self.index_store.path}.")

    def _load(self) -> None:
        try:
            self.index = self.index_store.load()
        except FileNotFoundError as exc:
            print(str(exc))
            return
        print(f"Loaded index from {self.index_store.path}.")

    def _print(self, word: str) -> None:
        if not word:
            print("Usage: print <word>")
            return
        if not self._ensure_index_loaded():
            print("No index loaded. Run 'build' or 'load' first.")
            return
        print(self.index.format_index_entry(word))

    def _find(self, query: str) -> None:
        ranker, query = parse_ranker_option(query)
        if not query:
            print("Usage: find <query terms>")
            return
        if not self._ensure_index_loaded():
            print("No index loaded. Run 'build' or 'load' first.")
            return
        try:
            results = self.index.find(query, ranker=ranker)
        except ValueError as exc:
            print(str(exc))
            return
        print(format_results(results, query, self.index, ranker=ranker))

    def _explain(self, query: str) -> None:
        ranker, query = parse_ranker_option(query)
        if not query:
            print("Usage: explain <query terms>")
            return
        if not self._ensure_index_loaded():
            print("No index loaded. Run 'build' or 'load' first.")
            return
        try:
            explanations = self.index.explain(query, ranker=ranker)
        except ValueError as exc:
            print(str(exc))
            return
        print(format_explanations(explanations, query))

    def _benchmark(self, include_bm25_grid: bool = False) -> None:
        start = time.perf_counter()
        if not self._ensure_index_loaded():
            print("No index loaded. Run 'build' or 'load' first.")
            return
        load_ms = (time.perf_counter() - start) * 1000

        timings: dict[str, float] = {}
        queries = {
            "tfidf_query_ms": (BENCHMARK_QUERY, "tfidf"),
            "bm25_query_ms": (BENCHMARK_QUERY, "bm25"),
            "phrase_query_ms": ('"good friends"', "tfidf"),
        }
        for label, (query, ranker) in queries.items():
            query_start = time.perf_counter()
            self.index.find(query, ranker=ranker)
            timings[label] = (time.perf_counter() - query_start) * 1000

        print("Benchmark results:")
        print(f"- pages={self.index.metadata['page_count']}")
        print(f"- terms={len(self.index.index)}")
        print(f"- load_ms={load_ms:.3f}")
        for label, elapsed in timings.items():
            print(f"- {label}={elapsed:.3f}")

        if include_bm25_grid:
            self._print_bm25_parameter_grid()

    def _print_bm25_parameter_grid(self) -> None:
        terms = BENCHMARK_QUERY.split()
        candidates = self.index.find(BENCHMARK_QUERY, ranker="frequency")

        print("BM25 parameter comparison:")
        for k1, b in BM25_PARAMETER_GRID:
            score_start = time.perf_counter()
            scored = [
                (
                    result.url,
                    self.index.bm25_score_with_parameters(
                        result.url,
                        terms,
                        k1=k1,
                        b=b,
                    ),
                )
                for result in candidates
            ]
            elapsed = (time.perf_counter() - score_start) * 1000
            top_url, top_score = max(scored, key=lambda item: item[1])
            print(
                f"- k1={k1} b={b} top={top_url} "
                f"score={top_score:.4f} time_ms={elapsed:.3f}"
            )

    def _ensure_index_loaded(self) -> bool:
        if self.index:
            return True
        try:
            self.index = self.index_store.load()
        except FileNotFoundError:
            return False
        return True


def help_text() -> str:
    return "\n".join(
        [
            "Commands:",
            "  build              crawl the site, build the index, and save it",
            "  load               load the saved index from disk",
            "  print <word>       print the inverted index entry for a word",
            "  find <query>       find pages containing all query terms",
            "  find --ranker bm25 <query>",
            "  explain <query>    show ranking contribution details",
            "  benchmark          measure local search timings",
            '  find "a phrase"    find pages containing an exact phrase',
            "  help               show this help",
            "  exit               leave the shell",
        ]
    )


def parse_ranker_option(command_text: str) -> tuple[str, str]:
    parts = command_text.split()
    if len(parts) >= 3 and parts[0] == "--ranker":
        return parts[1], " ".join(parts[2:])
    return "tfidf", command_text


def main(argv: Iterable[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    shell = SearchShell()

    if args:
        shell.execute(" ".join(args))
    else:
        shell.run()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
