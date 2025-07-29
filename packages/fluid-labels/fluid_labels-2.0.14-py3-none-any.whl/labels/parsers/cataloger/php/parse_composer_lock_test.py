import json
from io import BytesIO, TextIOWrapper
from pathlib import Path

import labels.parsers.cataloger.php.parse_composer_lock as parse_composer_lock_mod
from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.indexables import IndexedDict
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.php.model import (
    PhpComposerAuthors,
    PhpComposerExternalReference,
    PhpComposerInstalledEntry,
    PhpComposerLockEntry,
)
from labels.parsers.cataloger.php.parse_composer_lock import parse_composer_lock
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_composer_lock() -> None:
    test_data_path = get_test_data_path("dependencies/php/composer.lock")
    expected_packages = [
        Package(
            name="adoy/fastcgi-client",
            version="1.0.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=10,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.PHP,
            licenses=[],
            type=PackageType.PhpComposerPkg,
            metadata=PhpComposerLockEntry(
                name="adoy/fastcgi-client",
                version="1.0.2",
                source=PhpComposerExternalReference(
                    type="git",
                    url="https://github.com/adoy/PHP-FastCGI-Client.git",
                    reference="6d9a552f0206a1db7feb442824540aa6c55e5b27",
                    shasum=None,
                ),
                dist=PhpComposerExternalReference(
                    type="zip",
                    url=(
                        "https://api.github.com/repos/adoy/PHP-FastCGI-Client"
                        "/zipball/6d9a552f0206a1db7feb442824540aa6c55e5b27"
                    ),
                    reference="6d9a552f0206a1db7feb442824540aa6c55e5b27",
                    shasum=None,
                ),
                require=None,
                provide=None,
                require_dev=None,
                suggest=None,
                license=["MIT"],
                type="library",
                notification_url="https://packagist.org/downloads/",
                bin=None,
                authors=[
                    PhpComposerAuthors(
                        name="Pierrick Charron",
                        email="pierrick@adoy.net",
                        homepage=None,
                    ),
                ],
                description="Lightweight, single file FastCGI client for PHP.",
                homepage=None,
                keywords=["fastcgi", "fcgi"],
                time="2019-12-11T13:49:21+00:00",
            ),
            p_url="pkg:composer/adoy/fastcgi-client@1.0.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="alcaeus/mongo-php-adapter",
            version="1.1.11",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=47,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.PHP,
            licenses=[],
            type=PackageType.PhpComposerPkg,
            metadata=PhpComposerLockEntry(
                name="alcaeus/mongo-php-adapter",
                version="1.1.11",
                source=PhpComposerExternalReference(
                    type="git",
                    url="https://github.com/alcaeus/mongo-php-adapter.git",
                    reference="43b6add94c8b4cb9890d662cba4c0defde733dcf",
                    shasum=None,
                ),
                dist=PhpComposerExternalReference(
                    type="zip",
                    url=(
                        "https://api.github.com/repos/alcaeus"
                        "/mongo-php-adapter/zipball"
                        "/43b6add94c8b4cb9890d662cba4c0defde733dcf"
                    ),
                    reference="43b6add94c8b4cb9890d662cba4c0defde733dcf",
                    shasum=None,
                ),
                require={
                    "ext-ctype": "*",
                    "ext-hash": "*",
                    "ext-mongodb": "^1.2.0",
                    "mongodb/mongodb": "^1.0.1",
                    "php": "^5.6 || ^7.0",
                },
                provide={"ext-mongo": "1.6.14"},
                require_dev={
                    "phpunit/phpunit": "^5.7.27 || ^6.0 || ^7.0",
                    "squizlabs/php_codesniffer": "^3.2",
                },
                suggest=None,
                license=["MIT"],
                type="library",
                notification_url="https://packagist.org/downloads/",
                bin=None,
                authors=[
                    PhpComposerAuthors(
                        name="alcaeus",
                        email="alcaeus@alcaeus.org",
                        homepage=None,
                    ),
                    PhpComposerAuthors(
                        name="Olivier Lechevalier",
                        email="olivier.lechevalier@gmail.com",
                        homepage=None,
                    ),
                ],
                description=("Adapter to provide ext-mongo interface on top of mongo-php-libary"),
                homepage=None,
                keywords=["database", "mongodb"],
                time="2019-11-11T20:47:32+00:00",
            ),
            p_url="pkg:composer/alcaeus/mongo-php-adapter@1.1.11",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="behat/gherkin",
            version="v4.6.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=115,
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
            metadata=PhpComposerLockEntry(
                name="behat/gherkin",
                version="v4.6.2",
                source=PhpComposerExternalReference(
                    type="git",
                    url="https://github.com/Behat/Gherkin.git",
                    reference="51ac4500c4dc30cbaaabcd2f25694299df666a31",
                    shasum=None,
                ),
                dist=PhpComposerExternalReference(
                    type="zip",
                    url=(
                        "https://api.github.com/repos/Behat"
                        "/Gherkin/zipball"
                        "/51ac4500c4dc30cbaaabcd2f25694299df666a31"
                    ),
                    reference="51ac4500c4dc30cbaaabcd2f25694299df666a31",
                    shasum=None,
                ),
                require={"php": ">=5.3.1"},
                provide=None,
                require_dev={
                    "phpunit/phpunit": "~4.5|~5",
                    "symfony/phpunit-bridge": "~2.7|~3|~4",
                    "symfony/yaml": "~2.3|~3|~4",
                },
                suggest={
                    "symfony/yaml": ("If you want to parse features, represented in YAML files"),
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
                description="Gherkin DSL parser for PHP 5.3",
                homepage="http://behat.org/",
                keywords=[
                    "BDD",
                    "Behat",
                    "Cucumber",
                    "DSL",
                    "gherkin",
                    "parser",
                ],
                time="2020-03-17T14:03:26+00:00",
            ),
            p_url="pkg:composer/behat/gherkin@v4.6.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
        ),
        Package(
            name="codeception/codeception",
            version="4.1.6",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=174,
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
            metadata=PhpComposerLockEntry(
                name="codeception/codeception",
                version="4.1.6",
                source=PhpComposerExternalReference(
                    type="git",
                    url="https://github.com/Codeception/Codeception.git",
                    reference="5515b6a6c6f1e1c909aaff2e5f3a15c177dfd1a9",
                    shasum=None,
                ),
                dist=PhpComposerExternalReference(
                    type="zip",
                    url=(
                        "https://api.github.com/repos/Codeception"
                        "/Codeception/zipball"
                        "/5515b6a6c6f1e1c909aaff2e5f3a15c177dfd1a9"
                    ),
                    reference="5515b6a6c6f1e1c909aaff2e5f3a15c177dfd1a9",
                    shasum=None,
                ),
                require={
                    "behat/gherkin": "^4.4.0",
                    "codeception/lib-asserts": "^1.0",
                    "codeception/phpunit-wrapper": (
                        ">6.0.15 <6.1.0 | ^6.6.1 | ^7.7.1 | ^8.1.1 | ^9.0"
                    ),
                    "codeception/stub": "^2.0 | ^3.0",
                    "ext-curl": "*",
                    "ext-json": "*",
                    "ext-mbstring": "*",
                    "guzzlehttp/psr7": "~1.4",
                    "php": ">=5.6.0 <8.0",
                    "symfony/console": ">=2.7 <6.0",
                    "symfony/css-selector": ">=2.7 <6.0",
                    "symfony/event-dispatcher": ">=2.7 <6.0",
                    "symfony/finder": ">=2.7 <6.0",
                    "symfony/yaml": ">=2.7 <6.0",
                },
                provide=None,
                require_dev={
                    "codeception/module-asserts": "*@dev",
                    "codeception/module-cli": "*@dev",
                    "codeception/module-db": "*@dev",
                    "codeception/module-filesystem": "*@dev",
                    "codeception/module-phpbrowser": "*@dev",
                    "codeception/specify": "~0.3",
                    "codeception/util-universalframework": "*@dev",
                    "monolog/monolog": "~1.8",
                    "squizlabs/php_codesniffer": "~2.0",
                    "symfony/process": ">=2.7 <6.0",
                    "vlucas/phpdotenv": "^2.0 | ^3.0 | ^4.0",
                },
                suggest={
                    "codeception/specify": "BDD-style code blocks",
                    "codeception/verify": "BDD-style assertions",
                    "hoa/console": "For interactive console functionality",
                    "stecman/symfony-console-completion": ("For BASH autocompletion"),
                    "symfony/phpunit-bridge": "For phpunit-bridge support",
                },
                license=["MIT"],
                type="library",
                notification_url="https://packagist.org/downloads/",
                bin=["codecept"],
                authors=[
                    PhpComposerAuthors(
                        name="Michael Bodnarchuk",
                        email="davert@mail.ua",
                        homepage="http://codegyre.com",
                    ),
                ],
                description="BDD-style testing framework",
                homepage="http://codeception.com/",
                keywords=[
                    "BDD",
                    "TDD",
                    "acceptance testing",
                    "functional testing",
                    "unit testing",
                ],
                time="2020-06-07T16:31:51+00:00",
            ),
            p_url="pkg:composer/codeception/codeception@4.1.6",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_composer_lock(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        assert pkgs == expected_packages


def test_parse_composer_lock_skips_invalid_packages() -> None:
    invalid_composer_lock = {
        "packages": [
            {"name": "valid/package", "version": "1.0.0"},
            "invalid-package",
        ],
        "packages-dev": [],
    }

    json_str = json.dumps(invalid_composer_lock)
    bytes_io = BytesIO(json_str.encode("utf-8"))
    text_io = TextIOWrapper(bytes_io, encoding="utf-8")

    pkgs, _ = parse_composer_lock(
        None,
        None,
        LocationReadCloser(location=new_location("composer.lock"), read_closer=text_io),
    )

    assert len(pkgs) == 1
    assert pkgs[0].name == "valid/package"
    assert pkgs[0].version == "1.0.0"


def test_parse_composer_lock_skips_invalid_package_creation() -> None:
    invalid_composer_lock = {
        "packages": [
            {
                "invalid": "package",
                "description": "This package is invalid",
            },
        ],
        "packages-dev": [],
    }

    json_str = json.dumps(invalid_composer_lock)
    bytes_io = BytesIO(json_str.encode("utf-8"))
    text_io = TextIOWrapper(bytes_io, encoding="utf-8")

    pkgs, _ = parse_composer_lock(
        None,
        None,
        LocationReadCloser(location=new_location("composer.lock"), read_closer=text_io),
    )

    assert len(pkgs) == 0


@mocks(
    mocks=[
        Mock(
            module=parse_composer_lock_mod,
            target="new_package_from_composer",
            target_type="sync",
            expected=Package(
                name="test/package",
                version="1.0.0",
                locations=[],
                language=Language.PHP,
                licenses=[],
                type=PackageType.PhpComposerPkg,
                metadata=IndexedDict(),
                p_url="pkg:composer/test/package@1.0.0",
                dependencies=None,
                found_by=None,
                health_metadata=None,
                is_dev=False,
            ),
        ),
    ],
)
async def test_parse_composer_lock_skips_invalid_metadata_type() -> None:
    invalid_composer_lock = {
        "packages": [
            {
                "name": "test/package",
                "version": "1.0.0",
                "require": {"other/package": "^1.0"},
            },
        ],
        "packages-dev": [],
    }

    json_str = json.dumps(invalid_composer_lock)
    bytes_io = BytesIO(json_str.encode("utf-8"))
    text_io = TextIOWrapper(bytes_io, encoding="utf-8")

    pkgs, relationships = parse_composer_lock(
        None,
        None,
        LocationReadCloser(location=new_location("composer.lock"), read_closer=text_io),
    )

    assert len(relationships) == 0
    assert len(pkgs) == 1
    assert not isinstance(pkgs[0].metadata, PhpComposerInstalledEntry | PhpComposerLockEntry)
