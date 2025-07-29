from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails
from tree_sitter import Node

from labels.model.file import Coordinates, Location, LocationReadCloser, Scope
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.python.parse_pipfile_lock import (
    _get_location,
    _get_packages,
    _get_version,
    parse_pipfile_lock_deps,
)
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_pip_file_lock() -> None:
    test_data_path = get_test_data_path("dependencies/python/pipfile-lock/Pipfile.lock")
    expected = [
        Package(
            name="aio-pika",
            version="6.8.0",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=24,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:pypi/aio-pika@6.8.0",
        ),
        Package(
            name="aiodns",
            version="2.0.0",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=32,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:pypi/aiodns@2.0.0",
        ),
        Package(
            name="aiohttp",
            version="3.7.4.post0",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=40,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:pypi/aiohttp@3.7.4.post0",
        ),
        Package(
            name="aiohttp-jinja2",
            version="1.4.2",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=48,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:pypi/aiohttp-jinja2@1.4.2",
        ),
        Package(
            name="astroid",
            version="2.5.2",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=58,
                    ),
                    scope=Scope.DEV,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
            metadata=None,
            p_url="pkg:pypi/astroid@2.5.2",
        ),
        Package(
            name="autopep8",
            version="1.5.6",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=65,
                    ),
                    scope=Scope.DEV,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
            metadata=None,
            p_url="pkg:pypi/autopep8@1.5.6",
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_pipfile_lock_deps(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        assert pkgs is not None
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
    assert pkgs == expected


def test_get_location() -> None:
    base_location = Location(
        coordinates=Coordinates(
            real_path="test/path",
            file_system_id=None,
            line=1,
        ),
        access_path="test/path",
        annotations={},
    )

    dev_location = _get_location(base_location, 10, is_dev=True)
    assert dev_location.scope == Scope.DEV
    assert dev_location.coordinates
    assert dev_location.coordinates.line == 10

    location_without_coords = Location(
        coordinates=None,
        access_path="test/path",
        annotations={},
    )
    result = _get_location(location_without_coords, 30, is_dev=True)
    assert result.scope == Scope.DEV
    assert result.coordinates is None


def test_get_version() -> None:
    mock_node = MagicMock(spec=Node)
    mock_node.start_point = (0, 0)
    mock_node.end_point = (0, 0)

    value = IndexedDict[str, ParsedValue](mock_node)
    value[("version", mock_node)] = ("=1.2.3", mock_node)
    assert _get_version(value) == "1.2.3"

    value = IndexedDict[str, ParsedValue](mock_node)
    value[("version", mock_node)] = ("~^>=1.2.3", mock_node)
    assert _get_version(value) == "1.2.3"

    value = IndexedDict[str, ParsedValue](mock_node)
    value[("version", mock_node)] = ("1.2.3", mock_node)
    assert _get_version(value) == "1.2.3"

    value = IndexedDict[str, ParsedValue](mock_node)
    value[("version", mock_node)] = (123, mock_node)
    assert _get_version(value) == ""

    value = IndexedDict[str, ParsedValue](mock_node)
    assert _get_version(value) == ""


def test_get_packages_with_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    mock_node = MagicMock(spec=Node)
    mock_node.start_point = (0, 0)
    mock_node.end_point = (0, 0)

    dummy_content = b'{"dummy": "content"}'
    reader = LocationReadCloser(
        location=new_location("test/path"),
        read_closer=TextIOWrapper(BytesIO(dummy_content)),
    )

    dependencies = IndexedDict[str, ParsedValue](mock_node)
    package_data = IndexedDict[str, ParsedValue](mock_node)
    package_data[("version", mock_node)] = ("1.2.3", mock_node)
    dependencies[("test-package", mock_node)] = (package_data, mock_node)

    with patch("labels.model.package.Package.__init__") as mock_init:
        mock_init.side_effect = ValidationError.from_exception_data(
            title="",
            line_errors=[
                InitErrorDetails(
                    type="missing",
                    loc=("name",),
                    input=None,
                    ctx={},
                ),
            ],
        )

        packages = _get_packages(reader, dependencies)
        assert packages == []
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


def test_get_packages_with_invalid_dependencies() -> None:
    mock_node = MagicMock(spec=Node)
    mock_node.start_point = (0, 0)
    mock_node.end_point = (0, 0)

    dummy_content = b'{"dummy": "content"}'
    reader = LocationReadCloser(
        location=new_location("test/path"),
        read_closer=TextIOWrapper(BytesIO(dummy_content)),
    )

    assert _get_packages(reader, None) == []

    assert _get_packages(reader, "not a dict") == []
    assert _get_packages(reader, 123) == []
    assert _get_packages(reader, []) == []


def test_get_packages_with_invalid_items() -> None:
    mock_node = MagicMock(spec=Node)
    mock_node.start_point = (0, 0)
    mock_node.end_point = (0, 0)

    dummy_content = b'{"dummy": "content"}'
    reader = LocationReadCloser(
        location=new_location("test/path"),
        read_closer=TextIOWrapper(BytesIO(dummy_content)),
    )

    dependencies = IndexedDict[str, ParsedValue](mock_node)

    dependencies[("test-package", mock_node)] = ("not a dict", mock_node)
    assert _get_packages(reader, dependencies) == []

    dependencies[("test-package", mock_node)] = (123, mock_node)
    assert _get_packages(reader, dependencies) == []

    dependencies[("test-package", mock_node)] = (["1", "2", "3"], mock_node)
    assert _get_packages(reader, dependencies) == []

    dependencies[("test-package", mock_node)] = (None, mock_node)
    assert _get_packages(reader, dependencies) == []


def test_get_packages_with_empty_name_or_version() -> None:
    mock_node = MagicMock(spec=Node)
    mock_node.start_point = (0, 0)
    mock_node.end_point = (0, 0)

    dummy_content = b'{"dummy": "content"}'
    reader = LocationReadCloser(
        location=new_location("test/path"),
        read_closer=TextIOWrapper(BytesIO(dummy_content)),
    )

    dependencies = IndexedDict[str, ParsedValue](mock_node)

    package_data = IndexedDict[str, ParsedValue](mock_node)
    package_data[("version", mock_node)] = ("1.2.3", mock_node)
    dependencies[("", mock_node)] = (package_data, mock_node)
    assert _get_packages(reader, dependencies) == []

    package_data = IndexedDict[str, ParsedValue](mock_node)
    package_data[("version", mock_node)] = ("", mock_node)
    dependencies[("test-package", mock_node)] = (package_data, mock_node)
    assert _get_packages(reader, dependencies) == []

    package_data = IndexedDict[str, ParsedValue](mock_node)
    package_data[("version", mock_node)] = (None, mock_node)
    dependencies[("test-package", mock_node)] = (package_data, mock_node)
    assert _get_packages(reader, dependencies) == []

    package_data = IndexedDict[str, ParsedValue](mock_node)
    package_data[("version", mock_node)] = (123, mock_node)
    dependencies[("test-package", mock_node)] = (package_data, mock_node)
    assert _get_packages(reader, dependencies) == []
