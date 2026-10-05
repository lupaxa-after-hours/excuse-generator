"""Tests for excuse generation."""

from __future__ import annotations

import random

import pytest

from lupaxa.excuse_generator import (
    Category,
    ExcuseError,
    InvalidCategoryError,
    InvalidLevelError,
    Level,
    get_excuse,
    get_excuses,
)
from lupaxa.excuse_generator.dataset import load_excuses


def test_generation_returns_a_string() -> None:
    """An unfiltered excuse is a non-empty string."""
    excuse = get_excuse(rng=random.Random(1))
    assert isinstance(excuse, str)
    assert excuse.strip() == excuse
    assert excuse


def test_category_filtering() -> None:
    """A category limit stays inside that category."""
    catalog = load_excuses()
    allowed = _texts(catalog, category=Category.CODING)
    rng = random.Random(2)
    for _ in range(20):
        assert get_excuse(category="coding", rng=rng) in allowed


def test_level_filtering() -> None:
    """A level limit stays inside that level."""
    catalog = load_excuses()
    allowed = _texts(catalog, level=Level.ABSURD)
    rng = random.Random(3)
    for _ in range(20):
        assert get_excuse(level="absurd", rng=rng) in allowed


def test_combined_filtering() -> None:
    """Category and level together select that one pool."""
    catalog = load_excuses()
    allowed = set(catalog[Category.CODING][Level.QUESTIONABLE])
    chosen = get_excuse(
        category=Category.CODING,
        level=Level.QUESTIONABLE,
        rng=random.Random(4),
    )
    assert chosen in allowed
    assert "Git did something weird." in allowed


def test_random_category_can_vary() -> None:
    """Omitting the category can draw from more than one category."""
    catalog = load_excuses()
    owner = {text: category for category in Category for text in _texts(catalog, category=category)}
    rng = random.Random(5)
    seen = {owner[get_excuse(rng=rng)] for _ in range(40)}
    assert len(seen) > 1


def test_random_level_can_vary() -> None:
    """Omitting the level can draw from more than one level."""
    catalog = load_excuses()
    owner = {
        text: level for category in Category for level in Level for text in catalog[category][level]
    }
    rng = random.Random(6)
    seen = {owner[get_excuse(category="meeting", rng=rng)] for _ in range(40)}
    assert len(seen) > 1


def test_multiple_excuse_generation() -> None:
    """``get_excuses`` returns the requested number of strings."""
    excuses = get_excuses(5, category="friday", level="plausible", rng=random.Random(7))
    assert len(excuses) == 5
    assert all(isinstance(excuse, str) and excuse for excuse in excuses)


def test_invalid_category() -> None:
    """An unknown category is rejected."""
    with pytest.raises(InvalidCategoryError, match="Unknown category: nope"):
        get_excuse(category="nope")


def test_invalid_level() -> None:
    """An unknown level is rejected."""
    with pytest.raises(InvalidLevelError, match="Unknown level: spicy"):
        get_excuse(level="spicy")


def test_invalid_category_is_an_excuse_error() -> None:
    """Callers can catch the package base error."""
    with pytest.raises(ExcuseError):
        get_excuse(category=3)  # type: ignore[arg-type]


def test_count_must_be_positive() -> None:
    """A non-positive count is rejected."""
    with pytest.raises(ValueError, match="greater than zero"):
        get_excuses(0)
    with pytest.raises(ValueError, match="greater than zero"):
        get_excuses(True)  # type: ignore[arg-type]


def test_deterministic_rng() -> None:
    """The same generator seed produces the same excuses."""
    first = get_excuses(8, rng=random.Random(42))
    second = get_excuses(8, rng=random.Random(42))
    other = get_excuses(8, rng=random.Random(99))
    assert first == second
    assert first != other


def test_does_not_touch_global_random() -> None:
    """Generation leaves Python's global random state alone."""
    random.seed(123)
    before = random.getstate()
    get_excuse()
    get_excuses(3)
    assert random.getstate() == before


def _texts(
    catalog: dict[Category, dict[Level, tuple[str, ...]]],
    *,
    category: Category | None = None,
    level: Level | None = None,
) -> set[str]:
    categories = (category,) if category is not None else tuple(Category)
    levels = (level,) if level is not None else tuple(Level)
    return {text for item in categories for name in levels for text in catalog[item][name]}
