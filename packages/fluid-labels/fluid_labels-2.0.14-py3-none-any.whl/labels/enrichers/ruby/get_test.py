import pytest
import requests

from labels.enrichers.ruby.get import get_gem_package
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.fake_response import MockResponse


@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_get_gem_package_real_request() -> None:
    result = get_gem_package("rails")
    assert result is not None
    assert "name" in result


@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_get_gem_package_with_version_real_request() -> None:
    result = get_gem_package("rails", "7.0.4")
    assert result is not None
    assert "number" in result


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
async def test_get_gem_package_not_found() -> None:
    result = get_gem_package("nonexistent-package-12345")
    assert result is None
