from io import BytesIO, TextIOWrapper
from pathlib import Path

import labels.parsers.cataloger.php.parse_installed_json as parse_installed_json_mod
from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import RelationshipType
from labels.parsers.cataloger.php.model import (
    PhpComposerAuthors,
    PhpComposerExternalReference,
    PhpComposerLockEntry,
)
from labels.parsers.cataloger.php.parse_installed_json import (
    _extract_relationships,
    parse_installed_json,
)
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_composer_lock() -> None:
    test_data_paths = [
        get_test_data_path("dependencies/php/vendor/composer_1/installed.json"),
        get_test_data_path("dependencies/php/vendor/composer_2/installed.json"),
    ]
    expected_packages = [
        Package(
            name="asm89/stack-cors",
            version="1.3.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_paths[0],
                        file_system_id=None,
                        line=0,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_paths[0],
                    annotations={},
                ),
            ],
            language=Language.PHP,
            licenses=[],
            type=PackageType.PhpComposerPkg,
            metadata=PhpComposerLockEntry(
                name="asm89/stack-cors",
                version="1.3.0",
                source=PhpComposerExternalReference(
                    type="git",
                    url="https://github.com/asm89/stack-cors.git",
                    reference="b9c31def6a83f84b4d4a40d35996d375755f0e08",
                    shasum=None,
                ),
                dist=PhpComposerExternalReference(
                    type="zip",
                    url=(
                        "https://api.github.com/repos/asm89/stack-cors"
                        "/zipball/b9c31def6a83f84b4d4a40d35996d375755f0e08"
                    ),
                    reference="b9c31def6a83f84b4d4a40d35996d375755f0e08",
                    shasum=None,
                ),
                require={
                    "php": ">=5.5.9",
                    "symfony/http-foundation": "~2.7|~3.0|~4.0|~5.0",
                    "symfony/http-kernel": "~2.7|~3.0|~4.0|~5.0",
                },
                provide=None,
                require_dev={
                    "phpunit/phpunit": "^5.0 || ^4.8.10",
                    "squizlabs/php_codesniffer": "^2.3",
                },
                suggest=None,
                license=["MIT"],
                type="library",
                notification_url="https://packagist.org/downloads/",
                bin=None,
                authors=[
                    PhpComposerAuthors(
                        name="Alexander",
                        email="iam.asm89@gmail.com",
                        homepage=None,
                    ),
                ],
                description=("Cross-origin resource sharing library and stack middleware"),
                homepage="https://github.com/asm89/stack-cors",
                keywords=["cors", "stack"],
                time="2019-12-24T22:41:47+00:00",
            ),
            p_url="pkg:composer/asm89/stack-cors@1.3.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="behat/mink",
            version="v1.8.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_paths[0],
                        file_system_id=None,
                        line=0,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_paths[0],
                    annotations={},
                ),
            ],
            language=Language.PHP,
            licenses=[],
            type=PackageType.PhpComposerPkg,
            metadata=PhpComposerLockEntry(
                name="behat/mink",
                version="v1.8.1",
                source=PhpComposerExternalReference(
                    type="git",
                    url="https://github.com/minkphp/Mink.git",
                    reference="07c6a9fe3fa98c2de074b25d9ed26c22904e3887",
                    shasum=None,
                ),
                dist=PhpComposerExternalReference(
                    type="zip",
                    url=(
                        "https://api.github.com/repos/minkphp/Mink/zipball"
                        "/07c6a9fe3fa98c2de074b25d9ed26c22904e3887"
                    ),
                    reference="07c6a9fe3fa98c2de074b25d9ed26c22904e3887",
                    shasum=None,
                ),
                require={
                    "php": ">=5.3.1",
                    "symfony/css-selector": "^2.7|^3.0|^4.0|^5.0",
                },
                provide=None,
                require_dev={
                    "phpunit/phpunit": ("^4.8.36 || ^5.7.27 || ^6.5.14 || ^7.5.20"),
                    "symfony/debug": "^2.7|^3.0|^4.0",
                    "symfony/phpunit-bridge": "^3.4.38 || ^5.0.5",
                },
                suggest={
                    "behat/mink-browserkit-driver": (
                        "extremely fast headless driver for"
                        " Symfony\\\\Kernel-based apps (Sf2, Silex)"
                    ),
                    "behat/mink-goutte-driver": (
                        "fast headless driver for any app without JS emulation"
                    ),
                    "behat/mink-selenium2-driver": (
                        "slow, but JS-enabled driver for any app (requires Selenium2)"
                    ),
                    "behat/mink-zombie-driver": (
                        "fast and JS-enabled headless driver for any app (requires node.js)"
                    ),
                    "dmore/chrome-mink-driver": (
                        "fast and JS-enabled driver for any app"
                        " (requires chromium or google chrome)"
                    ),
                },
                license=["MIT"],
                type="library",
                notification_url="https://packagist.org/downloads/",
                bin=None,
                authors=[
                    PhpComposerAuthors(
                        name="Konstantin Kudryashov",
                        email="ever.zet@gmail.com",
                        homepage="http://everzet.com",
                    ),
                ],
                description="Browser controller/emulator abstraction for PHP",
                homepage="http://mink.behat.org/",
                keywords=["browser", "testing", "web"],
                time="2020-03-11T15:45:53+00:00",
            ),
            p_url="pkg:composer/behat/mink@v1.8.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
    ]
    for test_data_path in test_data_paths:
        with Path(test_data_path).open(encoding="utf-8") as reader:
            pkgs, _ = parse_installed_json(
                None,
                None,
                LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
            )
            for pkg in pkgs:
                # These values are fixed, because the content of the files and
                # packages should be the same, but the location is different
                pkg.locations[0].access_path = test_data_paths[0]
                if pkg.locations[0].coordinates:
                    pkg.locations[0].coordinates.line = 0
                    pkg.locations[0].coordinates.real_path = test_data_paths[0]
                pkg.is_dev = False
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        assert pkgs == expected_packages


def test_parse_installed_json_with_invalid_package() -> None:
    json_content = """{
        "packages": ["invalid_package", {
            "name": "test/package",
            "version": "1.0.0",
            "source": {
                "type": "git",
                "url": "https://github.com/test/package.git",
                "reference": "abc123"
            },
            "require": {
                "php": ">=7.0"
            }
        }]
    }"""

    bytes_io = BytesIO(json_content.encode("utf-8"))
    text_wrapper = TextIOWrapper(bytes_io, encoding="utf-8")

    location = new_location("fake/path/installed.json")

    pkgs, _ = parse_installed_json(
        None,
        None,
        LocationReadCloser(location=location, read_closer=text_wrapper),
    )

    assert all(isinstance(pkg.metadata, PhpComposerLockEntry) for pkg in pkgs)
    assert len(pkgs) == 1
    assert pkgs[0].name == "test/package"


def test_parse_installed_json_with_invalid_package_data() -> None:
    json_content = """{
        "packages": [{
            "name": "test/package",
            "version": "1.0.0",
            "source": {
                "type": 123  // type debe ser string, no número
            }
        }]
    }"""

    bytes_io = BytesIO(json_content.encode("utf-8"))
    text_wrapper = TextIOWrapper(bytes_io, encoding="utf-8")

    location = new_location("fake/path/installed.json")

    pkgs, _ = parse_installed_json(
        None,
        None,
        LocationReadCloser(location=location, read_closer=text_wrapper),
    )

    assert len(pkgs) == 0


@mocks(
    mocks=[
        Mock(
            module=parse_installed_json_mod,
            target="new_package_from_composer",
            target_type="sync",
            expected=Package(
                name="test/package",
                version="1.0.0",
                locations=[],
                language=Language.PHP,
                licenses=[],
                type=PackageType.PhpComposerPkg,
                metadata={},
                p_url="pkg:composer/test/package@1.0.0",
                dependencies=None,
                found_by=None,
                health_metadata=None,
                is_dev=False,
            ),
        ),
    ],
)
async def test_extract_relationships_skips_non_phpcomposer_metadata() -> None:
    json_content = """{
        "packages": [{
            "name": "test/package",
            "version": "1.0.0"
        }]
    }"""
    bytes_io = BytesIO(json_content.encode("utf-8"))
    text_wrapper = TextIOWrapper(bytes_io, encoding="utf-8")
    location = new_location("fake/path/installed.json")
    pkgs, relationships = parse_installed_json(
        None,
        None,
        LocationReadCloser(location=location, read_closer=text_wrapper),
    )
    assert len(pkgs) == 1
    assert len(relationships) == 0


def test_extract_relationships_creates_correct_relationships() -> None:
    pkg1 = Package(
        name="test/package1",
        version="1.0.0",
        locations=[],
        language=Language.PHP,
        licenses=[],
        type=PackageType.PhpComposerPkg,
        metadata=PhpComposerLockEntry(
            name="test/package1",
            version="1.0.0",
            source=None,
            dist=None,
            require={"test/package2": "^1.0"},
            provide=None,
            require_dev=None,
            suggest=None,
            license=[],
            type="library",
            notification_url="",
            bin=None,
            authors=[],
            description="",
            homepage="",
            keywords=[],
            time="",
        ),
        p_url="pkg:composer/test/package1@1.0.0",
        dependencies=None,
        found_by=None,
        health_metadata=None,
        is_dev=False,
    )

    pkg2 = Package(
        name="test/package2",
        version="1.0.0",
        locations=[],
        language=Language.PHP,
        licenses=[],
        type=PackageType.PhpComposerPkg,
        metadata=PhpComposerLockEntry(
            name="test/package2",
            version="1.0.0",
            source=None,
            dist=None,
            require={},
            provide=None,
            require_dev=None,
            suggest=None,
            license=[],
            type="library",
            notification_url="",
            bin=None,
            authors=[],
            description="",
            homepage="",
            keywords=[],
            time="",
        ),
        p_url="pkg:composer/test/package2@1.0.0",
        dependencies=None,
        found_by=None,
        health_metadata=None,
        is_dev=False,
    )

    packages = [pkg1, pkg2]
    relationships = _extract_relationships(packages)

    assert len(relationships) == 1
    relationship = relationships[0]
    assert relationship.from_ == pkg1
    assert relationship.to_ == pkg2
    assert relationship.type == RelationshipType.DEPENDENCY_OF_RELATIONSHIP
