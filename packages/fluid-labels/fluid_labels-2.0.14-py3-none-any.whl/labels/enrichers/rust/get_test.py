import pytest
import requests

from labels.enrichers.rust.get import get_cargo_package
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.fake_response import MockResponse


@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_get_cargo_package_real_request() -> None:
    result = get_cargo_package("serde")
    assert result is not None
    assert "crate" in result


@mocks(
    mocks=[
        Mock(
            module=requests,
            target="get",
            target_type="sync",
            expected=MockResponse(404, {}),
        ),
    ],
)
async def test_get_cargo_package_not_found() -> None:
    result = get_cargo_package("nonexistent-package-12345")
    assert result is None
