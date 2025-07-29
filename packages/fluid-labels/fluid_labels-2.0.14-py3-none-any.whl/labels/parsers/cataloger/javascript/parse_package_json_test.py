import logging
from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

import labels.parsers.cataloger.javascript.parse_package_json
from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.indexables import FileCoordinate, IndexedDict, ParsedValue, Position
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.javascript.model import NpmPackage
from labels.parsers.cataloger.javascript.parse_package_json import (
    _create_package,
    parse_package_json,
)
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_package_json() -> None:
    test_data_path = get_test_data_path("dependencies/javascript/pkg-json/package.json")
    expected_packages = [
        Package(
            name="JSONStream",
            version="^1.3.5",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=139,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="JSONStream",
                version="^1.3.5",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=False,
            ),
            p_url="pkg:npm/JSONStream@%5E1.3.5",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="abbrev",
            version="~1.1.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=140,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="abbrev",
                version="~1.1.1",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=False,
            ),
            p_url="pkg:npm/abbrev@~1.1.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="ansicolors",
            version="~0.3.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=141,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="ansicolors",
                version="~0.3.2",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=False,
            ),
            p_url="pkg:npm/ansicolors@~0.3.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="ansistyles",
            version="~0.1.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=142,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="ansistyles",
                version="~0.1.3",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=False,
            ),
            p_url="pkg:npm/ansistyles@~0.1.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="aproba",
            version="^2.0.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=143,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="aproba",
                version="^2.0.0",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=False,
            ),
            p_url="pkg:npm/aproba@%5E2.0.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="archy",
            version="~1.0.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=144,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="archy",
                version="~1.0.0",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=False,
            ),
            p_url="pkg:npm/archy@~1.0.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="bin-links",
            version="^1.1.7",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=145,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="bin-links",
                version="^1.1.7",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=False,
            ),
            p_url="pkg:npm/bin-links@%5E1.1.7",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="bluebird",
            version="^3.5.5",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=146,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="bluebird",
                version="^3.5.5",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=False,
            ),
            p_url="pkg:npm/bluebird@%5E3.5.5",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="byte-size",
            version="^5.0.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=147,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="byte-size",
                version="^5.0.1",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=False,
            ),
            p_url="pkg:npm/byte-size@%5E5.0.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="cacache",
            version="^12.0.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=148,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="cacache",
                version="^12.0.3",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=False,
            ),
            p_url="pkg:npm/cacache@%5E12.0.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="call-limit",
            version="^1.1.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=149,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="call-limit",
                version="^1.1.1",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=False,
            ),
            p_url="pkg:npm/call-limit@%5E1.1.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="chownr",
            version="^1.1.4",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=150,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="chownr",
                version="^1.1.4",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=False,
            ),
            p_url="pkg:npm/chownr@%5E1.1.4",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="ci-info",
            version="^2.0.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=151,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="ci-info",
                version="^2.0.0",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=False,
            ),
            p_url="pkg:npm/ci-info@%5E2.0.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="cli-columns",
            version="^3.1.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=152,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="cli-columns",
                version="^3.1.2",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=False,
            ),
            p_url="pkg:npm/cli-columns@%5E3.1.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="fs-vacuum",
            version="~1.2.10",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=153,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="fs-vacuum",
                version="~1.2.10",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=False,
            ),
            p_url="pkg:npm/fs-vacuum@~1.2.10",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="deep-equal",
            version="^1.0.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=157,
                    ),
                    scope=Scope.DEV,
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="deep-equal",
                version="^1.0.1",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=True,
            ),
            p_url="pkg:npm/deep-equal@%5E1.0.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
        ),
        Package(
            name="get-stream",
            version="^4.1.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=158,
                    ),
                    scope=Scope.DEV,
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="get-stream",
                version="^4.1.0",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=True,
            ),
            p_url="pkg:npm/get-stream@%5E4.1.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
        ),
        Package(
            name="licensee",
            version="^7.0.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=159,
                    ),
                    scope=Scope.DEV,
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="licensee",
                version="^7.0.3",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=True,
            ),
            p_url="pkg:npm/licensee@%5E7.0.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
        ),
        Package(
            name="marked",
            version="^0.6.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=160,
                    ),
                    scope=Scope.DEV,
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="marked",
                version="^0.6.3",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=True,
            ),
            p_url="pkg:npm/marked@%5E0.6.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
        ),
        Package(
            name="marked-man",
            version="^0.6.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=161,
                    ),
                    scope=Scope.DEV,
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackage(
                name="marked-man",
                version="^0.6.0",
                author=None,
                homepage=None,
                description=None,
                url=None,
                private=None,
                is_dev=True,
            ),
            p_url="pkg:npm/marked-man@%5E0.6.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
        ),
    ]
    with Path(test_data_path).open(
        encoding="utf-8",
    ) as reader:
        pkgs, _ = parse_package_json(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
    for pkg in pkgs:
        pkg.health_metadata = None
        pkg.licenses = []
    assert pkgs == expected_packages


def test_create_package_without_coordinates() -> None:
    reader = LocationReadCloser(
        location=Location(
            coordinates=None,
            scope=Scope.PROD,
            access_path="test/path",
            annotations={},
            dependency_type=DependencyType.DIRECT,
        ),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    package_json = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    dependencies = IndexedDict[str, ParsedValue]()
    dependencies[("test-package", position)] = ("1.0.0", position)
    package_json[("dependencies", position)] = (dependencies, position)

    package = _create_package(package_json, reader, "test-package", "1.0.0", is_dev=False)

    assert package is not None
    assert package.name == "test-package"
    assert package.version == "1.0.0"
    assert package.locations[0].coordinates is None
    assert package.locations[0].dependency_type == DependencyType.DIRECT
    assert package.locations[0].scope == Scope.PROD


def test_create_package_malformed_warning(caplog: pytest.LogCaptureFixture) -> None:
    reader = LocationReadCloser(
        location=Location(
            coordinates=None,
            scope=Scope.PROD,
            access_path="test/path",
            annotations={},
            dependency_type=DependencyType.DIRECT,
        ),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    package_json = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    dependencies = IndexedDict[str, ParsedValue]()
    dependencies[("test-package", position)] = ("1.0.0", position)
    package_json[("dependencies", position)] = (dependencies, position)

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

        package = _create_package(package_json, reader, "test-package", "1.0.0", is_dev=False)
        assert package is None
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


def test_parse_package_json_no_deps_warning(caplog: pytest.LogCaptureFixture) -> None:
    json_str = '{"dependencies": ["not-a-dict"]}'
    reader = LocationReadCloser(
        location=Location(
            coordinates=None,
            scope=Scope.PROD,
            access_path="test/path",
            annotations={},
            dependency_type=DependencyType.DIRECT,
        ),
        read_closer=TextIOWrapper(BytesIO(json_str.encode())),
    )

    with caplog.at_level(logging.WARNING):
        packages, relationships = parse_package_json(None, None, reader)
        assert packages == []
        assert relationships == []
        assert "No deps found in package JSON" in caplog.text


def test_parse_package_json_empty_name_or_specifier() -> None:
    json_str = """{
        "dependencies": {
            "": "1.0.0",
            "test-package": "",
            "valid-package": "2.0.0"
        }
    }"""

    reader = LocationReadCloser(
        location=Location(
            coordinates=None,
            scope=Scope.PROD,
            access_path="test/path",
            annotations={},
            dependency_type=DependencyType.DIRECT,
        ),
        read_closer=TextIOWrapper(BytesIO(json_str.encode())),
    )

    packages, relationships = parse_package_json(None, None, reader)

    assert len(packages) == 1
    assert packages[0].name == "valid-package"
    assert packages[0].version == "2.0.0"
    assert relationships == []


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.cataloger.javascript.parse_package_json,
            target="_create_package",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_parse_package_json_with_invalid_package() -> None:
    json_str = """{
        "dependencies": {
            "invalid-package": "1.0.0"
        }
    }"""

    reader = LocationReadCloser(
        location=Location(
            coordinates=None,
            scope=Scope.PROD,
            access_path="test/path",
            annotations={},
            dependency_type=DependencyType.DIRECT,
        ),
        read_closer=TextIOWrapper(BytesIO(json_str.encode())),
    )

    packages, relationships = parse_package_json(None, None, reader)
    assert packages == []
    assert relationships == []


def test_parse_package_json_no_dev_deps_warning(caplog: pytest.LogCaptureFixture) -> None:
    json_str = """{
        "dependencies": {
            "valid-package": "1.0.0"
        },
        "devDependencies": ["not-a-dict"]
    }"""

    reader = LocationReadCloser(
        location=Location(
            coordinates=None,
            scope=Scope.PROD,
            access_path="test/path",
            annotations={},
            dependency_type=DependencyType.DIRECT,
        ),
        read_closer=TextIOWrapper(BytesIO(json_str.encode())),
    )

    with caplog.at_level(logging.WARNING):
        packages, relationships = parse_package_json(None, None, reader)

        assert packages == []
        assert relationships == []
        assert "No dev deps found in package JSON" in caplog.text


def test_parse_package_json_empty_dev_deps_name_or_specifier() -> None:
    json_str = """{
        "dependencies": {
            "valid-package": "1.0.0"
        },
        "devDependencies": {
            "": "1.0.0",
            "test-package": "",
            "valid-dev-package": "2.0.0"
        }
    }"""

    reader = LocationReadCloser(
        location=Location(
            coordinates=None,
            scope=Scope.PROD,
            access_path="test/path",
            annotations={},
            dependency_type=DependencyType.DIRECT,
        ),
        read_closer=TextIOWrapper(BytesIO(json_str.encode())),
    )

    packages, relationships = parse_package_json(None, None, reader)

    assert len(packages) == 2

    prod_package = next(p for p in packages if p.name == "valid-package")
    assert prod_package.version == "1.0.0"
    assert not prod_package.is_dev

    dev_package = next(p for p in packages if p.name == "valid-dev-package")
    assert dev_package.version == "2.0.0"
    assert dev_package.is_dev

    assert relationships == []


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.cataloger.javascript.parse_package_json,
            target="_create_package",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_parse_package_json_with_invalid_dev_package() -> None:
    json_str = """{
        "dependencies": {
            "valid-package": "1.0.0"
        },
        "devDependencies": {
            "invalid-dev-package": "1.0.0"
        }
    }"""

    reader = LocationReadCloser(
        location=Location(
            coordinates=None,
            scope=Scope.PROD,
            access_path="test/path",
            annotations={},
            dependency_type=DependencyType.DIRECT,
        ),
        read_closer=TextIOWrapper(BytesIO(json_str.encode())),
    )

    packages, relationships = parse_package_json(None, None, reader)
    assert packages == []
    assert relationships == []
