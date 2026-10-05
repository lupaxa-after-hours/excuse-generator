"""lupaxa.excuse_generator — random excuses by category and absurdity.

``get_excuse`` returns one line. ``get_excuses`` returns several.
``get_blame`` returns something else to point at. Pass an ``rng`` when the
choice needs to be repeatable.
"""

from __future__ import annotations

from .exceptions import ExcuseDataError, ExcuseError, InvalidCategoryError, InvalidLevelError
from .generator import get_blame, get_excuse, get_excuses
from .models import Category, Level
from .version import __version__, get_version

__all__ = [
    "Category",
    "ExcuseDataError",
    "ExcuseError",
    "InvalidCategoryError",
    "InvalidLevelError",
    "Level",
    "__version__",
    "get_blame",
    "get_excuse",
    "get_excuses",
    "get_version",
]
