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
    InvalidIndexError,
    SearchResult,
    SearchIndex,
    format_explanations,
    format_results,
)
from src.stress_benchmark import format_stress_benchmark, run_stress_benchmark


BM25_PARAMETER_GRID = [(0.9, 0.4), (1.2, 0.75), (1.5, 0.9)]
BENCHMARK_QUERY = "good friends"
PROGRESS_BAR_WIDTH = 10
CRAWL_PROGRESS_TARGET_PAGES = 10


def format_progress_bar(step: int, total: int) -> str:
    """Return a fixed-width ASCII progress bar."""

    if total <= 0:
        total = 1
    bounded_step = max(0, min(step, total))
    filled = int(PROGRESS_BAR_WIDTH * bounded_step / total)
    if bounded_step and filled == 0:
        filled = 1
    return f"[{'#' * filled}{'.' * (PROGRESS_BAR_WIDTH - filled)}]"


def format_progress_line(label: str, step: int, total: int, detail: str = "") -> str:
    """Return a user-facing progress line."""

    suffix = f": {detail}" if detail else ""
    return f"Progress {format_progress_bar(step, total)} {step}/{total} {label}{suffix}"


def format_crawl_progress_line(page_count: int, url: str) -> str:
    """Return progress for a crawl whose final page count is discovered as it runs."""

    return (
        f"Crawl progress {format_progress_bar(page_count, CRAWL_PROGRESS_TARGET_PAGES)} "
        f"{page_count} page(s): {url}"
    )


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
            self._benchmark_command(rest)
            return True

        print(f"Unknown command: {command}. Type 'help' for available commands.")
        return True

    def run(self) -> None:
        """Run the interactive command loop until the user exits."""

        print("XJCO3011 search shell. Type 'help' for commands.")
        while True:
            try:
                if not self.execute(input("> ")):
                    break
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye.")
                break

    def _build(self) -> None:
        """Crawl the site, build the index, and persist it."""

        print(
            "Starting crawl. Live requests wait at least 6 seconds after the first page.",
            flush=True,
        )
        print(format_progress_line("Start crawl", 1, 3), flush=True)
        pages = []
        try:
            for page_count, page in enumerate(self.crawler.crawl(), start=1):
                pages.append(page)
                print(format_crawl_progress_line(page_count, page.url), flush=True)
        except CrawlError as exc:
            print(str(exc))
            return

        print(f"Building index from {len(pages)} page(s).", flush=True)
        print(format_progress_line("Build index", 2, 3), flush=True)
        documents = [PageDocument.from_crawled_page(page) for page in pages]
        self.index = SearchIndex.from_dict(build_search_index(documents))
        print(format_progress_line("Save index", 3, 3), flush=True)
        self.index_store.save(self.index)
        print(f"Built index for {len(pages)} page(s) at {self.index_store.path}.")

    def _load(self) -> None:
        """Load the compiled index into the current shell session."""

        print(
            format_progress_line("Load index", 1, 1, str(self.index_store.path)),
            flush=True,
        )
        try:
            self.index = self.index_store.load()
        except (FileNotFoundError, InvalidIndexError) as exc:
            print(str(exc))
            return
        print(f"Loaded index from {self.index_store.path}.")

    def _print(self, word: str) -> None:
        """Print one inverted-index entry."""

        if not word:
            print("Usage: print <word>")
            return
        if not self._ensure_index_loaded():
            print("No index loaded. Run 'build' or 'load' first.")
            return
        print(format_progress_line("Print index entry", 1, 1, word), flush=True)
        print(self.index.format_index_entry(word))

    def _find(self, query: str) -> None:
        """Run a ranked search and print formatted results."""

        try:
            ranker, query = parse_ranker_option(query)
        except ValueError as exc:
            print(str(exc))
            return
        if not query:
            print("Usage: find <query terms>")
            return
        print(format_progress_line("Load search index", 1, 2), flush=True)
        if not self._ensure_index_loaded():
            print("No index loaded. Run 'build' or 'load' first.")
            return
        try:
            print(format_progress_line("Search query", 2, 2, query), flush=True)
            results = self.index.find(query, ranker=ranker)
        except ValueError as exc:
            print(str(exc))
            return
        print(format_results(results, query, self.index, ranker=ranker))

    def _explain(self, query: str) -> None:
        """Print ranking contribution details for matching pages."""

        try:
            ranker, query = parse_ranker_option(query)
        except ValueError as exc:
            print(str(exc))
            return
        if not query:
            print("Usage: explain <query terms>")
            return
        print(format_progress_line("Load explanation index", 1, 2), flush=True)
        if not self._ensure_index_loaded():
            print("No index loaded. Run 'build' or 'load' first.")
            return
        try:
            print(format_progress_line("Explain ranking", 2, 2, query), flush=True)
            explanations = self.index.explain(query, ranker=ranker)
        except ValueError as exc:
            print(str(exc))
            return
        print(format_explanations(explanations, query))

    def _benchmark_command(self, option: str) -> None:
        """Dispatch benchmark variants."""

        if option == "--stress":
            def report_progress(step: int, total: int, page_count: int) -> None:
                print(
                    format_progress_line(
                        "Synthetic stress",
                        step,
                        total,
                        f"{page_count} pages",
                    ),
                    flush=True,
                )

            print(
                format_stress_benchmark(
                    run_stress_benchmark(progress=report_progress)
                )
            )
            return
        if option and option != "--bm25-grid":
            print("Usage: benchmark [--bm25-grid|--stress]")
            return
        self._benchmark(include_bm25_grid=option == "--bm25-grid")

    def _benchmark(self, include_bm25_grid: bool = False) -> None:
        """Print local timing evidence for lookup, search, explain, and rankers."""

        print(format_progress_line("Load benchmark index", 1, 5), flush=True)
        start = time.perf_counter()
        if not self._ensure_index_loaded():
            print("No index loaded. Run 'build' or 'load' first.")
            return
        load_ms = (time.perf_counter() - start) * 1000

        timings: dict[str, float] = {}
        result_sets: dict[str, list[SearchResult]] = {}

        # Measure local algorithm work only; live crawling delay is a requirement.
        print(format_progress_line("Word lookup", 2, 5), flush=True)
        lookup_start = time.perf_counter()
        self.index.format_index_entry("good")
        timings["word_lookup_ms"] = (time.perf_counter() - lookup_start) * 1000

        print(format_progress_line("Run ranking queries", 3, 5), flush=True)
        naive_start = time.perf_counter()
        self.index.naive_scan_find(BENCHMARK_QUERY)
        timings["naive_scan_ms"] = (time.perf_counter() - naive_start) * 1000

        optimized_start = time.perf_counter()
        optimized_results = self.index.find(BENCHMARK_QUERY, ranker="tfidf")
        timings["optimized_query_ms"] = (time.perf_counter() - optimized_start) * 1000
        timings["tfidf_query_ms"] = timings["optimized_query_ms"]
        result_sets["tfidf"] = optimized_results

        queries = {
            "bm25_query_ms": (BENCHMARK_QUERY, "bm25"),
            "phrase_query_ms": ('"good friends"', "tfidf"),
        }
        for label, (query, ranker) in queries.items():
            query_start = time.perf_counter()
            results = self.index.find(query, ranker=ranker)
            timings[label] = (time.perf_counter() - query_start) * 1000
            if query == BENCHMARK_QUERY:
                result_sets[ranker] = results

        print(format_progress_line("Explain ranking", 4, 5), flush=True)
        explain_start = time.perf_counter()
        self.index.explain(BENCHMARK_QUERY, ranker="bm25")
        timings["explain_ms"] = (time.perf_counter() - explain_start) * 1000

        print(format_progress_line("Print ranking comparison", 5, 5), flush=True)
        print("Benchmark results:")
        print(f"- pages={self.index.metadata['page_count']}")
        print(f"- terms={len(self.index.index)}")
        print(f"- load_ms={load_ms:.3f}")
        for label, elapsed in timings.items():
            print(f"- {label}={elapsed:.3f}")
        speedup = (
            timings["naive_scan_ms"] / timings["optimized_query_ms"]
            if timings["optimized_query_ms"]
            else 0.0
        )
        print(f"- optimized_vs_naive_speedup={speedup:.2f}x")
        self._print_ranking_comparison(result_sets)

        if include_bm25_grid:
            self._print_bm25_parameter_grid()

    def _print_ranking_comparison(
        self,
        result_sets: dict[str, list[SearchResult]],
    ) -> None:
        """Print top-result evidence for TF-IDF and BM25."""

        print("Ranking comparison:")
        for ranker in ("tfidf", "bm25"):
            results = result_sets.get(ranker, [])
            if not results:
                print(f"- {ranker}_top=none")
                continue
            top = results[0]
            print(f"- {ranker}_top={top.url} score={top.score:.4f}")

    def _print_bm25_parameter_grid(self) -> None:
        """Print a small BM25 parameter comparison grid."""

        terms = BENCHMARK_QUERY.split()
        candidates = self.index.find(BENCHMARK_QUERY, ranker="frequency")

        print("BM25 parameter comparison:")
        if not candidates:
            print(f"- No benchmark candidates for '{BENCHMARK_QUERY}'.")
            return

        for step, (k1, b) in enumerate(BM25_PARAMETER_GRID, start=1):
            print(
                format_progress_line(
                    "BM25 grid",
                    step,
                    len(BM25_PARAMETER_GRID),
                    f"k1={k1} b={b}",
                ),
                flush=True,
            )
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
        """Load the index on demand if it is not already in memory."""

        if self.index:
            return True
        try:
            self.index = self.index_store.load()
        except FileNotFoundError:
            return False
        except InvalidIndexError as exc:
            print(str(exc))
            return False
        return True


def help_text() -> str:
    """Return help text for the interactive shell."""

    return "\n".join(
        [
            "Commands:",
            "  build              crawl with progress, build the index, and save it",
            "  load               load the saved index from disk",
            "  print <word>       print the inverted index entry for a word",
            "  find <query>       find pages containing all query terms",
            "  find --ranker bm25 <query>",
            "  explain <query>    show ranking contribution details",
            "  benchmark          measure local search timings",
            "  benchmark --stress measure synthetic scaling evidence",
            '  find "a phrase"    find pages containing an exact phrase',
            "  help               show this help",
            "  exit               leave the shell",
        ]
    )


def parse_ranker_option(command_text: str) -> tuple[str, str]:
    """Parse an optional --ranker argument from a command body."""

    parts = command_text.split()
    if parts and parts[0] == "--ranker":
        if len(parts) < 3:
            raise ValueError("Usage: --ranker <frequency|tfidf|bm25> <query terms>")
        return parts[1], " ".join(parts[2:])
    return "tfidf", command_text


def main(argv: Iterable[str] | None = None) -> int:
    """Run one-shot commands from argv or start the interactive shell."""

    args = list(sys.argv[1:] if argv is None else argv)
    shell = SearchShell()

    if args:
        shell.execute(" ".join(args))
    else:
        shell.run()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
