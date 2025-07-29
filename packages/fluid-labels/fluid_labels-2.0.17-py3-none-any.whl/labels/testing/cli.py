# Keep it in sync with integrates/back/integrates/testing/cli.py"
import argparse
import logging
import os
import sys
from collections.abc import Generator
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path
from typing import NamedTuple

import coverage
import pytest

from labels.config.logger import configure_logger

LOGGER = logging.getLogger(__name__)


class Args(NamedTuple):
    target: Path
    tests: list[str]


def _get_args() -> Args:
    parser = argparse.ArgumentParser(
        prog="labels-test",
        description=(
            "🏹 Python package for unit and integration testing through "
            "Fluid Attacks' Labels project"
        ),
    )

    parser.add_argument(
        "--target",
        metavar="TARGET",
        type=Path,
        required=True,
        help="Directory to test. Default is current directory.",
    )

    parser.add_argument(
        "--tests",
        metavar="TESTS",
        type=str,
        required=False,
        nargs="*",
        help="Tests to run. Default is all tests.",
    )

    args = parser.parse_args()

    return Args(
        target=args.target,  # type: ignore[misc]
        tests=args.tests,  # type: ignore[misc]
    )


@contextmanager
def _track_coverage(args: Args) -> Generator[coverage.Coverage, None, None]:
    cov = coverage.Coverage()
    cov.set_option("run:source", [str(args.target)])
    cov.set_option("run:branch", value=True)
    cov.set_option("run:omit", ["**/*_test.py", "**/exceptions.py"])
    cov.start()

    yield cov

    cov.stop()


def _cov_read(cov_path: Path) -> int:
    if cov_path.is_file():
        with Path.open(cov_path, encoding="utf-8") as cov_file:
            return int(cov_file.read())
    return 0


def _cov_write(cov_path: Path, cov: int) -> None:
    if not cov_path.is_file():
        cov_path.touch()
    with Path.open(cov_path, "w", encoding="utf-8") as cov_file:
        cov_file.write(str(cov))


def _cov_test(args: Args, cov: coverage.Coverage) -> bool:
    path = Path(f"{args.target}/coverage")
    current = _cov_read(path)
    new = round(
        Decimal(
            cov.report(
                output_format="text",
                skip_covered=True,
                show_missing=True,
                skip_empty=True,
                sort="cover",
            ),
        ),
    )

    if new == current:
        LOGGER.info("Coverage remained at %s%%.", current)
        return True
    if new > current:
        LOGGER.info(
            "Coverage increased from %s%% to %s%%. Please update coverage file in your commit.",
            current,
            new,
        )
        _cov_write(path, new)
        return False
    LOGGER.info("Coverage decreased from %s%% to %s%%. Please add tests.", current, new)
    return False


def _pytest(args: Args) -> bool:
    os.environ["RUNNING_TESTS"] = "true"

    pytest_args = ["--asyncio-mode=auto", "--showlocals", "--strict-markers", "-vv"]
    if args.tests:
        pytest_args.extend(["-k", " or ".join(args.tests)])

    exit_code = pytest.main([str(args.target), *pytest_args])

    # https://docs.pytest.org/en/stable/reference/exit-codes.html
    # 0 for pass, 5 for no tests collected
    return exit_code in [0, 5]


def main() -> bool:
    configure_logger(log_to_remote=False)
    args = _get_args()

    if not args.tests:
        with _track_coverage(args) as cov:
            result = _pytest(args)
            result = result and _cov_test(args, cov)
    else:
        result = _pytest(args)

    return sys.exit(0) if result else sys.exit(1)
