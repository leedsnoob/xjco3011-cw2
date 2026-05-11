"""Tests for command-line behavior."""

from __future__ import annotations

import subprocess
import sys

from tests.test_search import sample_index


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
