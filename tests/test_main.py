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


def test_progress_bar_handles_zero_total_and_small_first_step() -> None:
    from src.main import format_progress_bar

    assert format_progress_bar(0, 0) == "[..........]"
    assert format_progress_bar(1, 100) == "[#.........]"


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

    assert "Progress [##########] 1/1 Load index" in output
    assert "Progress [##########] 1/1 Print index entry" in output
    assert "Progress [#####.....] 1/2 Load search index" in output
    assert "Progress [##########] 2/2 Search query" in output
    assert "Loaded index" in output
    assert "frequency=2" in output
    assert "https://quotes.toscrape.com/page/2/" in output


def test_build_command_saves_index_from_crawler(tmp_path, capsys) -> None:
    from src.main import SearchShell

    index_path = tmp_path / "index.json"
    shell = SearchShell(index_path=index_path, crawler=FakeCrawler())

    assert shell.execute("build") is True

    output = capsys.readouterr().out

    assert "Starting crawl" in output
    assert "Crawl progress [#.........] 1 page(s): https://quotes.toscrape.com/" in output
    assert "Building index from 1 page(s)" in output
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
    assert "Progress [#####.....] 1/2 Load explanation index" in output
    assert "Progress [##########] 2/2 Explain ranking" in output
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
    assert "Progress [##........] 1/5 Load benchmark index" in output
    assert "Progress [##########] 5/5 Print ranking comparison" in output
    assert "load_ms=" in output
    assert "naive_scan_ms=" in output
    assert "optimized_query_ms=" in output
    assert "optimized_vs_naive_speedup=" in output
    assert "word_lookup_ms=" in output
    assert "tfidf_query_ms=" in output
    assert "bm25_query_ms=" in output
    assert "phrase_query_ms=" in output
    assert "explain_ms=" in output
    assert "Ranking comparison:" in output
    assert "tfidf_top=" in output
    assert "bm25_top=" in output


def test_cli_benchmark_can_compare_bm25_parameter_grid(tmp_path, capsys) -> None:
    from src.main import SearchShell
    from src.search import IndexStore, SearchIndex

    index_path = tmp_path / "index.json"
    IndexStore(index_path).save(SearchIndex.from_dict(sample_index()))

    shell = SearchShell(index_path=index_path)

    assert shell.execute("benchmark --bm25-grid") is True

    output = capsys.readouterr().out

    assert "BM25 parameter comparison" in output
    assert "Progress [###.......] 1/3 BM25 grid" in output
    assert "Progress [##########] 3/3 BM25 grid" in output
    assert "k1=0.9 b=0.4" in output
    assert "k1=1.2 b=0.75" in output
    assert "k1=1.5 b=0.9" in output


def test_cli_benchmark_can_run_synthetic_stress_test(capsys) -> None:
    from src.main import SearchShell

    shell = SearchShell()

    assert shell.execute("benchmark --stress") is True

    output = capsys.readouterr().out

    assert "Synthetic stress benchmark:" in output
    assert "Progress [###.......] 1/3 Synthetic stress" in output
    assert "Progress [##########] 3/3 Synthetic stress" in output
    assert "| pages | terms | index_kb | candidates | build_ms |" in output
    assert "| 100 |" in output
    assert "| 500 |" in output
    assert "| 1000 |" in output


def test_cli_benchmark_reports_unknown_option(capsys) -> None:
    from src.main import SearchShell

    shell = SearchShell()

    assert shell.execute("benchmark --unknown") is True

    output = capsys.readouterr().out

    assert "Usage: benchmark [--bm25-grid|--stress]" in output


def test_missing_index_paths_do_not_traceback(tmp_path, capsys) -> None:
    from src.main import SearchShell

    shell = SearchShell(index_path=tmp_path / "missing.json")

    assert shell.execute("print good") is True
    assert shell.execute("explain good") is True
    assert shell.execute("benchmark") is True

    output = capsys.readouterr().out

    assert output.count("No index loaded") == 3


def test_invalid_index_json_reports_user_error(tmp_path, capsys) -> None:
    import pytest
    from src.main import SearchShell

    index_path = tmp_path / "index.json"
    index_path.write_text("{bad json", encoding="utf-8")
    shell = SearchShell(index_path=index_path)

    for command in ("load", "find good", "explain good", "benchmark"):
        try:
            assert shell.execute(command) is True
        except Exception as exc:  # pragma: no cover - documents regression output.
            pytest.fail(f"{command} raised {type(exc).__name__}: {exc}")

    output = capsys.readouterr().out

    assert "Invalid index file" in output
    assert "Run 'build' to regenerate it" in output
    assert "Traceback" not in output


def test_invalid_ranker_options_report_user_error(tmp_path, capsys) -> None:
    from src.main import SearchShell
    from src.search import IndexStore, SearchIndex

    index_path = tmp_path / "index.json"
    IndexStore(index_path).save(SearchIndex.from_dict(sample_index()))

    shell = SearchShell(index_path=index_path)

    assert shell.execute("find --ranker bad good") is True
    assert shell.execute("explain --ranker bad good") is True

    output = capsys.readouterr().out

    assert output.count("Unknown ranker: bad") == 2


def test_missing_ranker_query_reports_usage(tmp_path, capsys) -> None:
    from src.main import SearchShell
    from src.search import IndexStore, SearchIndex

    index_path = tmp_path / "index.json"
    IndexStore(index_path).save(SearchIndex.from_dict(sample_index()))

    shell = SearchShell(index_path=index_path)

    assert shell.execute("find --ranker") is True
    assert shell.execute("find --ranker bm25") is True
    assert shell.execute("explain --ranker") is True

    output = capsys.readouterr().out

    assert output.count("Usage: --ranker <frequency|tfidf|bm25> <query terms>") == 3


def test_unmatched_quote_reports_malformed_query(tmp_path, capsys) -> None:
    from src.main import SearchShell
    from src.search import IndexStore, SearchIndex

    index_path = tmp_path / "index.json"
    IndexStore(index_path).save(SearchIndex.from_dict(sample_index()))

    shell = SearchShell(index_path=index_path)

    assert shell.execute('find "good friends') is True
    assert shell.execute('explain "good friends') is True

    output = capsys.readouterr().out

    assert output.count("Malformed query: unmatched quote") == 2


def test_bm25_grid_handles_empty_index_without_traceback(tmp_path, capsys) -> None:
    from src.main import SearchShell
    from src.search import IndexStore, SearchIndex

    index_path = tmp_path / "index.json"
    payload = {
        "metadata": {
            "base_url": "https://quotes.toscrape.com/",
            "built_at": "2026-05-12T00:00:00+00:00",
            "page_count": 0,
            "document_lengths": {},
        },
        "pages": {},
        "index": {},
    }
    IndexStore(index_path).save(SearchIndex.from_dict(payload))

    shell = SearchShell(index_path=index_path)

    assert shell.execute("benchmark --bm25-grid") is True

    output = capsys.readouterr().out

    assert "BM25 parameter comparison" in output
    assert "No benchmark candidates" in output


def test_explain_handles_usage_and_no_results(tmp_path, capsys) -> None:
    from src.main import SearchShell
    from src.search import IndexStore, SearchIndex

    index_path = tmp_path / "index.json"
    IndexStore(index_path).save(SearchIndex.from_dict(sample_index()))

    shell = SearchShell(index_path=index_path)

    assert shell.execute("explain") is True
    assert shell.execute("explain zzzz") is True

    output = capsys.readouterr().out

    assert "Usage: explain <query terms>" in output
    assert "No pages found." in output


def test_interactive_run_handles_eof(monkeypatch, capsys) -> None:
    from src.main import SearchShell

    shell = SearchShell()
    monkeypatch.setattr("builtins.input", lambda prompt: (_ for _ in ()).throw(EOFError))

    shell.run()

    output = capsys.readouterr().out

    assert "XJCO3011 search shell" in output
    assert "Goodbye." in output


def test_interactive_run_exits_on_exit_command(monkeypatch, capsys) -> None:
    from src.main import SearchShell

    shell = SearchShell()
    monkeypatch.setattr("builtins.input", lambda prompt: "exit")

    shell.run()

    output = capsys.readouterr().out

    assert "XJCO3011 search shell" in output
    assert "Goodbye." in output


def test_interactive_run_continues_until_exit(monkeypatch, capsys) -> None:
    from src.main import SearchShell

    commands = iter(["help", "exit"])
    shell = SearchShell()
    monkeypatch.setattr("builtins.input", lambda prompt: next(commands))

    shell.run()

    output = capsys.readouterr().out

    assert "Commands:" in output
    assert "Goodbye." in output


def test_main_without_args_runs_shell(monkeypatch) -> None:
    from src import main as main_module

    calls: list[str] = []

    class FakeShell:
        def run(self) -> None:
            calls.append("run")

    monkeypatch.setattr(main_module, "SearchShell", FakeShell)

    assert main_module.main([]) == 0
    assert calls == ["run"]
