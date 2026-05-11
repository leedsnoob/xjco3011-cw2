"""Command-line entry point for the coursework search tool."""

from __future__ import annotations

import sys
from collections.abc import Iterable
from pathlib import Path

from src.crawler import CrawlError, QuoteCrawler
from src.indexer import PageDocument, build_search_index
from src.search import DEFAULT_INDEX_PATH, IndexStore, SearchIndex, format_results


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
        if not self.index:
            print("No index loaded. Run 'build' or 'load' first.")
            return
        print(self.index.format_index_entry(word))

    def _find(self, query: str) -> None:
        if not query:
            print("Usage: find <query terms>")
            return
        if not self.index:
            print("No index loaded. Run 'build' or 'load' first.")
            return
        print(format_results(self.index.find(query), query, self.index))


def help_text() -> str:
    return "\n".join(
        [
            "Commands:",
            "  build              crawl the site, build the index, and save it",
            "  load               load the saved index from disk",
            "  print <word>       print the inverted index entry for a word",
            "  find <query>       find pages containing all query terms",
            '  find "a phrase"    find pages containing an exact phrase',
            "  help               show this help",
            "  exit               leave the shell",
        ]
    )


def main(argv: Iterable[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    shell = SearchShell()

    if args:
        shell.execute(" ".join(args))
    else:
        shell.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
