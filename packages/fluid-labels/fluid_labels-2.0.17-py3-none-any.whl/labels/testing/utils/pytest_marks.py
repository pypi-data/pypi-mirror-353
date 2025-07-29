from collections.abc import Awaitable, Callable, Iterable, Sequence
from typing import ParamSpec, TypeVar, cast

import freezegun
import pytest
from _pytest.mark.structures import MarkGenerator

T = TypeVar("T")
P = ParamSpec("P")

_tag = MarkGenerator(_ispytest=True)
pytest.mark = _tag


def parametrize_async(
    *,
    args: list[str],
    cases: list[list[object]],
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Wrap pytest.mark.parametrize. Include several cases for the same test.

    ```python
    @parametrize(
        args=["arg", "expected"],
        cases=[
            ["a", "A"],
            ["b", "B"],
            ["c", "C"],
        ],
    )
    async def test_function(arg: str, expected: str) -> None:
        assert function(arg) == expected
    ```
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        typed_args = cast(Sequence[str], args)
        typed_cases = cast(Iterable[Sequence[object]], cases)

        return _tag.parametrize(typed_args, typed_cases)(func)

    return decorator


def parametrize_sync(
    *,
    args: list[str],
    cases: list[list[object]],
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Wrap pytest.mark.parametrize. Include several cases for the same test.

    ```python
    @parametrize(
        args=["arg", "expected"],
        cases=[
            ["a", "A"],
            ["b", "B"],
            ["c", "C"],
        ],
    )
    def test_function(arg: str, expected: str) -> None:
        assert function(arg) == expected
    ```
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        typed_args = cast(Sequence[str], args)
        typed_cases = cast(Iterable[Sequence[object]], cases)

        return _tag.parametrize(typed_args, typed_cases)(func)

    return decorator


def freeze_time(
    time: str,
) -> Callable[[Callable[P, T | Awaitable[T]]], Callable[P, T | Awaitable[T]]]:
    """Wrap freezegun.freeze_time to set the execution time of the test.

    ```python
    @freeze_time("2024-06-20")
    async def test_function() -> None:
        ...
    ```
    """

    def decorator(func: Callable[P, T | Awaitable[T]]) -> Callable[P, T | Awaitable[T]]:
        return freezegun.freeze_time(time)(func)

    return decorator
