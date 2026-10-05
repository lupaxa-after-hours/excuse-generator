"""Choose excuses and blame from the packaged datasets."""

from __future__ import annotations

import random

from lupaxa.excuse_generator.dataset import load_blame, load_excuses
from lupaxa.excuse_generator.exceptions import InvalidCategoryError, InvalidLevelError
from lupaxa.excuse_generator.models import Category, Level


def get_excuse(
    category: Category | str | None = None,
    level: Level | str | None = None,
    *,
    rng: random.Random | None = None,
) -> str:
    """Return one excuse.

    ``category`` and ``level`` narrow the pool. When either is omitted, one
    is chosen from the full set. Pass ``rng`` to make the choice repeatable
    without touching Python's global random state.
    """
    catalog = load_excuses()
    generator = _generator(rng)
    chosen_category = _category(category)
    chosen_level = _level(level)
    if chosen_category is None:
        chosen_category = generator.choice(tuple(Category))
    if chosen_level is None:
        chosen_level = generator.choice(tuple(Level))
    return generator.choice(catalog[chosen_category][chosen_level])


def get_excuses(
    count: int,
    category: Category | str | None = None,
    level: Level | str | None = None,
    *,
    rng: random.Random | None = None,
) -> list[str]:
    """Return ``count`` excuses, drawing with replacement."""
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise ValueError("count must be an integer greater than zero")
    generator = _generator(rng)
    return [get_excuse(category, level, rng=generator) for _ in range(count)]


def get_blame(*, rng: random.Random | None = None) -> str:
    """Return one thing to blame."""
    return _generator(rng).choice(load_blame())


def _generator(rng: random.Random | None) -> random.Random:
    if rng is None:
        return random.Random()
    return rng


def _category(category: Category | str | None) -> Category | None:
    if category is None:
        return None
    if isinstance(category, Category):
        return category
    if isinstance(category, str):
        try:
            return Category(category)
        except ValueError as exc:
            raise InvalidCategoryError(f"Unknown category: {category}") from exc
    raise InvalidCategoryError(f"Unknown category: {category!r}")


def _level(level: Level | str | None) -> Level | None:
    if level is None:
        return None
    if isinstance(level, Level):
        return level
    if isinstance(level, str):
        try:
            return Level(level)
        except ValueError as exc:
            raise InvalidLevelError(f"Unknown level: {level}") from exc
    raise InvalidLevelError(f"Unknown level: {level!r}")
