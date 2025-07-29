from re import Pattern
from typing import TypeVar

import pytest
from _pytest.python_api import RaisesContext

E = TypeVar("E", bound=BaseException)


def raises(
    expected_exc: type[E] | tuple[type[E], ...],
    match: str | Pattern[str] | None = None,
) -> RaisesContext[E]:
    """Wrap pytest.raises to handle exceptions in tests.

    ```python
    with raises(ValueError):
        function_that_raises_value_error()
    ```
    """
    return pytest.raises(expected_exc, match=match)
