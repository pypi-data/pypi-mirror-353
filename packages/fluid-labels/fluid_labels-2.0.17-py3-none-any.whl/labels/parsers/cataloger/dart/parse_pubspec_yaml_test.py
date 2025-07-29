import logging
from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.dart.parse_pubspec_yaml import parse_pubspec_yaml
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location

LOGGER = logging.getLogger(__name__)


def test_parse_pubspec_yaml_with_valid_dependencies() -> None:
    test_data_path = get_test_data_path("dependencies/dart/pubspec.yaml")
    expected_packages = [
        Package(
            name="cupertino_icons",
            version="^1.0.2",
            language=Language.DART,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=14,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DartPubPkg,
            p_url="pkg:pub/cupertino_icons@%5E1.0.2",
        ),
        Package(
            name="flutter_svg",
            version="^1.0.0",
            language=Language.DART,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=15,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DartPubPkg,
            p_url="pkg:pub/flutter_svg@%5E1.0.0",
        ),
        Package(
            name="permission_handler",
            version="^10.1.0",
            language=Language.DART,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=16,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DartPubPkg,
            p_url="pkg:pub/permission_handler@%5E10.1.0",
        ),
        Package(
            name="flutter_styled_toast",
            version="^2.0.0",
            language=Language.DART,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=17,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DartPubPkg,
            p_url="pkg:pub/flutter_styled_toast@%5E2.0.0",
        ),
        Package(
            name="photo_view",
            version="^0.13.0",
            language=Language.DART,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=18,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DartPubPkg,
            p_url="pkg:pub/photo_view@%5E0.13.0",
        ),
        Package(
            name="event",
            version="^2.1.2",
            language=Language.DART,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=19,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DartPubPkg,
            p_url="pkg:pub/event@%5E2.1.2",
        ),
        Package(
            name="dio",
            version="4.0.0",
            language=Language.DART,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=20,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DartPubPkg,
            p_url="pkg:pub/dio@4.0.0",
        ),
        Package(
            name="modal_bottom_sheet",
            version="^2.0.0",
            language=Language.DART,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=21,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DartPubPkg,
            p_url="pkg:pub/modal_bottom_sheet@%5E2.0.0",
        ),
        Package(
            name="another_xlider",
            version="^1.0.1+2",
            language=Language.DART,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=22,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DartPubPkg,
            p_url="pkg:pub/another_xlider@%5E1.0.1%2B2",
        ),
        Package(
            name="scrollable_positioned_list",
            version="^0.2.3",
            language=Language.DART,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=23,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DartPubPkg,
            p_url="pkg:pub/scrollable_positioned_list@%5E0.2.3",
        ),
        Package(
            name="url_launcher",
            version="^6.0.20",
            language=Language.DART,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=24,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DartPubPkg,
            p_url="pkg:pub/url_launcher@%5E6.0.20",
        ),
        Package(
            name="clipboard",
            version="^0.1.3",
            language=Language.DART,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=25,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DartPubPkg,
            p_url="pkg:pub/clipboard@%5E0.1.3",
        ),
        Package(
            name="file_picker",
            version="5.2.1",
            language=Language.DART,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=26,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DartPubPkg,
            p_url="pkg:pub/file_picker@5.2.1",
        ),
        Package(
            name="filesystem_picker",
            version="^3.1.0",
            language=Language.DART,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=27,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DartPubPkg,
            p_url="pkg:pub/filesystem_picker@%5E3.1.0",
        ),
        Package(
            name="flutter_lints",
            version="^1.0.0",
            language=Language.DART,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.DEV,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=32,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DartPubPkg,
            p_url="pkg:pub/flutter_lints@%5E1.0.0",
        ),
        Package(
            name="http",
            version="^0.12.0",
            language=Language.DART,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.DEV,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=33,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DartPubPkg,
            p_url="pkg:pub/http@%5E0.12.0",
        ),
    ]

    with Path(test_data_path).open("rb") as f:
        content = f.read()
    reader = TextIOWrapper(BytesIO(content))
    pkgs, rels = parse_pubspec_yaml(
        None,
        None,
        LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
    )
    assert pkgs == expected_packages
    assert rels == []


def test_parse_pubspec_yaml_with_empty_content() -> None:
    yaml_content = ""
    expected_packages: list[Package] = []

    bytes_io = BytesIO(yaml_content.encode("utf-8"))
    reader = TextIOWrapper(bytes_io)
    pkgs, rels = parse_pubspec_yaml(
        None,
        None,
        LocationReadCloser(location=new_location("test.yaml"), read_closer=reader),
    )
    assert pkgs == expected_packages
    assert rels == []


def test_parse_pubspec_yaml_with_malformed_package(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)
    yaml_content = """
name: test
description: test app

dependencies:
  test_package: 1.0.0
"""
    bytes_io = BytesIO(yaml_content.encode("utf-8"))
    reader = TextIOWrapper(bytes_io)
    location = new_location("test.yaml")

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

        pkgs, rels = parse_pubspec_yaml(
            None,
            None,
            LocationReadCloser(location=location, read_closer=reader),
        )
        assert pkgs == []
        assert rels == []
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


def test_parse_pubspec_yaml_with_location_without_coordinates() -> None:
    yaml_content = """
name: test
description: test app

dependencies:
  test_package: 1.0.0
"""
    bytes_io = BytesIO(yaml_content.encode("utf-8"))
    reader = TextIOWrapper(bytes_io)
    location = new_location("test.yaml")
    location.coordinates = None

    pkgs, rels = parse_pubspec_yaml(
        None,
        None,
        LocationReadCloser(location=location, read_closer=reader),
    )
    assert len(pkgs) == 1
    assert pkgs[0].locations[0].coordinates is None
    assert pkgs[0].locations[0].scope == Scope.PROD
    assert rels == []
