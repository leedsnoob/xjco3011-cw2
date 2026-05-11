"""Tests for command-line behavior."""

from __future__ import annotations

import subprocess
import sys

from tests.test_search import sample_index


class FakeCrawler:
    def crawl(self):
        from src.crawler import CrawledPage

        return [
            CrawledPage(
                url="https://quotes.toscrape.com/",
                title="Quotes",
                text="Good friends are good.",
                next_url=None,
            )
        ]


def test_load_print_and_find_commands_use_persisted_index(tmp_path, capsys) -> None:
    from src.main import SearchShell
    from src.search import IndexStore, SearchIndex

    index_path = tmp_path / "index.json"
    IndexStore(index_path).save(SearchIndex.from_dict(sample_index()))

    shell = SearchShell(index_path=index_path)

    assert shell.execute("load") is True
    assert shell.execute("print good") is True
    assert shell.execute("find good friends") is True

    output = capsys.readouterr().out

    assert "Loaded index" in output
    assert "frequency=2" in output
    assert "https://quotes.toscrape.com/page/2/" in output


def test_build_command_saves_index_from_crawler(tmp_path, capsys) -> None:
    from src.main import SearchShell

    index_path = tmp_path / "index.json"
    shell = SearchShell(index_path=index_path, crawler=FakeCrawler())

    assert shell.execute("build") is True

    output = capsys.readouterr().out

    assert "Built index for 1 page(s)" in output
    assert index_path.exists()


def test_help_blank_print_usage_and_missing_load(tmp_path, capsys) -> None:
    from src.main import SearchShell, main

    shell = SearchShell(index_path=tmp_path / "missing.json")

    assert shell.execute("") is True
    assert shell.execute("help") is True
    assert shell.execute("print") is True
    assert shell.execute("load") is True
    assert main(["help"]) == 0

    output = capsys.readouterr().out

    assert "Commands:" in output
    assert "Usage: print <word>" in output
    assert "Index file not found" in output


def test_build_command_reports_crawl_error(tmp_path, capsys) -> None:
    from src.crawler import CrawlError
    from src.main import SearchShell

    class BrokenCrawler:
        def crawl(self):
            raise CrawlError("network unavailable")

    shell = SearchShell(index_path=tmp_path / "index.json", crawler=BrokenCrawler())

    assert shell.execute("build") is True

    assert "network unavailable" in capsys.readouterr().out


def test_find_requires_query_and_loaded_index(tmp_path, capsys) -> None:
    from src.main import SearchShell

    shell = SearchShell(index_path=tmp_path / "missing.json")

    assert shell.execute("find") is True
    assert shell.execute("find good") is True

    output = capsys.readouterr().out

    assert "Usage: find <query terms>" in output
    assert "No index loaded" in output


def test_find_auto_loads_existing_index_for_one_shot_usage(tmp_path, capsys) -> None:
    from src.main import SearchShell
    from src.search import IndexStore, SearchIndex

    index_path = tmp_path / "index.json"
    IndexStore(index_path).save(SearchIndex.from_dict(sample_index()))

    shell = SearchShell(index_path=index_path)

    assert shell.execute("find good friends") is True

    output = capsys.readouterr().out

    assert "https://quotes.toscrape.com/page/2/" in output


def test_unknown_and_exit_commands(capsys) -> None:
    from src.main import SearchShell

    shell = SearchShell()

    assert shell.execute("unknown") is True
    assert shell.execute("exit") is False

    output = capsys.readouterr().out

    assert "Unknown command" in output


def test_importing_cli_does_not_emit_environment_warning() -> None:
    result = subprocess.run(
        [sys.executable, "-c", "import src.main"],
        capture_output=True,
        check=True,
        text=True,
    )

    assert "NotOpenSSLWarning" not in result.stderr


def test_cli_one_shot_unknown_command_does_not_traceback() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "src.main", "not-a-command"],
        capture_output=True,
        check=True,
        text=True,
    )

    assert "Unknown command" in result.stdout
    assert "Traceback" not in result.stderr


def test_cli_explain_command_outputs_term_contributions(tmp_path, capsys) -> None:
    from src.main import SearchShell
    from src.search import IndexStore, SearchIndex

    index_path = tmp_path / "index.json"
    IndexStore(index_path).save(SearchIndex.from_dict(sample_index()))

    shell = SearchShell(index_path=index_path)

    assert shell.execute("explain --ranker bm25 good friends") is True

    output = capsys.readouterr().out

    assert "ranker=bm25" in output
    assert "tf=" in output
    assert "df=" in output
    assert "idf=" in output
    assert "contribution=" in output


def test_cli_find_accepts_ranker_option(tmp_path, capsys) -> None:
    from src.main import SearchShell
    from src.search import IndexStore, SearchIndex

    index_path = tmp_path / "index.json"
    IndexStore(index_path).save(SearchIndex.from_dict(sample_index()))

    shell = SearchShell(index_path=index_path)

    assert shell.execute("find --ranker bm25 good friends") is True

    output = capsys.readouterr().out

    assert "Found" in output
    assert "score=" in output


def test_cli_benchmark_command_reports_timings(tmp_path, capsys) -> None:
    from src.main import SearchShell
    from src.search import IndexStore, SearchIndex

    index_path = tmp_path / "index.json"
    IndexStore(index_path).save(SearchIndex.from_dict(sample_index()))

    shell = SearchShell(index_path=index_path)

    assert shell.execute("benchmark") is True

    output = capsys.readouterr().out

    assert "Benchmark results" in output
    assert "load_ms=" in output
    assert "tfidf_query_ms=" in output
    assert "bm25_query_ms=" in output
