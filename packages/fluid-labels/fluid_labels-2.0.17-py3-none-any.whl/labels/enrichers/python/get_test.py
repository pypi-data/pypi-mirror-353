import pytest
import requests

from labels.enrichers.python.get import get_pypi_package
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.fake_response import MockResponse


@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_get_pypi_package_real_request() -> None:
    result = get_pypi_package("requests")
    assert result is not None
    assert "info" in result


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
async def test_get_pypi_package_not_found() -> None:
    result = get_pypi_package("nonexistent-package")
    assert result is None
