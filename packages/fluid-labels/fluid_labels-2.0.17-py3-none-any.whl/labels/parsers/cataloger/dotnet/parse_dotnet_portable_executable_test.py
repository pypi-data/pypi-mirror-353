import logging
from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import MagicMock, patch

import pefile
from _pytest.logging import LogCaptureFixture

from labels.model.file import Coordinates, Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.dotnet.parse_dotnet_portable_executable import (
    DotnetPortableExecutableEntry,
    build_dot_net_package,
    extract_version,
    find_name,
    find_version,
    keep_greater_semantic_version,
    parse_dotnet_portable_executable,
    parse_version_resource,
    process_file_info,
    punctuation_count,
    space_normalize,
)
from labels.testing.utils.helpers import get_test_data_path
from labels.testing.utils.pytest_marks import parametrize_sync
from labels.utils.file import new_location


def test_parse_dotnet_portable_executable() -> None:
    test_data_path = get_test_data_path("dependencies/dotnet/EntityFramework.dll")
    expected_packages = [
        Package(
            name="EntityFramework",
            version="6.5.1",
            language=Language.DOTNET,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=None,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.DotnetPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=DotnetPortableExecutableEntry(
                assembly_version="6.0.0.0",
                legal_copyright=("© Microsoft Corporation. All rights reserved."),
                company_name="Microsoft Corporation",
                product_name="Microsoft Entity Framework",
                product_version="6.5.1",
                comments="EntityFramework.dll",
                internal_name="EntityFramework.dll",
            ),
            p_url="pkg:nuget/EntityFramework@6.5.1",
        ),
    ]

    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, relations = parse_dotnet_portable_executable(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        assert relations == []
        assert pkgs == expected_packages


def test_parse_version_resource_no_version_info() -> None:
    mock_pe = MagicMock(spec=pefile.PE)
    delattr(mock_pe, "VS_VERSIONINFO")

    result = parse_version_resource(mock_pe)
    assert result is None


def test_parse_version_resource_no_file_info() -> None:
    mock_pe = MagicMock(spec=pefile.PE)
    mock_pe.VS_VERSIONINFO = [MagicMock()]
    delattr(mock_pe, "FileInfo")

    result = parse_version_resource(mock_pe)
    assert result is None


def test_parse_version_resource_no_stringtable() -> None:
    mock_pe = MagicMock(spec=pefile.PE)
    mock_pe.VS_VERSIONINFO = [MagicMock()]
    mock_pe.FileInfo = [MagicMock()]

    mock_file_info = MagicMock()
    mock_file_info.StringTable = None
    mock_pe.FileInfo[0] = mock_file_info

    result = parse_version_resource(mock_pe)
    assert result is None


def test_parse_version_resource_no_valid_stringtable() -> None:
    mock_pe = MagicMock(spec=pefile.PE)
    mock_pe.VS_VERSIONINFO = [MagicMock(), MagicMock()]
    mock_pe.FileInfo = [MagicMock(), MagicMock()]

    for file_info in mock_pe.FileInfo:
        file_info.StringTable = None

    result = parse_version_resource(mock_pe)
    assert result is None


def test_process_file_info_no_stringtable() -> None:
    mock_file_info = MagicMock(spec=pefile.Structure)
    mock_file_info.StringTable = []

    result = process_file_info([mock_file_info])
    assert result is None


@parametrize_sync(
    args=["input_str", "expected"],
    cases=[
        ["", ""],
        ["  hello   world  ", "hello world"],
        ["hello\tworld\n", "hello world"],
        ["hello    world", "hello world"],
        ["hello\x00world", "helloworld"],
        ["hello\x1fworld", "hello world"],
        ["hello café", "hello café"],
        ["hello 🌍", "hello 🌍"],
        ["  hello   world  \t\n  ", "hello world"],
    ],
)
def test_space_normalize(input_str: str, expected: str) -> None:
    assert space_normalize(input_str) == expected


@parametrize_sync(
    args=["version_resources", "expected"],
    cases=[
        [
            {
                "ProductName": "My Custom App",
                "FileDescription": "Application Description",
                "InternalName": "app.exe",
                "OriginalFilename": "original.exe",
            },
            "My Custom App",
        ],
        [
            {
                "ProductName": "",
                "FileDescription": "Application Description",
                "InternalName": "app.exe",
                "OriginalFilename": "original.exe",
            },
            "Application Description",
        ],
        [
            {
                "ProductName": "",
                "FileDescription": "",
                "InternalName": "app.exe",
                "OriginalFilename": "original.exe",
            },
            "app.exe",
        ],
        [
            {
                "ProductName": "",
                "FileDescription": "",
                "InternalName": "",
                "OriginalFilename": "original.exe",
            },
            "original.exe",
        ],
        [
            {
                "ProductName": "",
                "FileDescription": "",
                "InternalName": "",
                "OriginalFilename": "",
            },
            "",
        ],
    ],
)
def test_find_name_non_microsoft(version_resources: dict[str, str], expected: str) -> None:
    assert find_name(version_resources) == expected


@parametrize_sync(
    args=["version", "expected"],
    cases=[
        ["1.2.3", 2],
        ["1,2,3", 2],
        ["1", 0],
        ["", 0],
    ],
)
def test_punctuation_count(version: str, expected: int) -> None:
    assert punctuation_count(version) == expected


@parametrize_sync(
    args=["version", "expected"],
    cases=[
        ["1.2.3 beta", "1.2.3"],
        ["2.0.0 release candidate", "2.0.0"],
        ["3.1.0 preview", "3.1.0"],
        ["4.5.6 alpha test", "4.5.6"],
        ["1.2.3 4.5.6", "1.2.3 4.5.6"],
        ["alpha beta", "alpha beta"],
        ["", ""],
    ],
)
def test_extract_version(version: str, expected: str) -> None:
    assert extract_version(version) == expected


@parametrize_sync(
    args=["product_version", "file_version", "expected"],
    cases=[
        ["1.2.3", "1.2.4", "1.2.4"],
        ["1.2.4", "1.2.3", "1.2.4"],
        ["1.2.3", "1.2.3", ""],
        ["invalid", "1.2.3", ""],
        ["1.2.3", "invalid", "1.2.3"],
        ["invalid", "invalid", ""],
        ["1.2.3-alpha", "1.2.3-beta", "1.2.3-beta"],
        ["1.2.3-beta", "1.2.3-alpha", "1.2.3-beta"],
        ["1.2.3+123", "1.2.4+456", "1.2.4+456"],
        ["1.2.3+123", "1.2.4+456", "1.2.4+456"],
    ],
)
def test_keep_greater_semantic_version(
    product_version: str,
    file_version: str,
    expected: str,
) -> None:
    assert keep_greater_semantic_version(product_version, file_version) == expected


@parametrize_sync(
    args=["version_resources", "expected"],
    cases=[
        [
            {"ProductVersion": "1.2.3", "FileVersion": "1.2.4"},
            "1.2.4",
        ],
        [
            {"ProductVersion": "1.2.4", "FileVersion": "1.2.3"},
            "1.2.4",
        ],
        [
            {"ProductVersion": "1.2.3", "FileVersion": "1.2.3"},
            "1.2.3",
        ],
        [
            {"ProductVersion": "1.2.3", "FileVersion": "1.2"},
            "1.2.3",
        ],
        [
            {"ProductVersion": "1.2", "FileVersion": "1.2.3"},
            "1.2.3",
        ],
        [
            {"ProductVersion": "invalid", "FileVersion": "1.2.3"},
            "1.2.3",
        ],
        [
            {"ProductVersion": "1.2.3", "FileVersion": "invalid"},
            "1.2.3",
        ],
        [
            {},
            "",
        ],
        [
            {"ProductVersion": "alpha", "FileVersion": "beta"},
            "alpha",
        ],
        [
            {"ProductVersion": "alpha", "FileVersion": "1.2.3"},
            "1.2.3",
        ],
        [
            {"ProductVersion": "1.2.3", "FileVersion": "beta"},
            "1.2.3",
        ],
        [
            {
                "ProductVersion": "1",
                "FileVersion": "alpha.beta",
            },
            "1",
        ],
        [
            {
                "ProductVersion": "alpha",
                "FileVersion": "1",
            },
            "1",
        ],
    ],
)
def test_find_version(version_resources: dict[str, str], expected: str) -> None:
    assert find_version(version_resources) == expected


def test_build_dot_net_package_no_name() -> None:
    version_resources = {
        "ProductName": "",
        "FileDescription": "",
        "InternalName": "",
        "OriginalFilename": "",
    }

    test_path = "/test/path/file.dll"
    bytes_io = BytesIO(b"test content")
    text_io = TextIOWrapper(bytes_io, encoding="utf-8")
    reader = LocationReadCloser(
        location=new_location(test_path),
        read_closer=text_io,
    )

    result = build_dot_net_package(version_resources, reader)
    assert result is None


def test_build_dot_net_package_no_version(caplog: LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    version_resources = {
        "ProductName": "TestApp",
        "ProductVersion": "",
        "FileVersion": "",
    }

    test_path = "/test/path/file.dll"
    bytes_io = BytesIO(b"test content")
    text_io = TextIOWrapper(bytes_io, encoding="utf-8")
    reader = LocationReadCloser(
        location=new_location(test_path),
        read_closer=text_io,
    )

    result = build_dot_net_package(version_resources, reader)
    assert result is None
    assert (
        "Unable to find version for portable executable in file /test/path/file.dll" in caplog.text
    )


def test_parse_dotnet_portable_executable_no_coordinates() -> None:
    test_path = "/test/path/file.dll"
    bytes_io = BytesIO(b"test content")
    text_io = TextIOWrapper(bytes_io, encoding="utf-8")

    location = Location(
        coordinates=None,
        access_path=test_path,
        annotations={},
    )

    reader = LocationReadCloser(
        location=location,
        read_closer=text_io,
    )

    pkgs, relations = parse_dotnet_portable_executable(None, None, reader)
    assert pkgs == []
    assert relations == []


def test_parse_dotnet_portable_executable_invalid_pe() -> None:
    test_path = "/test/path/file.dll"
    bytes_io = BytesIO(b"test content")
    text_io = TextIOWrapper(bytes_io, encoding="utf-8")

    location = Location(
        coordinates=Coordinates(
            real_path=test_path,
            file_system_id=None,
            line=None,
        ),
        access_path=test_path,
        annotations={},
    )

    reader = LocationReadCloser(
        location=location,
        read_closer=text_io,
    )

    with patch("pefile.PE", side_effect=pefile.PEFormatError("Invalid PE file")):
        pkgs, relations = parse_dotnet_portable_executable(None, None, reader)
        assert pkgs == []
        assert relations == []


def test_parse_dotnet_portable_executable_no_version_resource(caplog: LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    test_path = "/test/path/file.dll"
    bytes_io = BytesIO(b"test content")
    text_io = TextIOWrapper(bytes_io, encoding="utf-8")

    location = Location(
        coordinates=Coordinates(
            real_path=test_path,
            file_system_id=None,
            line=None,
        ),
        access_path=test_path,
        annotations={},
    )

    reader = LocationReadCloser(
        location=location,
        read_closer=text_io,
    )

    mock_pe = MagicMock(spec=pefile.PE)
    with (
        patch("pefile.PE", return_value=mock_pe),
        patch(
            "labels.parsers.cataloger.dotnet.parse_dotnet_portable_executable.parse_version_resource",
            return_value=None,
        ),
    ):
        pkgs, relations = parse_dotnet_portable_executable(None, None, reader)
        assert pkgs == []
        assert relations == []
        assert (
            f"Unable to find version resource for portable executable in file {test_path}"
            in caplog.text
        )


def test_parse_dotnet_portable_executable_no_package(caplog: LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    test_path = "/test/path/file.dll"
    bytes_io = BytesIO(b"test content")
    text_io = TextIOWrapper(bytes_io, encoding="utf-8")

    location = Location(
        coordinates=Coordinates(
            real_path=test_path,
            file_system_id=None,
            line=None,
        ),
        access_path=test_path,
        annotations={},
    )

    reader = LocationReadCloser(
        location=location,
        read_closer=text_io,
    )

    mock_pe = MagicMock(spec=pefile.PE)
    with (
        patch("pefile.PE", return_value=mock_pe),
        patch(
            "labels.parsers.cataloger.dotnet.parse_dotnet_portable_executable.parse_version_resource",
            return_value={"ProductName": "TestApp"},
        ),
        patch(
            "labels.parsers.cataloger.dotnet.parse_dotnet_portable_executable.build_dot_net_package",
            return_value=None,
        ),
    ):
        pkgs, relations = parse_dotnet_portable_executable(None, None, reader)
        assert pkgs == []
        assert relations == []
        assert f"Unable to build package for portable executable in file {test_path}" in caplog.text
