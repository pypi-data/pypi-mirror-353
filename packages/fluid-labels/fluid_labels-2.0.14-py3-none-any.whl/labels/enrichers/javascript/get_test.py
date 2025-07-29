import pytest

import labels.enrichers.javascript.get
from labels.enrichers.javascript.get import get_npm_package
from labels.testing.mocks import Mock, mocks


@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_get_npm_package_real_request() -> None:
    result = get_npm_package("express")
    assert result is not None
    assert "name" in result
    assert "versions" in result


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.javascript.get,
            target="make_get",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_npm_package_not_found() -> None:
    result = get_npm_package("fake-package")
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.javascript.get,
            target="make_get",
            target_type="sync",
            expected={
                "name": "test-package",
                "time": {
                    "unpublished": {
                        "time": "2025-05-07T00:00:00.000Z",
                        "versions": ["1.0.0"],
                    },
                },
            },
        ),
    ],
)
async def test_get_npm_package_unpublished() -> None:
    result = get_npm_package("test-package")
    assert result is None
