"""Excuse categories and absurdity levels."""

from __future__ import annotations

from enum import StrEnum


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
