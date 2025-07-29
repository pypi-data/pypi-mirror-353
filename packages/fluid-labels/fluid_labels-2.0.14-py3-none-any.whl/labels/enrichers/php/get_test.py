import pytest
import requests

from labels.enrichers.php.get import (
    PackagistPackageInfo,
    find_version,
    get_composer_package,
)
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.fake_response import MockResponse


def test_find_version_exact_match() -> None:
    versions: list[PackagistPackageInfo] = [
        {"version": "1.0.0", "name": "test"},
        {"version": "2.0.0", "name": "test"},
    ]
    result = find_version(versions, "2.0.0")
    assert result == {"version": "2.0.0", "name": "test"}


def test_find_version_no_match() -> None:
    versions: list[PackagistPackageInfo] = [
        {"version": "1.0.0", "name": "test"},
        {"version": "2.0.0", "name": "test"},
    ]
    result = find_version(versions, "3.0.0")
    assert result is None


def test_find_version_no_version_specified() -> None:
    versions: list[PackagistPackageInfo] = [
        {"version": "1.0.0", "name": "test"},
        {"version": "2.0.0", "name": "test"},
    ]
    result = find_version(versions, None)
    assert result == {"version": "1.0.0", "name": "test"}


def test_find_version_empty_list() -> None:
    versions: list[PackagistPackageInfo] = []
    result = find_version(versions, None)
    assert result is None


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
async def test_get_composer_package_not_found() -> None:
    result = get_composer_package("nonexistent/package12345")
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=requests,
            target="get",
            target_type="sync",
            expected=MockResponse(
                200,
                {
                    "packages": {
                        "test/package": [],
                    },
                },
            ),
        ),
    ],
)
async def test_get_composer_package_no_versions() -> None:
    result = get_composer_package("test/package")
    assert result is None


@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_get_composer_package_success() -> None:
    result = get_composer_package("symfony/console")
    assert result is not None
    assert "version" in result
    assert "name" in result
