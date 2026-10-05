"""Excuse categories and absurdity levels."""

from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    """String enum for the Python 3.10 baseline.

    ``enum.StrEnum`` arrived in Python 3.11. This small stand-in keeps the
    same ``class Category(StrEnum)`` shape on 3.10.
    """

    def __str__(self) -> str:
        """Return the enum value."""
        return str(self.value)


class Category(StrEnum):
    """Excuse category."""

    CODING = "coding"
    DEVOPS = "devops"
    MEETING = "meeting"
    DEADLINE = "deadline"
    HOUSEHOLD = "household"
    GENERAL = "general"
    FRIDAY = "friday"


class Level(StrEnum):
    """Absurdity level, from believable to unreasonable."""

    PLAUSIBLE = "plausible"
    QUESTIONABLE = "questionable"
    ABSURD = "absurd"
    UNHINGED = "unhinged"
