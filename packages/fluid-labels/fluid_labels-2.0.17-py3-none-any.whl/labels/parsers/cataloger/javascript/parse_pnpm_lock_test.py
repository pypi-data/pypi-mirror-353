from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.indexables import FileCoordinate, IndexedDict, IndexedList, ParsedValue, Position
from labels.model.package import Digest, Language, Package, PackageType
from labels.model.relationship import RelationshipType
from labels.parsers.cataloger.javascript.model import PnpmEntry
from labels.parsers.cataloger.javascript.parse_pnpm_lock import (
    _generate_relations_relationship,
    _process_package,
    _process_relationships,
    extract_package_name_from_key_dependency,
    extract_version_from_value_dependency,
    manage_coordinates,
    parse_pnpm_lock,
    process_package_string,
)
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_pnpm_lock() -> None:
    test_data_path = get_test_data_path("dependencies/javascript/pnpm-v6/pnpm-lock.yaml")
    expected_packages = [
        Package(
            name="slug",
            version="0.9.0",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=12,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            type=PackageType.NpmPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PnpmEntry(
                is_dev=False,
                integrity=Digest(
                    algorithm="sha-512",
                    value="sha512-1Yjs2SvM8TflER/OD3cOjhWWOZb58A2t7wpE2S9XfBYTiIl+XFhQG2bjy4Pu1I+EAlCNUzRDYDdFwFYUKvXcIA==",
                ),
            ),
            p_url="pkg:npm/slug@0.9.0",
        ),
        Package(
            name="zod",
            version="3.21.4",
            language=Language.JAVASCRIPT,
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
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            type=PackageType.NpmPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PnpmEntry(
                is_dev=False,
                integrity=Digest(
                    algorithm="sha-512",
                    value="sha512-m46AKbrzKVzOzs/DZgVnG5H55N1sv1M8qZU3A8RIKbs3mrACDNeIOeilDymVb2HdmP8uwshOCF4uJ8uM9rCqJw==",
                ),
            ),
            p_url="pkg:npm/zod@3.21.4",
        ),
        Package(
            name="@zag-js/script-manager",
            version="0.8.6",
            language=Language.JAVASCRIPT,
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
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            type=PackageType.NpmPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PnpmEntry(
                is_dev=False,
                integrity=Digest(
                    algorithm="sha-512",
                    value="sha512-BsAI2y9K2WKXRvkX8NULCNSj0ie8fcqJLnCEXvEOErydGQdPzO39zInQ0t+6iqPHjcNVoyNV151dfX+3wyUSVg==",
                ),
            ),
            p_url="pkg:npm/%40zag-js/script-manager@0.8.6",
        ),
        Package(
            name="hoek",
            version="5.0.0",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.DEV,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=24,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            type=PackageType.NpmPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PnpmEntry(
                is_dev=True,
                integrity=Digest(
                    algorithm="sha-512",
                    value="sha512-BsAI2y9K2WKXRvkX8NULCNSj0ie8fcqJLnCEXvEOErydGQdPzO39zInQ0t+6iqPHjcNVoyNV151dfX+3wyUSVg==",
                ),
            ),
            p_url="pkg:npm/hoek@5.0.0",
        ),
        Package(
            name="yargs",
            version="17.7.1",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.DEV,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=28,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            type=PackageType.NpmPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PnpmEntry(
                is_dev=True,
                integrity=Digest(
                    algorithm="sha-512",
                    value="sha512-cwiTb08Xuv5fqF4AovYacTFNxk62th7LKJ6BL9IGUpTJrWoU7/7WdQGTP2SjKf1dUNBGzDd28p/Yfs/GI6JrLw==",
                ),
            ),
            p_url="pkg:npm/yargs@17.7.1",
        ),
        Package(
            name="@builder.io/qwik",
            version="1.2.6",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=41,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            type=PackageType.NpmPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PnpmEntry(is_dev=False, integrity=Digest(algorithm="sha-512", value=None)),
            p_url="pkg:npm/%40builder.io/qwik@1.2.6",
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_pnpm_lock(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        assert pkgs == expected_packages


def test_extract_package_name_from_key_dependency_with_match() -> None:
    result = extract_package_name_from_key_dependency("@my-package/name")
    assert result == "@my-package/name"


def test_extract_version_from_value_dependency_no_match() -> None:
    result = extract_version_from_value_dependency("not-a-version")
    assert result is None


def test_process_relationships_with_non_string_dependency() -> None:
    dependencies = IndexedDict[str, ParsedValue]()

    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    dependencies[("test-package", position)] = (123, position)

    packages: list[Package] = []

    relationships = _process_relationships(dependencies, packages, None)

    assert len(relationships) == 0


def test_process_relationships_with_valid_packages() -> None:
    dependencies = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    dependencies[("@test-package/dependency", position)] = ("1.0.0", position)

    dep_package = Package(
        name="@test-package/dependency",
        version="1.0.0",
        language=Language.JAVASCRIPT,
        licenses=[],
        locations=[],
        type=PackageType.NpmPkg,
        p_url="pkg:npm/%40test-package/dependency@1.0.0",
    )

    current_package = Package(
        name="@test-package/main",
        version="2.0.0",
        language=Language.JAVASCRIPT,
        licenses=[],
        locations=[],
        type=PackageType.NpmPkg,
        p_url="pkg:npm/%40test-package/main@2.0.0",
    )

    packages = [dep_package, current_package]

    relationships = _process_relationships(dependencies, packages, current_package)

    assert len(relationships) == 1
    relationship = relationships[0]

    assert relationship.from_ == dep_package
    assert relationship.to_ == current_package
    assert relationship.type == RelationshipType.DEPENDENCY_OF_RELATIONSHIP


def test_generate_relations_relationship_with_invalid_packages_items() -> None:
    package_yaml = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )
    package_yaml[("packages", position)] = ("not-an-indexed-dict", position)
    packages: list[Package] = []
    relationships = _generate_relations_relationship(package_yaml, packages)
    assert len(relationships) == 0


def test_generate_relations_relationship_with_invalid_package_value() -> None:
    package_yaml = IndexedDict[str, ParsedValue]()
    packages_items = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )
    packages_items[("/@test-package/main@2.0.0", position)] = ("not-an-indexed-dict", position)
    package_yaml[("packages", position)] = (packages_items, position)
    packages: list[Package] = []
    relationships = _generate_relations_relationship(package_yaml, packages)
    assert len(relationships) == 0


def test_manage_coordinates_without_coordinates() -> None:
    base_location = Location(
        scope=Scope.PROD,
        coordinates=None,
        access_path="test/path",
        annotations={},
        dependency_type=DependencyType.DIRECT,
    )
    package_yaml = IndexedDict[str, ParsedValue]()
    result = manage_coordinates(
        package_yaml=package_yaml,
        package_key="test-key",
        package_name="test-package",
        direct_dependencies=[],
        base_location=base_location,
    )
    assert result == base_location
    assert result.coordinates is None


def test_manage_coordinates_with_invalid_packages() -> None:
    base_location = Location(
        scope=Scope.PROD,
        coordinates=Coordinates(
            real_path="test/path",
            file_system_id=None,
            line=1,
        ),
        access_path="test/path",
        annotations={},
        dependency_type=DependencyType.DIRECT,
    )
    package_yaml = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )
    package_yaml[("packages", position)] = ("not-an-indexed-dict", position)
    result = manage_coordinates(
        package_yaml=package_yaml,
        package_key="test-key",
        package_name="test-package",
        direct_dependencies=[],
        base_location=base_location,
    )
    assert result == base_location
    assert result.coordinates
    assert result.coordinates.line == 1


def test_process_package_with_empty_values() -> None:
    package_yaml = IndexedDict[str, ParsedValue]()
    pkg_spec = IndexedDict[str, ParsedValue]()
    base_location = Location(
        scope=Scope.PROD,
        coordinates=Coordinates(
            real_path="test/path",
            file_system_id=None,
            line=1,
        ),
        access_path="test/path",
        annotations={},
        dependency_type=DependencyType.DIRECT,
    )
    result = _process_package(
        package_key="/@1.0.0",
        pkg_spec=pkg_spec,
        package_yaml=package_yaml,
        direct_dependencies=[],
        base_location=base_location,
    )
    assert result is None
    result = _process_package(
        package_key="/test-package@",
        pkg_spec=pkg_spec,
        package_yaml=package_yaml,
        direct_dependencies=[],
        base_location=base_location,
    )
    assert result is None


def test_process_package_string_with_invalid_types() -> None:
    spec = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )
    spec[("name", position)] = (123, position)
    spec[("version", position)] = (456, position)
    result = process_package_string("github.com/test/repo", spec)
    assert result is None


def test_process_package_with_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    package_yaml = IndexedDict[str, ParsedValue]()
    pkg_spec = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )
    packages_items = IndexedDict[str, ParsedValue]()
    packages_items[("/test-package@1.0.0", position)] = (pkg_spec, position)
    package_yaml[("packages", position)] = (packages_items, position)

    base_location = Location(
        scope=Scope.PROD,
        coordinates=Coordinates(
            real_path="test/path",
            file_system_id=None,
            line=1,
        ),
        access_path="test/path",
        annotations={},
        dependency_type=DependencyType.DIRECT,
    )
    with patch("labels.model.package.Package.__init__") as mock_init:
        mock_init.side_effect = ValidationError.from_exception_data(
            title="",
            line_errors=[
                InitErrorDetails(  # type: ignore
                    type="missing",
                    loc=("name",),
                    input=None,
                    ctx={},
                ),
            ],
        )
        result = _process_package(
            package_key="/test-package@1.0.0",
            pkg_spec=pkg_spec,
            package_yaml=package_yaml,
            direct_dependencies=[],
            base_location=base_location,
        )
        assert result is None
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


def test_parse_pnpm_lock_with_empty_yaml() -> None:
    content = b""
    reader = LocationReadCloser(
        location=Location(
            scope=Scope.PROD,
            coordinates=Coordinates(
                real_path="test/path",
                file_system_id=None,
                line=1,
            ),
            access_path="test/path",
            annotations={},
            dependency_type=DependencyType.DIRECT,
        ),
        read_closer=TextIOWrapper(BytesIO(content)),
    )
    with patch(
        "labels.parsers.cataloger.javascript.parse_pnpm_lock.parse_yaml_with_tree_sitter",
    ) as mock_parse:
        mock_parse.return_value = None
        packages, relationships = parse_pnpm_lock(None, None, reader)
        assert packages == []
        assert relationships == []


def test_parse_pnpm_lock_with_direct_dependencies() -> None:
    content = b""
    reader = LocationReadCloser(
        location=Location(
            scope=Scope.PROD,
            coordinates=Coordinates(
                real_path="test/path",
                file_system_id=None,
                line=1,
            ),
            access_path="test/path",
            annotations={},
            dependency_type=DependencyType.DIRECT,
        ),
        read_closer=TextIOWrapper(BytesIO(content)),
    )
    package_yaml = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )
    dependencies = IndexedList[ParsedValue]()
    dev_dependencies = IndexedList[ParsedValue]()
    dependencies.append(("test-package", position))
    dev_dependencies.append(("dev-package", position))
    package_yaml[("dependencies", position)] = (dependencies, position)
    package_yaml[("devDependencies", position)] = (dev_dependencies, position)
    package_yaml[("packages", position)] = (IndexedDict[str, ParsedValue](), position)

    with patch(
        "labels.parsers.cataloger.javascript.parse_pnpm_lock.parse_yaml_with_tree_sitter",
    ) as mock_parse:
        mock_parse.return_value = package_yaml
        packages, relationships = parse_pnpm_lock(None, None, reader)
        assert len(packages) == 0
        assert len(relationships) == 0


def test_parse_pnpm_lock_with_invalid_packages_items() -> None:
    content = b""
    reader = LocationReadCloser(
        location=Location(
            scope=Scope.PROD,
            coordinates=Coordinates(
                real_path="test/path",
                file_system_id=None,
                line=1,
            ),
            access_path="test/path",
            annotations={},
            dependency_type=DependencyType.DIRECT,
        ),
        read_closer=TextIOWrapper(BytesIO(content)),
    )
    package_yaml = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )
    package_yaml[("packages", position)] = ("not-an-indexed-dict", position)

    with patch(
        "labels.parsers.cataloger.javascript.parse_pnpm_lock.parse_yaml_with_tree_sitter",
    ) as mock_parse:
        mock_parse.return_value = package_yaml
        packages, relationships = parse_pnpm_lock(None, None, reader)
        assert packages == []
        assert relationships == []


def test_parse_pnpm_lock_with_invalid_pkg_spec() -> None:
    content = b""
    reader = LocationReadCloser(
        location=Location(
            scope=Scope.PROD,
            coordinates=Coordinates(
                real_path="test/path",
                file_system_id=None,
                line=1,
            ),
            access_path="test/path",
            annotations={},
            dependency_type=DependencyType.DIRECT,
        ),
        read_closer=TextIOWrapper(BytesIO(content)),
    )
    package_yaml = IndexedDict[str, ParsedValue]()
    packages_items = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )
    packages_items[("/@test-package/main@2.0.0", position)] = ("not-an-indexed-dict", position)
    package_yaml[("packages", position)] = (packages_items, position)

    with patch(
        "labels.parsers.cataloger.javascript.parse_pnpm_lock.parse_yaml_with_tree_sitter",
    ) as mock_parse:
        mock_parse.return_value = package_yaml
        packages, relationships = parse_pnpm_lock(None, None, reader)
        assert packages == []
        assert relationships == []
