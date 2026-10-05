"""Command-line interface for lupaxa.excuse_generator."""

from __future__ import annotations

import argparse
import random
import sys

from lupaxa.excuse_generator.exceptions import ExcuseDataError, ExcuseError
from lupaxa.excuse_generator.generator import get_blame, get_excuses
from lupaxa.excuse_generator.models import Category, Level
from lupaxa.excuse_generator.version import get_version

MAX_COUNT = 100


def build_parser() -> argparse.ArgumentParser:
    """Return the excuse-generator argument parser."""
    parser = argparse.ArgumentParser(
        prog="excuse-generator",
        description="Generate a random excuse.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit.",
    )
    parser.add_argument(
        "-c",
        "--category",
        help="Limit excuses to one category.",
    )
    parser.add_argument(
        "-l",
        "--level",
        help="Limit excuses to one absurdity level.",
    )
    parser.add_argument(
        "-n",
        "--count",
        type=_count,
        default=None,
        help=f"Print this many excuses (1 to {MAX_COUNT}).",
    )
    parser.add_argument(
        "--blame",
        action="store_true",
        help="Print one thing to blame.",
    )
    parser.add_argument(
        "--categories",
        action="store_true",
        help="List categories and exit.",
    )
    parser.add_argument(
        "--levels",
        action="store_true",
        help="List absurdity levels and exit.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed generation for a repeatable result.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"excuse-generator {get_version()}")
        return 0

    _reject_combinations(parser, args)

    try:
        if args.categories:
            for category in sorted(category.value for category in Category):
                print(category)
            return 0
        if args.levels:
            for level in Level:
                print(level.value)
            return 0

        generator = random.Random(args.seed)
        if args.blame:
            print(get_blame(rng=generator))
            return 0

        excuses = get_excuses(
            1 if args.count is None else args.count,
            category=args.category,
            level=args.level,
            rng=generator,
        )
    except ExcuseDataError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except ExcuseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    for excuse in excuses:
        print(excuse)
    return 0


def _count(value: str) -> int:
    try:
        count = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("count must be an integer") from exc
    if count < 1:
        raise argparse.ArgumentTypeError("count must be greater than zero")
    if count > MAX_COUNT:
        raise argparse.ArgumentTypeError(f"count must be at most {MAX_COUNT}")
    return count


def _reject_combinations(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    filters: list[str] = []
    if args.category is not None:
        filters.append("--category")
    if args.level is not None:
        filters.append("--level")
    if args.count is not None:
        filters.append("--count")

    if args.categories and args.levels:
        parser.error("--categories and --levels cannot be used together")
    if args.blame and (filters or args.categories or args.levels):
        parser.error("--blame cannot be combined with excuse options")
    if (args.categories or args.levels) and (filters or args.seed is not None):
        flag = "--categories" if args.categories else "--levels"
        parser.error(f"{flag} cannot be combined with generation options")
