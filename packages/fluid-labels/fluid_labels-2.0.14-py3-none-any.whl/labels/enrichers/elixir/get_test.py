import pytest

import labels.enrichers.elixir.get
from labels.enrichers.elixir.get import get_hex_package
from labels.testing.mocks import Mock, mocks


@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_get_hex_package_real_request() -> None:
    result = get_hex_package("phoenix")
    assert result is not None
    assert "name" in result


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.elixir.get,
            target="make_get",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_hex_package_not_found() -> None:
    result = get_hex_package("nonexistent_package_12345")
    assert result is None
