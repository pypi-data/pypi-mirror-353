from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser
from labels.model.indexables import FileCoordinate, IndexedDict, Position
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.dart.parse_pubspec_lock import (
    DartPubspecLickEntry,
    get_hosted_url,
    get_vcs_url,
    package_url,
    parse_pubspec_lock,
)
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_pubspec_lock() -> None:
    test_data_path = get_test_data_path("dependencies/dart/pubspec.lock")
    expected_packages = [
        Package(
            name="ale",
            version="3.3.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=4,
                    ),
                    dependency_type=DependencyType.TRANSITIVE,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.DART,
            licenses=[],
            type=PackageType.DartPubPkg,
            metadata=DartPubspecLickEntry(name="ale", version="3.3.0", hosted_url="", vcs_url=""),
            p_url="pkg:pub/ale@3.3.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="analyzer",
            version="0.40.7",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=11,
                    ),
                    dependency_type=DependencyType.TRANSITIVE,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.DART,
            licenses=[],
            type=PackageType.DartPubPkg,
            metadata=DartPubspecLickEntry(
                name="analyzer",
                version="0.40.7",
                hosted_url="",
                vcs_url="",
            ),
            p_url="pkg:pub/analyzer@0.40.7",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="ansicolor",
            version="1.1.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=18,
                    ),
                    dependency_type=DependencyType.TRANSITIVE,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.DART,
            licenses=[],
            type=PackageType.DartPubPkg,
            metadata=DartPubspecLickEntry(
                name="ansicolor",
                version="1.1.1",
                hosted_url="",
                vcs_url="",
            ),
            p_url="pkg:pub/ansicolor@1.1.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="archive",
            version="2.0.13",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=25,
                    ),
                    dependency_type=DependencyType.TRANSITIVE,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.DART,
            licenses=[],
            type=PackageType.DartPubPkg,
            metadata=DartPubspecLickEntry(
                name="archive",
                version="2.0.13",
                hosted_url="",
                vcs_url="",
            ),
            p_url="pkg:pub/archive@2.0.13",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="args",
            version="1.6.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=32,
                    ),
                    dependency_type=DependencyType.TRANSITIVE,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.DART,
            licenses=[],
            type=PackageType.DartPubPkg,
            metadata=DartPubspecLickEntry(name="args", version="1.6.0", hosted_url="", vcs_url=""),
            p_url="pkg:pub/args@1.6.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="flutter",
            version="0.0.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=39,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.DART,
            licenses=[],
            type=PackageType.DartPubPkg,
            metadata=DartPubspecLickEntry(
                name="flutter",
                version="0.0.0",
                hosted_url="",
                vcs_url="",
            ),
            p_url="pkg:pub/flutter@0.0.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="key_binder",
            version="1.11.20",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=44,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.DART,
            licenses=[],
            type=PackageType.DartPubPkg,
            metadata=DartPubspecLickEntry(
                name="key_binder",
                version="1.11.20",
                hosted_url="",
                vcs_url=(
                    "git@github.com:Workiva/key_binder.git"
                    "@3f7b3a6350e73c7dcac45301c0e18fbd42af02f7"
                ),
            ),
            p_url=(
                "pkg:pub/key_binder@1.11.20?vcs_url"
                "=git%40github.com:Workiva"
                "/key_binder.git%403f7b3a6350e73c7dcac45301c0e18fbd42af02f7"
            ),
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_pubspec_lock(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
        assert pkgs == expected_packages


def test_get_hosted_url_hosted_custom_url() -> None:
    entry: IndexedDict[str, str | dict[str, str]] = IndexedDict()
    key_pos: Position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=6),
    )
    value_pos: Position = Position(
        start=FileCoordinate(line=1, column=8),
        end=FileCoordinate(line=1, column=13),
    )
    entry[("hosted", key_pos)] = ("hosted", value_pos)
    entry[("description", key_pos)] = ({"url": "https://custom-pub.dev"}, value_pos)
    assert get_hosted_url(entry) == "custom-pub.dev"


def test_get_hosted_url_invalid_url() -> None:
    entry: IndexedDict[str, str | dict[str, str]] = IndexedDict()
    key_pos: Position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=6),
    )
    value_pos: Position = Position(
        start=FileCoordinate(line=1, column=8),
        end=FileCoordinate(line=1, column=13),
    )
    entry[("hosted", key_pos)] = ("hosted", value_pos)
    entry[("description", key_pos)] = ({"url": ""}, value_pos)
    assert get_hosted_url(entry) == ""


def test_get_vcs_url_with_path() -> None:
    entry: IndexedDict[str, str | dict[str, str]] = IndexedDict()
    key_pos: Position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=6),
    )
    value_pos: Position = Position(
        start=FileCoordinate(line=1, column=8),
        end=FileCoordinate(line=1, column=13),
    )
    entry[("source", key_pos)] = ("git", value_pos)
    entry[("description", key_pos)] = (
        {
            "url": "https://github.com/example/repo",
            "resolved-ref": "abc123",
            "path": "subdir",
        },
        value_pos,
    )
    assert get_vcs_url(entry) == "https://github.com/example/repo@abc123#subdir"


def test_package_url_with_hosted_url() -> None:
    entry = DartPubspecLickEntry(
        name="test_package",
        version="1.0.0",
        hosted_url="custom-pub.dev",
        vcs_url="",
    )
    assert package_url(entry) == "pkg:pub/test_package@1.0.0?hosted_url=custom-pub.dev"


def test_parse_pubspec_lock_with_non_string_version() -> None:
    entry: IndexedDict[str, str | dict[str, str]] = IndexedDict()
    key_pos: Position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=6),
    )
    value_pos: Position = Position(
        start=FileCoordinate(line=1, column=8),
        end=FileCoordinate(line=1, column=13),
    )

    entry[("name", key_pos)] = ("test_package", value_pos)
    entry[("version", key_pos)] = ({"invalid": "version"}, value_pos)

    yaml_content = b"""packages:
  test_package:
    name: test_package
    version: {"invalid": "version"}
    source: hosted
    description:
      url: https://pub.dev
"""
    content = TextIOWrapper(BytesIO(yaml_content))

    pkgs, _ = parse_pubspec_lock(
        None,
        None,
        LocationReadCloser(location=new_location("./pubspec.lock"), read_closer=content),
    )
    assert not any(pkg.name == "test_package" for pkg in pkgs)


def test_parse_pubspec_lock_without_coordinates() -> None:
    yaml_content = b"""packages:
  test_package:
    name: test_package
    version: 1.0.0
    source: hosted
    description:
      url: https://pub.dev
"""
    content = TextIOWrapper(BytesIO(yaml_content))

    location = new_location("./pubspec.lock")
    location.coordinates = None

    pkgs, _ = parse_pubspec_lock(
        None,
        None,
        LocationReadCloser(location=location, read_closer=content),
    )

    assert len(pkgs) == 1
    assert pkgs[0].name == "test_package"
    assert pkgs[0].version == "1.0.0"
    assert pkgs[0].locations[0].coordinates is None


def test_parse_pubspec_lock_malformed_warning(caplog: pytest.LogCaptureFixture) -> None:
    yaml_content = b"""packages:
  test_package:
    name: test_package
    version: 1.0.0
    source: hosted
    description:
      url: https://pub.dev
"""
    content = TextIOWrapper(BytesIO(yaml_content))

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

        pkgs, _ = parse_pubspec_lock(
            None,
            None,
            LocationReadCloser(location=new_location("./pubspec.lock"), read_closer=content),
        )

        assert len(pkgs) == 0
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )
