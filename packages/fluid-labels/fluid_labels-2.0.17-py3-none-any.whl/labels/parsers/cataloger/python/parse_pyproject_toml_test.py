from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.python.parse_pyproject_toml import (
    _get_location,
    _get_packages,
    _get_version,
    parse_pyproject_toml,
)
from labels.parsers.collection.toml import parse_toml_with_tree_sitter
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_pyproject_file() -> None:
    test_data_path = get_test_data_path("dependencies/python/poetry/pyproject.toml")
    expected = [
        Package(
            name="python",
            version="^3.11",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=9,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:pypi/python@%5E3.11",
        ),
        Package(
            name="apkid",
            version=">2.1.5",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=10,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:pypi/apkid@%3E2.1.5",
        ),
        Package(
            name="python-json-logger",
            version="<3.3.0",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.DEV,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=14,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:pypi/python-json-logger@%3C3.3.0",
        ),
        Package(
            name="numpy",
            version=">=1.21,<1.26",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.DEV,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=17,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:pypi/numpy@%3E%3D1.21%2C%3C1.26",
        ),
    ]

    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_pyproject_toml(
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
    test_data_path = "./pyproject.toml"
    base_location = Location(
        scope=Scope.PROD,
        coordinates=Coordinates(
            real_path=test_data_path,
            file_system_id=None,
            line=1,
        ),
        access_path=test_data_path,
        annotations={},
        dependency_type=DependencyType.DIRECT,
        reachable_cves=[],
    )

    result = _get_location(base_location, 10, Scope.DEV)
    assert result.scope == Scope.DEV
    assert result.coordinates is not None
    assert result.coordinates.line == 10
    assert result.dependency_type == DependencyType.DIRECT

    location_sin_coords = Location(
        scope=Scope.PROD,
        coordinates=None,
        access_path=test_data_path,
        annotations={},
        dependency_type=DependencyType.DIRECT,
        reachable_cves=[],
    )
    result_sin_coords = _get_location(location_sin_coords, 10, Scope.DEV)
    assert result_sin_coords.scope == Scope.DEV
    assert result_sin_coords.coordinates is None


def test_get_version() -> None:
    assert _get_version("1.2.3") == "1.2.3"

    toml_content = 'version = "2.0.0"'
    parsed = parse_toml_with_tree_sitter(toml_content)
    version_dict = parsed
    assert _get_version(version_dict) == "2.0.0"

    empty_toml = ""
    parsed_empty = parse_toml_with_tree_sitter(empty_toml)
    empty_dict = parsed_empty
    assert _get_version(empty_dict) == ""

    assert _get_version(123) is None


def test_get_packages_skip_invalid() -> None:
    test_data_path = "./pyproject.toml"
    reader = LocationReadCloser(
        location=new_location(test_data_path),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    empty_name_dict = parse_toml_with_tree_sitter('"" = "1.0.0"')
    packages_empty_name = _get_packages(reader, empty_name_dict)
    assert len(packages_empty_name) == 0

    empty_version_dict = parse_toml_with_tree_sitter('package = ""')
    packages_empty_version = _get_packages(reader, empty_version_dict)
    assert len(packages_empty_version) == 0

    none_version_dict = parse_toml_with_tree_sitter("package = null")
    packages_none_version = _get_packages(reader, none_version_dict)
    assert len(packages_none_version) == 0


async def test_get_packages_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    test_data_path = "./pyproject.toml"
    reader = LocationReadCloser(
        location=new_location(test_data_path),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    valid_dict = parse_toml_with_tree_sitter('package = "1.0.0"')

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

        packages = _get_packages(reader, valid_dict)
        assert len(packages) == 0
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


def test_parse_pyproject_toml_invalid_tool() -> None:
    test_data_path = "./pyproject.toml"

    content = 'tool = "invalid"'
    reader = LocationReadCloser(
        location=new_location(test_data_path),
        read_closer=TextIOWrapper(BytesIO(content.encode())),
    )
    packages, relationships = parse_pyproject_toml(None, None, reader)
    assert len(packages) == 0
    assert len(relationships) == 0

    content = "tool = null"
    reader = LocationReadCloser(
        location=new_location(test_data_path),
        read_closer=TextIOWrapper(BytesIO(content.encode())),
    )
    packages, relationships = parse_pyproject_toml(None, None, reader)
    assert len(packages) == 0
    assert len(relationships) == 0


def test_parse_pyproject_toml_invalid_poetry() -> None:
    test_data_path = "./pyproject.toml"

    content = """
    [tool]
    poetry = "invalid"
    """
    reader = LocationReadCloser(
        location=new_location(test_data_path),
        read_closer=TextIOWrapper(BytesIO(content.encode())),
    )
    packages, relationships = parse_pyproject_toml(None, None, reader)
    assert len(packages) == 0
    assert len(relationships) == 0

    content = """
    [tool]
    poetry = null
    """
    reader = LocationReadCloser(
        location=new_location(test_data_path),
        read_closer=TextIOWrapper(BytesIO(content.encode())),
    )
    packages, relationships = parse_pyproject_toml(None, None, reader)
    assert len(packages) == 0
    assert len(relationships) == 0


def test_parse_pyproject_toml_invalid_dependencies() -> None:
    test_data_path = "./pyproject.toml"

    content = """
    [tool.poetry]
    dependencies = "invalid"
    """
    reader = LocationReadCloser(
        location=new_location(test_data_path),
        read_closer=TextIOWrapper(BytesIO(content.encode())),
    )
    packages, relationships = parse_pyproject_toml(None, None, reader)
    assert len(packages) == 0
    assert len(relationships) == 0

    content = """
    [tool.poetry]
    dependencies = null
    """
    reader = LocationReadCloser(
        location=new_location(test_data_path),
        read_closer=TextIOWrapper(BytesIO(content.encode())),
    )
    packages, relationships = parse_pyproject_toml(None, None, reader)
    assert len(packages) == 0
    assert len(relationships) == 0


def test_parse_pyproject_toml_invalid_dev() -> None:
    test_data_path = "./pyproject.toml"

    content = """
    [tool.poetry]
    dependencies = { python = "^3.11" }
    [tool.poetry.group]
    dev = "invalid"
    """
    reader = LocationReadCloser(
        location=new_location(test_data_path),
        read_closer=TextIOWrapper(BytesIO(content.encode())),
    )
    packages, relationships = parse_pyproject_toml(None, None, reader)
    assert len(packages) == 1
    assert len(relationships) == 0


def test_parse_pyproject_toml_invalid_dev_dependencies() -> None:
    test_data_path = "./pyproject.toml"

    content = """
    [tool.poetry]
    dependencies = { python = "^3.11" }
    [tool.poetry.group]
    [tool.poetry.group.dev]
    dependencies = "invalid"
    """
    reader = LocationReadCloser(
        location=new_location(test_data_path),
        read_closer=TextIOWrapper(BytesIO(content.encode())),
    )
    packages, relationships = parse_pyproject_toml(None, None, reader)
    assert len(packages) == 1
    assert len(relationships) == 0


def test_parse_pyproject_toml_valid_dev_dependencies() -> None:
    test_data_path = "./pyproject.toml"

    content = """
    [tool.poetry]
    dependencies = { python = "^3.11" }
    [tool.poetry.group]
    [tool.poetry.group.dev]
    dependencies = { pytest = "^7.0.0" }
    """
    reader = LocationReadCloser(
        location=new_location(test_data_path),
        read_closer=TextIOWrapper(BytesIO(content.encode())),
    )
    packages, relationships = parse_pyproject_toml(None, None, reader)
    assert len(packages) == 2
    assert len(relationships) == 0
    assert any(pkg.name == "pytest" and pkg.locations[0].scope == Scope.DEV for pkg in packages)


def test_parse_pyproject_toml_no_group() -> None:
    test_data_path = "./pyproject.toml"

    content = """
    [tool.poetry]
    dependencies = { python = "^3.11" }
    """
    reader = LocationReadCloser(
        location=new_location(test_data_path),
        read_closer=TextIOWrapper(BytesIO(content.encode())),
    )
    packages, relationships = parse_pyproject_toml(None, None, reader)
    assert len(packages) == 1
    assert len(relationships) == 0
    assert packages[0].name == "python"
    assert packages[0].locations[0].scope == Scope.PROD
