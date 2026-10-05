"""Custom exceptions for the excuse generator."""

from __future__ import annotations


class ExcuseError(Exception):
    """Base application exception."""


class InvalidCategoryError(ExcuseError):
    """Unknown excuse category."""


class InvalidLevelError(ExcuseError):
    """Unknown absurdity level."""


class ExcuseDataError(ExcuseError):
    """Packaged excuse data is invalid."""
