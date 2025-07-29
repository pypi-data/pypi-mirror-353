import json
from io import BytesIO, TextIOWrapper
from pathlib import Path

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.php.parse_composer_json import (
    _get_location,
    _get_packages,
    parse_composer_json,
)
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_composer_json() -> None:
    test_data_path = get_test_data_path("dependencies/php/composer.json")
    expected_packages = [
        Package(
            name="php",
            version="^8.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=9,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.PROD,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.PHP,
            licenses=[],
            type=PackageType.PhpComposerPkg,
            p_url="pkg:composer/php@%5E8.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="laravel/framework",
            version="^12.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=10,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.PROD,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.PHP,
            licenses=[],
            type=PackageType.PhpComposerPkg,
            p_url="pkg:composer/laravel/framework@%5E12.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="laravel/tinker",
            version="^2.10.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=11,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.PROD,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.PHP,
            licenses=[],
            type=PackageType.PhpComposerPkg,
            p_url="pkg:composer/laravel/tinker@%5E2.10.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="fakerphp/faker",
            version="^1.23",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=14,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.DEV,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.PHP,
            licenses=[],
            type=PackageType.PhpComposerPkg,
            p_url="pkg:composer/fakerphp/faker@%5E1.23",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
        ),
        Package(
            name="laravel/pail",
            version="^1.2.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=15,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.DEV,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.PHP,
            licenses=[],
            type=PackageType.PhpComposerPkg,
            p_url="pkg:composer/laravel/pail@%5E1.2.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
        ),
        Package(
            name="laravel/pint",
            version="^1.13",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=16,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.DEV,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.PHP,
            licenses=[],
            type=PackageType.PhpComposerPkg,
            p_url="pkg:composer/laravel/pint@%5E1.13",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
        ),
        Package(
            name="laravel/sail",
            version="^1.41",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=17,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.DEV,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.PHP,
            licenses=[],
            type=PackageType.PhpComposerPkg,
            p_url="pkg:composer/laravel/sail@%5E1.41",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
        ),
        Package(
            name="mockery/mockery",
            version="^1.6",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=18,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.DEV,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.PHP,
            licenses=[],
            type=PackageType.PhpComposerPkg,
            p_url="pkg:composer/mockery/mockery@%5E1.6",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
        ),
        Package(
            name="nunomaduro/collision",
            version="^8.6",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=19,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.DEV,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.PHP,
            licenses=[],
            type=PackageType.PhpComposerPkg,
            p_url="pkg:composer/nunomaduro/collision@%5E8.6",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
        ),
        Package(
            name="phpunit/phpunit",
            version="^11.5.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=20,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.DEV,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.PHP,
            licenses=[],
            type=PackageType.PhpComposerPkg,
            p_url="pkg:composer/phpunit/phpunit@%5E11.5.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
        ),
    ]

    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, relationships = parse_composer_json(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        assert pkgs == expected_packages
        assert len(relationships) == 0


def test_parse_composer_json_with_invalid_dependencies() -> None:
    invalid_composer_json = {
        "require": {
            "valid/package": "1.0.0",
            "invalid-package": None,
        },
        "require-dev": {
            "valid/dev-package": "2.0.0",
            "invalid-dev-package": [],
        },
    }

    json_str = json.dumps(invalid_composer_json)
    bytes_io = BytesIO(json_str.encode("utf-8"))
    text_io = TextIOWrapper(bytes_io, encoding="utf-8")

    pkgs, relationships = parse_composer_json(
        None,
        None,
        LocationReadCloser(location=new_location("composer.json"), read_closer=text_io),
    )

    assert len(pkgs) == 2
    assert len(relationships) == 0
    assert any(pkg.name == "valid/package" and pkg.version == "1.0.0" for pkg in pkgs)
    assert any(pkg.name == "valid/dev-package" and pkg.version == "2.0.0" for pkg in pkgs)


def test_get_location_without_coordinates() -> None:
    location_no_coords = Location(
        coordinates=None,
        dependency_type=DependencyType.DIRECT,
        scope=Scope.PROD,
        access_path="test.json",
        annotations={},
    )
    result = _get_location(location_no_coords, sourceline=15, is_dev=False)
    assert result.scope == Scope.PROD
    assert result.dependency_type == DependencyType.DIRECT
    assert result.coordinates is None


def test_get_packages_with_empty_dependencies() -> None:
    empty_deps: IndexedDict[str, ParsedValue] = IndexedDict()
    location = Location(
        coordinates=Coordinates(
            real_path="test.json",
            file_system_id=None,
            line=1,
        ),
        dependency_type=DependencyType.DIRECT,
        scope=Scope.PROD,
        access_path="test.json",
        annotations={},
    )
    reader = LocationReadCloser(
        location=location,
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    packages = _get_packages(reader, empty_deps, is_dev=False)
    assert len(packages) == 0
