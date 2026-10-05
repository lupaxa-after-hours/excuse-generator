"""Tests for the excuse-generator CLI."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from lupaxa.excuse_generator.cli import main
from lupaxa.excuse_generator.dataset import load_blame, load_excuses
from lupaxa.excuse_generator.exceptions import ExcuseDataError
from lupaxa.excuse_generator.models import Category, Level
from lupaxa.excuse_generator.version import __version__

_SRC = Path(__file__).resolve().parents[1] / "src"


def test_default_prints_one_excuse(capsys: pytest.CaptureFixture[str]) -> None:
    """Running with no arguments prints one excuse."""
    assert main(["--seed", "1"]) == 0
    line = capsys.readouterr().out
    assert line.endswith("\n")
    assert "\n" not in line.strip()
    assert line.strip()


def test_category(capsys: pytest.CaptureFixture[str]) -> None:
    """``--category coding`` stays inside that category."""
    catalog = load_excuses()
    allowed = {text for level in Level for text in catalog[Category.CODING][level]}
    assert main(["--category", "coding", "--seed", "2"]) == 0
    assert capsys.readouterr().out.strip() in allowed


def test_level(capsys: pytest.CaptureFixture[str]) -> None:
    """``--level absurd`` stays inside that level."""
    catalog = load_excuses()
    allowed = {text for category in Category for text in catalog[category][Level.ABSURD]}
    assert main(["--level", "absurd", "--seed", "3"]) == 0
    assert capsys.readouterr().out.strip() in allowed


def test_count(capsys: pytest.CaptureFixture[str]) -> None:
    """``--count 5`` prints five lines."""
    assert main(["--count", "5", "--seed", "4"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 5
    assert all(lines)


def test_blame(capsys: pytest.CaptureFixture[str]) -> None:
    """``--blame`` prints one packaged blame entry."""
    assert main(["--blame", "--seed", "5"]) == 0
    assert capsys.readouterr().out.strip() in set(load_blame())


def test_categories(capsys: pytest.CaptureFixture[str]) -> None:
    """``--categories`` lists categories in alphabetical order."""
    assert main(["--categories"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "coding",
        "deadline",
        "devops",
        "friday",
        "general",
        "household",
        "meeting",
    ]


def test_levels(capsys: pytest.CaptureFixture[str]) -> None:
    """``--levels`` keeps severity order."""
    assert main(["--levels"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "plausible",
        "questionable",
        "absurd",
        "unhinged",
    ]


def test_seed_is_repeatable(capsys: pytest.CaptureFixture[str]) -> None:
    """``--seed 42`` repeats."""
    assert main(["--seed", "42"]) == 0
    first = capsys.readouterr().out
    assert main(["--seed", "42"]) == 0
    assert capsys.readouterr().out == first


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    """``--version`` prints the package version and exits 0."""
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == f"excuse-generator {__version__}"


def test_invalid_category_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    """An unknown category is a usage error without a traceback."""
    assert main(["--category", "nope"]) == 2
    error = capsys.readouterr().err
    assert "Unknown category" in error
    assert "Traceback" not in error


def test_invalid_count() -> None:
    """A count outside 1 to 100 is a usage error."""
    with pytest.raises(SystemExit) as zero:
        main(["--count", "0"])
    assert zero.value.code == 2
    with pytest.raises(SystemExit) as huge:
        main(["--count", "101"])
    assert huge.value.code == 2


def test_blame_rejects_filters() -> None:
    """Blame cannot be combined with excuse filters."""
    with pytest.raises(SystemExit) as exc:
        main(["--blame", "--category", "coding"])
    assert exc.value.code == 2


def test_list_flags_are_exclusive() -> None:
    """Category and level listings cannot be combined."""
    with pytest.raises(SystemExit) as exc:
        main(["--categories", "--levels"])
    assert exc.value.code == 2


def test_data_failure_exits_1(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Broken packaged data exits 1 without a traceback."""

    def broken(*_args: object, **_kwargs: object) -> list[str]:
        raise ExcuseDataError("broken data")

    monkeypatch.setattr("lupaxa.excuse_generator.cli.get_excuses", broken)
    assert main([]) == 1
    error = capsys.readouterr().err
    assert "broken data" in error
    assert "Traceback" not in error


def test_module_entry_version() -> None:
    """``python -m lupaxa.excuse_generator --version`` prints the version."""
    env = os.environ.copy()
    src = str(_SRC)
    current = env.get("PYTHONPATH")
    env["PYTHONPATH"] = src if not current else src + os.pathsep + current
    proc = subprocess.run(
        [sys.executable, "-m", "lupaxa.excuse_generator", "--version"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert proc.returncode == 0, proc.stderr
    assert __version__ in proc.stdout
