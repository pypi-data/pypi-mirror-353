from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from enum import Enum
from pathlib import Path

from skippy_cov import __version__, select_tests_to_run
from skippy_cov.diff_handler import DiffHandler
from skippy_cov.utils import CoverageMap, filter_by_path

logger = logging.getLogger(__name__)


class Format(Enum):
    pytest = "pytest"
    json = "json"
    lines = "lines"

    @classmethod
    def argtype(cls, s: str) -> Enum:
        try:
            return cls[s]
        except KeyError as e:
            raise argparse.ArgumentTypeError(  # noqa: TRY003
                f"{s!r} is not a valid format"
            ) from e

    def __str__(self):
        return self.value


def run(
    diff: str,
    coverage_file: Path,
    relative_to: list[Path] | None,
    keep_prefix: bool,
    fmt: Format = Format.pytest,
    display: bool = False,
) -> set[str]:
    """
    Run the test filter. If `display` = True will also print the output to stdout
    """
    diff_handler = DiffHandler(diff)
    coverage_map = CoverageMap(coverage_file)
    selected_tests = select_tests_to_run(diff_handler, coverage_map)
    tests = sorted(selected_tests)
    if not tests:
        logger.info("No specific tests selected to run based on changes and coverage.")
    if keep_prefix and relative_to and len(relative_to) > 1:
        logger.warning(
            "Trying to remove prefix with more than one path as filter is not allowed. "
            "The keep_prefix flag will be set to True"
        )
        keep_prefix = True

    if relative_to:
        selected_tests = filter_by_path(selected_tests, relative_to, keep_prefix)

    output = set()
    for test in selected_tests:
        output |= test.as_set()

    if display:
        if fmt == Format.pytest:
            print(" ".join(output))
        elif fmt == Format.lines:
            print("\n".join(output))
        elif fmt == Format.json:
            obj = {}
            for test in selected_tests:
                obj[test.path.as_posix()] = list(test.tests)
            print(json.dumps(obj))

    return output


def get_default_branch() -> str:
    """
    Determine the default branch to diff against.

    This function attempts to determine the default branch by inspecting the
    output of `git remote show origin`. If it fails to determine the branch
    (e.g., not in a git repository, or `origin` is not configured), it falls
    back to "main".

    Returns:
        str: The name of the default branch (e.g., "main", "develop").
    """
    try:
        output = subprocess.check_output(
            ["git", "remote", "show", "origin"], stderr=subprocess.DEVNULL, text=True
        )
        for line in output.splitlines():
            if "HEAD branch" in line:
                return line.split(":")[-1].strip()
    except Exception:
        logger.info("Could not determine default branch, falling back to 'main'.")
    return "main"


def get_diff_content(diff_arg: str | None = None) -> str:
    """
    Get the diff content based on the provided argument.
    It can either be a file path or a git ref/branch to diff against.
    """
    # If it's a file path and exists, read it as a file
    if diff_arg:  # Only try Path if diff_arg is not None/empty
        path = Path(diff_arg)
        if path.exists():
            return path.read_text()
    # Otherwise, treat as git diff argument (branch/refspec)
    diff_ref = diff_arg if diff_arg else f"{get_default_branch()}...HEAD"
    try:
        diff = subprocess.check_output(
            ["git", "diff", diff_ref], stderr=subprocess.DEVNULL, text=True
        )
    except Exception as e:
        print(
            f"skippy-cov: failed to get git diff for '{diff_ref}': {e}", file=sys.stderr
        )
        sys.exit(1)
    else:
        return diff


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Select pytest tests based on diff and coverage."
    )
    parser.add_argument(
        "--diff",
        required=False,
        help="Path to a diff file or a git ref/branch to diff against (default: main branch).",
        default=None,
    )
    parser.add_argument(
        "--coverage-file",
        required=False,
        help="Path to the coverage file (.coverage sqlite database).",
        type=Path,
        default=Path(".coverage"),
    )
    parser.add_argument(
        "--relative-to",
        required=False,
        help="Display only tests contained in a folder",
        type=Path,
        nargs="+",
        default=None,
    )
    parser.add_argument(
        "--keep-prefix",
        required=False,
        default=True,
        action="store_true",
        help="When using --relative-to, determine if the original path should be kept or removed",
    )
    parser.add_argument(
        "--strip-prefix",
        dest="keep_prefix",
        action="store_false",
        help="When using --relative-to, determine if the original path should be kept or removed",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging.", default=False
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--format",
        required=False,
        help="Output format",
        type=Format.argtype,
        default=Format.pytest,
        choices=Format,
    )
    args = parser.parse_args(argv)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    diff_content = (
        get_diff_content(args.diff) if args.diff is not None else get_diff_content(None)
    )

    run(
        diff_content,
        args.coverage_file,
        args.relative_to,
        args.keep_prefix,
        args.format,
        display=True,
    )
