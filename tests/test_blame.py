"""Tests for the blame generator."""

from __future__ import annotations

import random

from lupaxa.excuse_generator import get_blame
from lupaxa.excuse_generator.dataset import load_blame


def test_returns_a_known_blame_entry() -> None:
    """Blame comes from the packaged list."""
    entries = set(load_blame())
    rng = random.Random(1)
    for _ in range(15):
        blame = get_blame(rng=rng)
        assert blame in entries


def test_deterministic_rng() -> None:
    """The same generator seed produces the same blame."""
    assert get_blame(rng=random.Random(42)) == get_blame(rng=random.Random(42))


def test_does_not_touch_global_random() -> None:
    """Blame selection leaves Python's global random state alone."""
    random.seed(123)
    before = random.getstate()
    get_blame()
    assert random.getstate() == before
