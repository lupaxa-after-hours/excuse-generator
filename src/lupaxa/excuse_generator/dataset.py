"""Load and validate packaged excuse and blame data."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from lupaxa.excuse_generator.exceptions import ExcuseDataError
from lupaxa.excuse_generator.models import Category, Level

ExcuseCatalog = dict[Category, dict[Level, tuple[str, ...]]]


def data_dir() -> Path:
    """Return the directory that holds the packaged JSON files.

    A checkout keeps the files in the repository ``data/`` directory.
    An installed wheel keeps copies inside the package.
    """
    repo = Path(__file__).resolve().parents[3] / "data" / "excuses.json"
    if repo.is_file():
        return repo.parent
    bundled = Path(__file__).resolve().parent / "data" / "excuses.json"
    if bundled.is_file():
        return bundled.parent
    raise ExcuseDataError("Packaged excuse data was not found.")


def load_excuses() -> ExcuseCatalog:
    """Return every excuse, grouped by category and level."""
    return parse_excuses(_read_json(data_dir() / "excuses.json", "excuses.json"))


def load_blame() -> tuple[str, ...]:
    """Return the blame entries."""
    return parse_blame(_read_json(data_dir() / "blame.json", "blame.json"))


def parse_excuses(payload: object) -> ExcuseCatalog:
    """Validate an excuse-data object and return it grouped by enum."""
    if not isinstance(payload, dict):
        raise ExcuseDataError("Excuse data must be a JSON object of categories.")

    found = _string_keys(payload, "Excuse categories")
    expected = {category.value for category in Category}
    _expect_exact_keys(found, expected, "categories")

    seen: set[str] = set()
    catalog: ExcuseCatalog = {}
    for category in Category:
        raw_levels = payload[category.value]
        if not isinstance(raw_levels, dict):
            raise ExcuseDataError(f"Category {category.value!r} must be a JSON object of levels.")
        level_keys = _string_keys(raw_levels, f"Levels for {category.value!r}")
        _expect_exact_keys(
            level_keys,
            {level.value for level in Level},
            f"levels for {category.value}",
        )
        catalog[category] = {}
        for level in Level:
            raw_items = raw_levels[level.value]
            if not isinstance(raw_items, list):
                raise ExcuseDataError(
                    f"Category {category.value!r} level {level.value!r} must be a list."
                )
            if not raw_items:
                raise ExcuseDataError(
                    f"Category {category.value!r} level {level.value!r} has no excuses."
                )
            items: list[str] = []
            for raw_item in raw_items:
                text = _text_entry(raw_item, kind="Excuse")
                if text in seen:
                    raise ExcuseDataError(f"Duplicate excuse: {text}")
                seen.add(text)
                items.append(text)
            catalog[category][level] = tuple(items)
    return catalog


def parse_blame(payload: object) -> tuple[str, ...]:
    """Validate a blame-data array and return the entries."""
    if not isinstance(payload, list):
        raise ExcuseDataError("Blame data must be a JSON array.")
    if not payload:
        raise ExcuseDataError("Blame data has no entries.")

    seen: set[str] = set()
    entries: list[str] = []
    for raw_item in payload:
        text = _text_entry(raw_item, kind="Blame entry")
        if text in seen:
            raise ExcuseDataError(f"Duplicate blame entry: {text}")
        seen.add(text)
        entries.append(text)
    return tuple(entries)


def _read_json(path: Path, name: str) -> object:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ExcuseDataError(f"Could not read packaged data: {name}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ExcuseDataError(f"Packaged data is not valid JSON: {name}") from exc


def _string_keys(payload: Mapping[object, object], label: str) -> set[str]:
    keys: set[str] = set()
    for key in payload:
        if not isinstance(key, str):
            raise ExcuseDataError(f"{label} must be strings.")
        keys.add(key)
    return keys


def _expect_exact_keys(found: set[str], expected: set[str], label: str) -> None:
    missing = sorted(expected - found)
    unexpected = sorted(found - expected)
    if missing or unexpected:
        raise ExcuseDataError(
            f"Excuse {label} do not match the packaged set "
            f"(missing: {missing}, unexpected: {unexpected})."
        )


def _text_entry(value: object, *, kind: str) -> str:
    if (
        not isinstance(value, str)
        or value == ""
        or value != value.strip()
        or "\n" in value
        or "\r" in value
    ):
        raise ExcuseDataError(
            f"{kind} must be a non-empty single-line string without surrounding whitespace."
        )
    return value
