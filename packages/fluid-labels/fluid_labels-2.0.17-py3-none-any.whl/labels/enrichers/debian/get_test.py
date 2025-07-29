import pytest

import labels.enrichers.debian.get
from labels.enrichers.debian.get import (
    get_deb_package,
    get_deb_package_version_list,
    get_deb_snapshot,
)
from labels.testing.mocks import Mock, mocks


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.debian.get,
            target="make_get",
            target_type="sync",
            expected={"error": "Package not found"},
        ),
    ],
)
async def test_get_deb_package_version_list_error_response() -> None:
    result = get_deb_package_version_list("nonexistent-package")
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.debian.get,
            target="make_get",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_deb_package_version_list_not_found() -> None:
    result = get_deb_package_version_list("nonexistent-package")
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.debian.get,
            target="make_get",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_deb_package_not_found() -> None:
    result = get_deb_package("nonexistent-package", "1.0.0")
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.debian.get,
            target="make_get",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_deb_package_error() -> None:
    result = get_deb_package("python3.9", "3.9.2-1")
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.debian.get,
            target="make_get",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_deb_snapshot_not_found() -> None:
    result = get_deb_snapshot("nonexistent-package", "1.0.0")
    assert result is None


@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_real_debian_package_request() -> None:
    versions = get_deb_package_version_list("bash")
    assert versions is not None
    assert len(versions) > 0
    latest_version = versions[0]["version"]

    package = get_deb_package("bash", latest_version)
    assert package is not None

    snapshot = get_deb_snapshot("bash", latest_version)
    assert snapshot is not None
