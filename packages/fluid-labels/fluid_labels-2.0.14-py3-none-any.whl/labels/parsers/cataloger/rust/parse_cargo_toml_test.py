from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser
from labels.model.indexables import FileCoordinate, IndexedDict, ParsedValue, Position
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.rust import parse_cargo_toml as parse_cargo_toml_module
from labels.parsers.cataloger.rust.parse_cargo_toml import (
    _get_location,
    _get_packages,
    _get_version,
)
from labels.parsers.cataloger.rust.utils import package_url
from labels.testing.mocks import Mock, mocks
from labels.testing.utils import parametrize_sync
from labels.testing.utils.helpers import get_test_data_path


def test_parse_cargo_toml() -> None:
    test_data_path = get_test_data_path("dependencies/rust/Cargo.toml")
    expected = [
        Package(
            name="chrono",
            version="0.4",
            locations=[Location(access_path=test_data_path)],
            language=Language.RUST,
            licenses=[],
            p_url=package_url("chrono", "0.4"),
            type=PackageType.RustPkg,
        ),
        Package(
            name="futures",
            version="0.3",
            locations=[Location(access_path=test_data_path)],
            language=Language.RUST,
            licenses=[],
            p_url=package_url("futures", "0.3"),
            type=PackageType.RustPkg,
        ),
        Package(
            name="atk",
            version="^0",
            locations=[Location(access_path=test_data_path)],
            language=Language.RUST,
            licenses=[],
            p_url=package_url("atk", "^0"),
            type=PackageType.RustPkg,
        ),
        Package(
            name="glib-sys",
            version="^0",
            locations=[Location(access_path=test_data_path)],
            language=Language.RUST,
            licenses=[],
            p_url=package_url("glib-sys", "^0"),
            type=PackageType.RustPkg,
        ),
        Package(
            name="gobject-sys",
            version="^0",
            locations=[Location(access_path=test_data_path)],
            language=Language.RUST,
            licenses=[],
            p_url=package_url("gobject-sys", "^0"),
            type=PackageType.RustPkg,
        ),
        Package(
            name="glib",
            version="^0",
            locations=[Location(access_path=test_data_path)],
            language=Language.RUST,
            licenses=[],
            p_url=package_url("glib", "^0"),
            type=PackageType.RustPkg,
        ),
        Package(
            name="gio",
            version="^0",
            locations=[Location(access_path=test_data_path)],
            language=Language.RUST,
            licenses=[],
            p_url=package_url("gio", "^0"),
            type=PackageType.RustPkg,
        ),
        Package(
            name="gdk",
            version="^0",
            locations=[Location(access_path=test_data_path)],
            language=Language.RUST,
            licenses=[],
            p_url=package_url("gdk", "^0"),
            type=PackageType.RustPkg,
        ),
        Package(
            name="gdk-pixbuf",
            version="^0",
            locations=[Location(access_path=test_data_path)],
            language=Language.RUST,
            licenses=[],
            p_url=package_url("gdk-pixbuf", "^0"),
            type=PackageType.RustPkg,
        ),
        Package(
            name="gtk",
            version="^0",
            locations=[Location(access_path=test_data_path)],
            language=Language.RUST,
            licenses=[],
            p_url=package_url("gtk", "^0"),
            type=PackageType.RustPkg,
        ),
        Package(
            name="once_cell",
            version="^0",
            locations=[Location(access_path=test_data_path)],
            language=Language.RUST,
            licenses=[],
            p_url=package_url("once_cell", "^0"),
            type=PackageType.RustPkg,
        ),
        Package(
            name="pango",
            version="^0",
            locations=[Location(access_path=test_data_path)],
            language=Language.RUST,
            licenses=[],
            p_url=package_url("pango", "^0"),
            type=PackageType.RustPkg,
        ),
        Package(
            name="pangocairo",
            version="^0",
            locations=[Location(access_path=test_data_path)],
            language=Language.RUST,
            licenses=[],
            p_url=package_url("pangocairo", "^0"),
            type=PackageType.RustPkg,
        ),
        Package(
            name="cairo-rs",
            version="^0",
            locations=[Location(access_path=test_data_path)],
            language=Language.RUST,
            licenses=[],
            p_url=package_url("cairo-rs", "^0"),
            type=PackageType.RustPkg,
        ),
        Package(
            name="async-tls",
            version="0.6",
            locations=[Location(access_path=test_data_path)],
            language=Language.RUST,
            licenses=[],
            p_url=package_url("async-tls", "0.6"),
            type=PackageType.RustPkg,
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        location = Location(access_path=test_data_path)
        reader_obj = LocationReadCloser(location=location, read_closer=reader)
        pkgs, relationships = parse_cargo_toml_module.parse_cargo_toml(
            None,
            None,
            reader_obj,
        )
    assert pkgs == expected
    assert relationships == []


@parametrize_sync(
    args=["location", "sourceline", "esperado"],
    cases=[
        [
            Location(
                coordinates=Coordinates(real_path="/foo/bar", line=1),
                dependency_type=DependencyType.UNKNOWN,
            ),
            10,
            Location(
                coordinates=Coordinates(real_path="/foo/bar", line=10),
                dependency_type=DependencyType.DIRECT,
            ),
        ],
        [
            Location(
                access_path="/foo/bar",
                dependency_type=DependencyType.UNKNOWN,
            ),
            5,
            Location(
                access_path="/foo/bar",
                dependency_type=DependencyType.UNKNOWN,
            ),
        ],
    ],
)
def test_get_location(location: Location, sourceline: int, esperado: Location) -> None:
    resultado = _get_location(location, sourceline)
    assert resultado == esperado


@parametrize_sync(
    args=["valor", "esperado"],
    cases=[
        [
            "1.0.0",
            "1.0.0",
        ],
        [
            123,
            None,
        ],
    ],
)
def test_get_version_simple_values(valor: ParsedValue, esperado: str | None) -> None:
    resultado = _get_version(valor)
    assert resultado == esperado


def test_get_version_with_version() -> None:
    mock_position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=1),
    )
    indexed_dict: IndexedDict[str, ParsedValue] = IndexedDict()
    indexed_dict[("version", mock_position)] = ("2.0.0", mock_position)
    resultado = _get_version(indexed_dict)
    assert resultado == "2.0.0"


def test_get_version_with_git_and_branch() -> None:
    mock_position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=1),
    )
    indexed_dict: IndexedDict[str, ParsedValue] = IndexedDict()
    indexed_dict[("git", mock_position)] = ("https://github.com/user/repo", mock_position)
    indexed_dict[("branch", mock_position)] = ("main", mock_position)
    resultado = _get_version(indexed_dict)
    assert resultado == "https://github.com/user/repo@main"


def test_get_version_with_git_only() -> None:
    mock_position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=1),
    )
    indexed_dict: IndexedDict[str, ParsedValue] = IndexedDict()
    indexed_dict[("git", mock_position)] = ("https://github.com/user/repo", mock_position)
    resultado = _get_version(indexed_dict)
    assert resultado == ""


def test_get_version_empty_dict() -> None:
    indexed_dict: IndexedDict[str, ParsedValue] = IndexedDict()
    resultado = _get_version(indexed_dict)
    assert resultado == ""


def test_get_packages_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    mock_position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=1),
    )
    dependencies: IndexedDict[str, ParsedValue] = IndexedDict()
    dependencies[("test-pkg", mock_position)] = ("1.0.0", mock_position)

    location = Location(access_path="/test/Cargo.toml")
    bytes_io = BytesIO(b"")
    reader = LocationReadCloser(location=location, read_closer=TextIOWrapper(bytes_io))

    with patch("labels.model.package.Package.__init__") as mock_init:
        mock_init.side_effect = ValidationError.from_exception_data(
            title="",
            line_errors=[
                InitErrorDetails(  # type: ignore[misc]
                    type="missing",
                    loc=("name",),
                    input=None,
                    ctx={},
                ),
            ],
        )
        packages = _get_packages(reader, dependencies, is_dev=False)
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )
        assert packages == []


@mocks(
    mocks=[
        Mock(
            module=parse_cargo_toml_module,
            target="_get_version",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_packages_skip_invalid_version() -> None:
    mock_position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=1),
    )
    dependencies: IndexedDict[str, ParsedValue] = IndexedDict()
    dependencies[("test-pkg", mock_position)] = ("1.0.0", mock_position)

    location = Location(access_path="/test/Cargo.toml")
    bytes_io = BytesIO(b"")
    reader = LocationReadCloser(location=location, read_closer=TextIOWrapper(bytes_io))

    packages = _get_packages(reader, dependencies, is_dev=False)
    assert packages == []
