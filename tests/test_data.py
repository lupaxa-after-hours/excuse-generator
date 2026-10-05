"""Validation tests for the packaged datasets."""

from __future__ import annotations

import pytest

from lupaxa.excuse_generator.dataset import load_blame, load_excuses, parse_blame, parse_excuses
from lupaxa.excuse_generator.exceptions import ExcuseDataError, ExcuseError
from lupaxa.excuse_generator.models import Category, Level


def test_packaged_excuses_cover_every_category_and_level() -> None:
    """Every category has every level, with at least ten original excuses."""
    catalog = load_excuses()
    assert set(catalog) == set(Category)
    for category in Category:
        assert set(catalog[category]) == set(Level)
        for level in Level:
            excuses = catalog[category][level]
            assert len(excuses) >= 10
            for excuse in excuses:
                assert isinstance(excuse, str)
                assert excuse
                assert excuse == excuse.strip()
                assert "\n" not in excuse


def test_packaged_excuses_are_unique() -> None:
    """The same excuse is not stored twice."""
    catalog = load_excuses()
    excuses = [
        text for category in Category for level in Level for text in catalog[category][level]
    ]
    assert len(excuses) >= 280
    assert len(set(excuses)) == len(excuses)
    assert "Git did something weird." in catalog[Category.CODING][Level.QUESTIONABLE]


def test_packaged_blame_entries() -> None:
    """Blame entries are unique non-empty strings."""
    entries = load_blame()
    assert 30 <= len(entries) <= 50
    assert len(set(entries)) == len(entries)
    for entry in entries:
        assert isinstance(entry, str)
        assert entry
        assert entry == entry.strip()


def test_data_errors_are_excuse_errors() -> None:
    """Malformed packaged data uses the internal data error."""
    with pytest.raises(ExcuseDataError, match="JSON object"):
        parse_excuses([])
    with pytest.raises(ExcuseError):
        parse_blame({})


def test_duplicate_excuse_is_rejected() -> None:
    """A repeated excuse is a data error."""
    payload = _valid_excuses()
    payload["coding"]["plausible"].append(payload["devops"]["absurd"][0])
    with pytest.raises(ExcuseDataError, match="Duplicate excuse"):
        parse_excuses(payload)


def test_missing_level_is_rejected() -> None:
    """A category without a level is a data error."""
    payload = _valid_excuses()
    del payload["friday"]["unhinged"]
    with pytest.raises(ExcuseDataError, match="missing"):
        parse_excuses(payload)


def test_whitespace_excuse_is_rejected() -> None:
    """Surrounding whitespace is a data error."""
    payload = _valid_excuses()
    payload["general"]["plausible"] = ["  padded  "]
    with pytest.raises(ExcuseDataError, match="surrounding whitespace"):
        parse_excuses(payload)


def test_duplicate_blame_is_rejected() -> None:
    """A repeated blame entry is a data error."""
    with pytest.raises(ExcuseDataError, match="Duplicate blame entry"):
        parse_blame(["DNS.", "DNS."])


def test_empty_blame_entry_is_rejected() -> None:
    """A blank blame entry is a data error."""
    with pytest.raises(ExcuseDataError, match="non-empty"):
        parse_blame(["DNS.", ""])


def _valid_excuses() -> dict[str, dict[str, list[str]]]:
    return {
        category.value: {level.value: [f"{category.value} {level.value} sample"] for level in Level}
        for category in Category
    }
