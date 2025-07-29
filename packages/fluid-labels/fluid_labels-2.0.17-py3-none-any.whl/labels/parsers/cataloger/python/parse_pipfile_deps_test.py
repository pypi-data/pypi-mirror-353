from io import BytesIO, TextIOWrapper
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.indexables import FileCoordinate, IndexedDict, ParsedValue, Position
from labels.parsers.cataloger.python.parse_pipfile_deps import (
    _get_location,
    _get_packages,
    parse_pipfile_deps,
)


def test_get_location_with_coordinates() -> None:
    original_location = Location(
        coordinates=Coordinates(
            real_path="/test/path",
            file_system_id=None,
            line=1,
        ),
        dependency_type=DependencyType.DIRECT,
        access_path="/test/path",
        annotations={},
        scope=Scope.PROD,
    )

    result = _get_location(original_location, 42, Scope.DEV)

    assert result.scope == Scope.DEV
    assert result.dependency_type == DependencyType.DIRECT
    assert result.coordinates is not None
    assert result.coordinates.line == 42
    assert result.coordinates.real_path == "/test/path"


def test_get_location_without_coordinates() -> None:
    original_location = Location(
        coordinates=None,
        dependency_type=DependencyType.DIRECT,
        access_path="/test/path",
        annotations={},
        scope=Scope.PROD,
    )

    result = _get_location(original_location, 42, Scope.DEV)

    assert result.scope == Scope.DEV
    assert result.dependency_type == DependencyType.DIRECT
    assert result.coordinates is None
    assert result.access_path == "/test/path"


def test_get_location_preserves_other_attributes() -> None:
    original_location = Location(
        coordinates=Coordinates(
            real_path="/test/path",
            file_system_id="123",
            line=1,
        ),
        dependency_type=DependencyType.DIRECT,
        access_path="/test/path",
        annotations={"key": "value"},
        scope=Scope.PROD,
    )

    result = _get_location(original_location, 42, Scope.DEV)

    assert result.scope == Scope.DEV
    assert result.dependency_type == DependencyType.DIRECT
    assert result.coordinates is not None
    assert result.coordinates.line == 42
    assert result.coordinates.real_path == "/test/path"
    assert result.coordinates.file_system_id == "123"
    assert result.annotations == {"key": "value"}


def test_get_packages_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    location = Location(access_path="/test/Pipfile")
    bytes_io = BytesIO(b"")
    reader = LocationReadCloser(location=location, read_closer=TextIOWrapper(bytes_io))

    toml_packages = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=1),
    )
    toml_packages[("test-package", position)] = ("1.0.0", position)

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

        packages = _get_packages(reader, toml_packages, is_dev=False)
        assert packages == []
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


def test_parse_pipfile_deps_invalid_toml_packages() -> None:
    location = Location(access_path="/test/Pipfile")
    bytes_io = BytesIO(b"")
    reader = LocationReadCloser(location=location, read_closer=TextIOWrapper(bytes_io))

    with patch("labels.parsers.collection.toml.parse_toml_with_tree_sitter") as mock_parse:
        mock_parse.return_value = {"packages": "invalid_type"}
        packages, relationships = parse_pipfile_deps(None, None, reader)
        assert packages == []
        assert relationships == []


def test_parse_pipfile_deps_invalid_dev_deps() -> None:
    location = Location(access_path="/test/Pipfile")
    bytes_io = BytesIO(b"")
    reader = LocationReadCloser(location=location, read_closer=TextIOWrapper(bytes_io))

    toml_packages = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=1),
    )
    toml_packages[("test-package", position)] = ("1.0.0", position)

    with patch("labels.parsers.collection.toml.parse_toml_with_tree_sitter") as mock_parse:
        mock_parse.return_value = {
            "packages": toml_packages,
            "dev-packages": "invalid_type",
        }
        packages, relationships = parse_pipfile_deps(None, None, reader)
        assert len(packages) == 1
        assert relationships == []
