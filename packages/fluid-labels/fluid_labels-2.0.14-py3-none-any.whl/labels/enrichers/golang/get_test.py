import pytest

import labels.enrichers.golang.get
from labels.enrichers.golang.get import fetch_latest_version_info, fetch_license_info
from labels.testing.mocks import Mock, mocks


@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_fetch_latest_version_info_real_request() -> None:
    result = fetch_latest_version_info("golang.org/x/text")
    assert result is not None
    assert "Version" in result
    assert "Time" in result


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.golang.get,
            target="make_get",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_fetch_latest_version_info_not_found() -> None:
    result = fetch_latest_version_info("nonexistent/module/v1")
    assert result is None


@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_fetch_license_info_real_request() -> None:
    result = fetch_license_info("golang/go")
    assert result is not None
    assert "license" in result
    assert "content" in result


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.golang.get,
            target="make_get",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_fetch_license_info_not_found() -> None:
    result = fetch_license_info("nonexistent/repo12345")
    assert result is None
