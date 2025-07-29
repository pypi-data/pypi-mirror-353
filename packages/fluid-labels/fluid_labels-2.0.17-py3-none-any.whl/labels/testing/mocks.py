import functools
from collections.abc import Awaitable, Callable, Iterator
from contextlib import contextmanager
from types import ModuleType
from typing import Literal, NamedTuple, ParamSpec, TypeVar

import pytest

T = TypeVar("T")
P = ParamSpec("P")
TargetType = Literal["sync", "async", "managed", "function"]


class Mock(NamedTuple):
    module: ModuleType
    target: str
    target_type: TargetType
    expected: object


def mocks(  # noqa: C901
    *,
    mocks: list[Mock],
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Apply a list of mocks to the test function.

    Example usage:

    ```python
    @mocks(
        mocks=[
            Mock(module, target, target_type, expected),
            ...
        ],
    )
    async def test_something():
        ...
    ```
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:  # type: ignore[misc]
            def _mock(monkeypatch: pytest.MonkeyPatch, mock: Mock) -> None:
                def _sync(*_args: P.args, **_kwargs: P.kwargs) -> object:
                    return mock.expected

                async def _async(*_args: P.args, **_kwargs: P.kwargs) -> object:
                    return mock.expected

                @contextmanager
                def _managed_function() -> Iterator[object]:
                    yield mock.expected

                match mock.target_type:
                    case "sync":
                        monkeypatch.setattr(mock.module, mock.target, _sync)
                    case "async":
                        monkeypatch.setattr(mock.module, mock.target, _async)
                    case "function":
                        monkeypatch.setattr(mock.module, mock.target, mock.expected)
                    case _:
                        monkeypatch.setattr(mock.module, mock.target, _managed_function)

            with pytest.MonkeyPatch.context() as monkeypatch:
                for mock in mocks:
                    _mock(monkeypatch, mock)
                return await func(*args, **kwargs)

        return wrapper  # type: ignore[misc]

    return decorator
