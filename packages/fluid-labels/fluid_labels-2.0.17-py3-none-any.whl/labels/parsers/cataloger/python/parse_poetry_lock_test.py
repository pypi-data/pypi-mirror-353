from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, Location, LocationReadCloser
from labels.model.indexables import IndexedDict, IndexedList, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.python.model import PythonRequirementsEntry
from labels.parsers.cataloger.python.parse_poetry_lock import (
    _get_dependencies,
    _get_location,
    _parse_packages,
    _parse_relationships,
    parse_poetry_lock,
)
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_poetry_lock_file() -> None:
    test_data_path = get_test_data_path("dependencies/python/poetry/poetry.lock")
    expected = [
        Package(
            name="apkid",
            version="3.0.0",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=5,
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
            metadata=PythonRequirementsEntry(
                name="apkid",
                extras=[],
                markers="pkg:pypi/apkid@3.0.0",
                version_constraint=None,
            ),
            p_url="pkg:pypi/apkid@3.0.0",
        ),
        Package(
            name="python-json-logger",
            version="3.2.1",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=23,
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
            metadata=PythonRequirementsEntry(
                name="python-json-logger",
                extras=[],
                markers="pkg:pypi/python-json-logger@3.2.1",
                version_constraint=None,
            ),
            p_url="pkg:pypi/python-json-logger@3.2.1",
        ),
        Package(
            name="yara-python-dex",
            version="1.0.7",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=37,
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
            metadata=PythonRequirementsEntry(
                name="yara-python-dex",
                extras=[],
                markers="pkg:pypi/yara-python-dex@1.0.7",
                version_constraint=None,
            ),
            p_url="pkg:pypi/yara-python-dex@1.0.7",
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_poetry_lock(
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
    test_path = "/test/path/file.txt"

    location_with_coords = Location(
        coordinates=Coordinates(
            real_path=test_path,
            file_system_id=None,
            line=1,
        ),
        access_path=test_path,
        annotations={},
    )
    updated_location = _get_location(location_with_coords, 5)

    assert updated_location.coordinates is not None
    assert updated_location.coordinates.line == 5
    assert updated_location.coordinates.real_path == test_path

    location_without_coords = Location(
        coordinates=None,
        access_path=test_path,
        annotations={},
    )
    unchanged_location = _get_location(location_without_coords, 5)

    assert unchanged_location.coordinates is None
    assert unchanged_location.access_path == test_path


def test_parse_packages_with_invalid_toml_pkgs() -> None:
    mock_node = MagicMock()
    toml_content: IndexedDict[str, ParsedValue] = IndexedDict(mock_node)
    package_dict: IndexedDict[str, ParsedValue] = IndexedDict(mock_node)
    toml_content[("package", mock_node)] = (package_dict, mock_node)

    reader = LocationReadCloser(
        location=new_location("/test/path/file.txt"),
        read_closer=TextIOWrapper(BytesIO(b"test content")),
    )

    result = _parse_packages(toml_content, reader)

    assert result == []


def test_parse_packages_with_invalid_package_type() -> None:
    mock_node = MagicMock()
    toml_content: IndexedDict[str, ParsedValue] = IndexedDict(mock_node)
    packages_list: IndexedList[ParsedValue] = IndexedList(mock_node)
    packages_list.append(("invalid_package", mock_node))
    toml_content[("package", mock_node)] = (packages_list, mock_node)

    reader = LocationReadCloser(
        location=new_location("/test/path/file.txt"),
        read_closer=TextIOWrapper(BytesIO(b"test content")),
    )

    result = _parse_packages(toml_content, reader)

    assert result == []


def test_parse_packages_with_missing_name_or_version() -> None:
    mock_node = MagicMock()

    toml_content: IndexedDict[str, ParsedValue] = IndexedDict(mock_node)
    packages_list: IndexedList[ParsedValue] = IndexedList(mock_node)
    package1: IndexedDict[str, ParsedValue] = IndexedDict(mock_node)
    package1[("name", mock_node)] = ("", mock_node)
    package1[("version", mock_node)] = ("1.0.0", mock_node)
    package2: IndexedDict[str, ParsedValue] = IndexedDict(mock_node)
    package2[("name", mock_node)] = ("test-package", mock_node)
    package2[("version", mock_node)] = ("", mock_node)
    package3: IndexedDict[str, ParsedValue] = IndexedDict(mock_node)
    packages_list.append((package1, mock_node))
    packages_list.append((package2, mock_node))
    packages_list.append((package3, mock_node))
    toml_content[("package", mock_node)] = (packages_list, mock_node)

    reader = LocationReadCloser(
        location=new_location("/test/path/file.txt"),
        read_closer=TextIOWrapper(BytesIO(b"test content")),
    )

    result = _parse_packages(toml_content, reader)

    assert result == []


def test_parse_packages_with_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    mock_node = MagicMock()
    toml_content: IndexedDict[str, ParsedValue] = IndexedDict(mock_node)
    packages_list: IndexedList[ParsedValue] = IndexedList(mock_node)

    package: IndexedDict[str, ParsedValue] = IndexedDict(mock_node)
    package[("name", mock_node)] = ("test-package", mock_node)
    package[("version", mock_node)] = ("1.0.0", mock_node)

    packages_list.append((package, mock_node))
    toml_content[("package", mock_node)] = (packages_list, mock_node)

    reader = LocationReadCloser(
        location=new_location("/test/path/file.txt"),
        read_closer=TextIOWrapper(BytesIO(b"test content")),
    )

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

        result = _parse_packages(toml_content, reader)
        assert result == []
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


def test_get_dependencies_with_invalid_package_type() -> None:
    packages = [
        Package(
            name="test-package",
            version="1.0.0",
            language=Language.PYTHON,
            licenses=[],
            locations=[Location()],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PythonRequirementsEntry(
                name="test-package",
                extras=[],
                markers="pkg:pypi/test-package@1.0.0",
                version_constraint=None,
            ),
            p_url="pkg:pypi/test-package@1.0.0",
        ),
    ]

    result = _get_dependencies("not_an_indexed_dict", packages)
    assert result is None


def test_parse_relationships_with_invalid_toml_pkgs() -> None:
    mock_node = MagicMock()
    toml_content: IndexedDict[str, ParsedValue] = IndexedDict(mock_node)
    toml_content[("package", mock_node)] = (IndexedDict(mock_node), mock_node)

    packages = [
        Package(
            name="test-package",
            version="1.0.0",
            language=Language.PYTHON,
            licenses=[],
            locations=[Location()],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PythonRequirementsEntry(
                name="test-package",
                extras=[],
                markers="pkg:pypi/test-package@1.0.0",
                version_constraint=None,
            ),
            p_url="pkg:pypi/test-package@1.0.0",
        ),
    ]

    result = _parse_relationships(toml_content, packages)
    assert result == []


def test_parse_relationships_with_no_dependencies() -> None:
    mock_node = MagicMock()
    toml_content: IndexedDict[str, ParsedValue] = IndexedDict(mock_node)
    packages_list: IndexedList[ParsedValue] = IndexedList(mock_node)

    package: IndexedDict[str, ParsedValue] = IndexedDict(mock_node)
    package[("name", mock_node)] = ("test-package", mock_node)
    package[("version", mock_node)] = ("1.0.0", mock_node)
    package[("dependencies", mock_node)] = (IndexedDict(mock_node), mock_node)

    packages_list.append((package, mock_node))
    toml_content[("package", mock_node)] = (packages_list, mock_node)

    packages = [
        Package(
            name="different-package",
            version="1.0.0",
            language=Language.PYTHON,
            licenses=[],
            locations=[Location()],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PythonRequirementsEntry(
                name="different-package",
                extras=[],
                markers="pkg:pypi/different-package@1.0.0",
                version_constraint=None,
            ),
            p_url="pkg:pypi/different-package@1.0.0",
        ),
    ]

    result = _parse_relationships(toml_content, packages)
    assert result == []


def test_parse_relationships_with_missing_dependency() -> None:
    mock_node = MagicMock()
    toml_content: IndexedDict[str, ParsedValue] = IndexedDict(mock_node)
    packages_list: IndexedList[ParsedValue] = IndexedList(mock_node)

    package: IndexedDict[str, ParsedValue] = IndexedDict(mock_node)
    package[("name", mock_node)] = ("test-package", mock_node)
    package[("version", mock_node)] = ("1.0.0", mock_node)

    dependencies: IndexedDict[str, ParsedValue] = IndexedDict(mock_node)
    dependencies[("missing-dep", mock_node)] = ("*", mock_node)
    package[("dependencies", mock_node)] = (dependencies, mock_node)

    packages_list.append((package, mock_node))
    toml_content[("package", mock_node)] = (packages_list, mock_node)

    packages = [
        Package(
            name="test-package",
            version="1.0.0",
            language=Language.PYTHON,
            licenses=[],
            locations=[Location()],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PythonRequirementsEntry(
                name="test-package",
                extras=[],
                markers="pkg:pypi/test-package@1.0.0",
                version_constraint=None,
            ),
            p_url="pkg:pypi/test-package@1.0.0",
        ),
    ]

    result = _parse_relationships(toml_content, packages)
    assert result == []
