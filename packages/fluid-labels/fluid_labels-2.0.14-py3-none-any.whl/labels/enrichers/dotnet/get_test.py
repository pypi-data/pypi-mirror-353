import pytest
import requests

import labels.enrichers.dotnet.get
from labels.enrichers.dotnet.get import (
    _fetch_nuget_data,
    _get_catalog_entry_from_items,
    _get_latest_package_data,
    _get_latest_version_group_url,
    _get_package_data_for_version,
    _get_package_index,
    _get_version_group_items,
    get_nuget_package,
)
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.fake_response import MockResponse
from labels.testing.utils.pytest_marks import parametrize_sync


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
async def test_fetch_nuget_data_failure() -> None:
    result = _fetch_nuget_data("https://api.nuget.org/test")
    assert result is None


def test_get_catalog_entry_from_items() -> None:
    items_list = [
        {"catalogEntry": {"version": "1.0.0"}},
        {"catalogEntry": {"version": "2.0.0"}},
    ]
    result = _get_catalog_entry_from_items(items_list)
    assert result == {"version": "2.0.0"}

    nested_items = [
        {
            "items": [
                {"catalogEntry": {"version": "1.0.0-pre"}},
                {"catalogEntry": {"version": "1.0.0"}},
            ],
        },
    ]
    result = _get_catalog_entry_from_items(nested_items)
    assert result == {"version": "1.0.0"}


def test_get_catalog_entry_from_items_only_prereleases() -> None:
    items_list = [
        {
            "items": [
                {"catalogEntry": {"version": "1.0.0-pre"}},
                {"catalogEntry": {"version": "1.1.0-pre"}},
                {"catalogEntry": {"version": "2.0.0-pre"}},
            ],
        },
    ]
    result = _get_catalog_entry_from_items(items_list)
    assert result is None


def test_get_catalog_entry_from_items_empty() -> None:
    result = _get_catalog_entry_from_items([])
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.dotnet.get,
            target="_get_latest_package_data",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_nuget_package_not_found() -> None:
    result = get_nuget_package("NonExistentPackage123456789")
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.dotnet.get,
            target="_fetch_nuget_data",
            target_type="sync",
            expected={"catalogEntry": None},
        ),
    ],
)
async def test_get_package_data_for_version_invalid_catalog() -> None:
    result = _get_package_data_for_version("TestPackage", "1.0.0")
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.dotnet.get,
            target="_fetch_nuget_data",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_package_data_for_version_no_package_data() -> None:
    result = _get_package_data_for_version("TestPackage", "1.0.0")
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.dotnet.get,
            target="_get_package_index",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_latest_package_data_no_index() -> None:
    result = _get_latest_package_data("TestPackage")
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.dotnet.get,
            target="_get_package_index",
            target_type="sync",
            expected={"items": []},
        ),
        Mock(
            module=labels.enrichers.dotnet.get,
            target="_get_latest_version_group_url",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_latest_package_data_no_items_url() -> None:
    result = _get_latest_package_data("TestPackage")
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.dotnet.get,
            target="_fetch_nuget_data",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_package_index_not_found() -> None:
    result = _get_package_index("TestPackage")
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.dotnet.get,
            target="_fetch_nuget_data",
            target_type="sync",
            expected={"items": [{"@id": "test_url"}]},
        ),
    ],
)
async def test_get_package_index_success() -> None:
    result = _get_package_index("TestPackage")
    assert result == {"items": [{"@id": "test_url"}]}


@parametrize_sync(
    args=["input_data", "expected"],
    cases=[
        [{}, None],
        [{"items": "not_a_list"}, None],
        [{"items": []}, None],
        [{"items": [{"@id": {"not": "a_string"}}]}, None],
        [{"items": [{"@id": "test_url"}]}, "test_url"],
    ],
)
def test_get_latest_version_group_url_cases(
    input_data: dict[str, str | None],
    expected: str | None,
) -> None:
    assert _get_latest_version_group_url(input_data) == expected


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.dotnet.get,
            target="_fetch_nuget_data",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_version_group_items_not_found() -> None:
    result = _get_version_group_items("test_url")
    assert result == []


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.dotnet.get,
            target="_fetch_nuget_data",
            target_type="sync",
            expected={"items": [{"catalogEntry": {"version": "1.0.0"}}]},
        ),
    ],
)
async def test_get_version_group_items_success() -> None:
    result = _get_version_group_items("test_url")
    assert result == [{"catalogEntry": {"version": "1.0.0"}}]


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_get_nuget_package_with_version() -> None:
    result = get_nuget_package("Newtonsoft.Json", "13.0.2")
    assert result is not None
    assert result["version"] == "13.0.2"


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_get_nuget_package_latest() -> None:
    result = get_nuget_package("Newtonsoft.Json")
    assert result is not None
    assert "version" in result
    assert "authors" in result
