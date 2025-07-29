import json
import logging
from io import BytesIO, TextIOWrapper
from pathlib import Path

import pytest

import labels.parsers.cataloger.javascript.parse_package_lock
from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.indexables import FileCoordinate, IndexedDict, ParsedValue, Position
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship, RelationshipType
from labels.parsers.cataloger.javascript.model import NpmPackageLockEntry
from labels.parsers.cataloger.javascript.parse_package_lock import (
    _get_name,
    _solve_sub_dependencies,
    get_direct_dependencies,
    get_direct_dependencies_v2_v3,
    handle_v1,
    handle_v2,
    parse_package_lock,
)
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_package_lock() -> None:
    test_data_path = get_test_data_path("dependencies/javascript/pkg-lock/package-lock.json")
    expected_packages = [
        Package(
            name="@actions/core",
            version="1.6.0",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=5,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.NpmPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/@actions/core/-/core-1.6.0.tgz",
                integrity="sha512-NB1UAZomZlCV/LmJqkLhNTqtKfFXJZAUPcfl/zqG7EfsQdeUJtaWO98SGbuQ3pydJ3fHl2CvI/51OKYlCYYcaw==",
                is_dev=False,
            ),
            p_url="pkg:npm/%40actions/core@1.6.0",
        ),
        Package(
            name="ansi-regex",
            version="3.0.0",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=13,
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
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/ansi-regex/-/ansi-regex-3.0.0.tgz",
                integrity="sha1-7QMXwyIGT3lGbAKWa922Bas32Zg=",
                is_dev=False,
            ),
            p_url="pkg:npm/ansi-regex@3.0.0",
        ),
        Package(
            name="cowsay",
            version="1.4.0",
            language=Language.JAVASCRIPT,
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
            type=PackageType.NpmPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/cowsay/-/cowsay-1.4.0.tgz",
                integrity="sha512-rdg5k5PsHFVJheO/pmE3aDg2rUDDTfPJau6yYkZYlHFktUz+UxbE+IgnUAEyyCyv4noL5ltxXD0gZzmHPCy/9g==",
                is_dev=False,
            ),
            p_url="pkg:npm/cowsay@1.4.0",
        ),
        Package(
            name="get-stdin",
            version="5.0.1",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=29,
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
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/get-stdin/-/get-stdin-5.0.1.tgz",
                integrity="sha1-Ei4WFZHiH/TFJTAwVpPyDmOTo5g=",
                is_dev=False,
            ),
            p_url="pkg:npm/get-stdin@5.0.1",
        ),
        Package(
            name="is-fullwidth-code-point",
            version="2.0.0",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=34,
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
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/is-fullwidth-code-point/-/is-fullwidth-code-point-2.0.0.tgz",
                integrity="sha1-o7MKXE8ZkYMWeqq5O+764937ZU8=",
                is_dev=False,
            ),
            p_url="pkg:npm/is-fullwidth-code-point@2.0.0",
        ),
        Package(
            name="minimist",
            version="0.0.10",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=39,
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
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/minimist/-/minimist-0.0.10.tgz",
                integrity="sha1-3j+YVD2/lggr5IrRoMfNqDYwHc8=",
                is_dev=False,
            ),
            p_url="pkg:npm/minimist@0.0.10",
        ),
        Package(
            name="optimist",
            version="0.6.1",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=44,
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
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/optimist/-/optimist-0.6.1.tgz",
                integrity="sha1-2j6nRob6IaGaERwybpDrFaAZZoY=",
                is_dev=False,
            ),
            p_url="pkg:npm/optimist@0.6.1",
        ),
        Package(
            name="string-width",
            version="2.1.1",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=53,
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
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/string-width/-/string-width-2.1.1.tgz",
                integrity="sha512-nOqH59deCq9SRHlxq1Aw85Jnt4w6KvLKqWVik6oA9ZklXLNIOlqg4F2yrT1MVaTjAqvVwdfeZ7w7aCvJD7ugkw==",
                is_dev=False,
            ),
            p_url="pkg:npm/string-width@2.1.1",
        ),
        Package(
            name="strip-ansi",
            version="4.0.0",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=62,
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
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/strip-ansi/-/strip-ansi-4.0.0.tgz",
                integrity="sha1-qEeQIusaw2iocTibY1JixQXuNo8=",
                is_dev=False,
            ),
            p_url="pkg:npm/strip-ansi@4.0.0",
        ),
        Package(
            name="strip-eof",
            version="1.0.0",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=70,
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
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/strip-eof/-/strip-eof-1.0.0.tgz",
                integrity="sha1-u0P/VZim6wXYm1n80SnJgzE2Br8=",
                is_dev=False,
            ),
            p_url="pkg:npm/strip-eof@1.0.0",
        ),
        Package(
            name="wordwrap",
            version="0.0.3",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=75,
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
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/wordwrap/-/wordwrap-0.0.3.tgz",
                integrity="sha1-o9XabNXAvAAI03I0u68b7WMFkQc=",
                is_dev=False,
            ),
            p_url="pkg:npm/wordwrap@0.0.3",
        ),
        Package(
            name="resolve-url-loader",
            version="3.1.4",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=80,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.NpmPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/resolve-url-loader/-/resolve-url-loader-3.1.4.tgz",
                integrity="sha512-D3sQ04o0eeQEySLrcz4DsX3saHfsr8/N6tfhblxgZKXxMT2Louargg12oGNfoTRLV09GXhVUe5/qgA5vdgNigg==",
                is_dev=False,
            ),
            p_url="pkg:npm/resolve-url-loader@3.1.4",
        ),
        Package(
            name="convert-source-map",
            version="1.7.0",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=97,
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
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/convert-source-map/-/convert-source-map-1.7.0.tgz",
                integrity="sha512-4FJkXzKXEDB1snCFZlLP4gpC3JILicCpGbzG9f9G7tGqGCzETQ2hWPrcinA9oU4wtf2biUaEH5065UnMeR33oA==",
                is_dev=False,
            ),
            p_url="pkg:npm/convert-source-map@1.7.0",
        ),
        Package(
            name="emojis-list",
            version="2.1.0",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=105,
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
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/emojis-list/-/emojis-list-2.1.0.tgz",
                integrity="sha1-TapNnbAPmBmIDHn6RXrlsJof04k=",
                is_dev=False,
            ),
            p_url="pkg:npm/emojis-list@2.1.0",
        ),
        Package(
            name="json5",
            version="1.0.1",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=110,
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
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/json5/-/json5-1.0.1.tgz",
                integrity="sha512-aKS4WQjPenRxiQsC93MNfjx+nbF4PAdYzmd/1JIj8HYzqfbu86beTuNgXDzPknWk0n0uARlyewZo4s++ES36Ow==",
                is_dev=False,
            ),
            p_url="pkg:npm/json5@1.0.1",
        ),
        Package(
            name="loader-utils",
            version="1.2.3",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=118,
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
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/loader-utils/-/loader-utils-1.2.3.tgz",
                integrity="sha512-fkpz8ejdnEMG3s37wGL07iSBDg99O9D5yflE9RGNH3hRdx9SOwYfnGYdZOUIZitN8E+E2vkq3MUMYMvPYl5ZZA==",
                is_dev=False,
            ),
            p_url="pkg:npm/loader-utils@1.2.3",
        ),
        Package(
            name="postcss",
            version="7.0.36",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=128,
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
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/postcss/-/postcss-7.0.36.tgz",
                integrity="sha512-BebJSIUMwJHRH0HAQoxN4u1CN86glsrwsW0q7T+/m44eXOUAxSNdHRkNZPYz5vVUbg17hFgOQDE7fZk7li3pZw==",
                is_dev=False,
            ),
            p_url="pkg:npm/postcss@7.0.36",
        ),
        Package(
            name="source-map",
            version="0.6.1",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=138,
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
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/source-map/-/source-map-0.6.1.tgz",
                integrity="sha512-UjgapumWlbMhkBgzT7Ykc5YXUT46F0iKu8SGXq0bcwP5dz/h0Plj6enJqjz1Zbq2l5WaqYnrVbwWOWMyF3F47g==",
                is_dev=False,
            ),
            p_url="pkg:npm/source-map@0.6.1",
        ),
        Package(
            name="supports-color",
            version="6.1.0",
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=143,
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
            metadata=NpmPackageLockEntry(
                resolved="https://registry.npmjs.org/supports-color/-/supports-color-6.1.0.tgz",
                integrity="sha512-qe1jfm1Mg7Nq/NSh6XE24gPXROEVsWHxC1LIx//XNlD9iw7YZQGjZNjYN7xGaEG6iKdA8EtNFW6R0gjnVXp+wQ==",
                is_dev=False,
            ),
            p_url="pkg:npm/supports-color@6.1.0",
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_package_lock(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []

    assert pkgs == expected_packages


def test_parse_package_lock_v2() -> None:
    test_data_path = get_test_data_path("dependencies/javascript/pkg-lock/package-lock-2.json")
    expected_packages = [
        Package(
            name="@types/prop-types",
            version="15.7.5",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=14,
                    ),
                    dependency_type=DependencyType.TRANSITIVE,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackageLockEntry(
                resolved=("https://registry.npmjs.org/@types/prop-types/-/prop-types-15.7.5.tgz"),
                integrity="sha1-XxnSuFqY6VWANvajysyIGUIPBc8=",
            ),
            p_url="pkg:npm/%40types/prop-types@15.7.5",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="@types/react",
            version="18.0.17",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=20,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackageLockEntry(
                resolved=("https://registry.npmjs.org/@types/react/-/react-18.0.17.tgz"),
                integrity="sha1-RYPZwyLWfv5LOak10iPtzHBQzPQ=",
            ),
            p_url="pkg:npm/%40types/react@18.0.17",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="@types/scheduler",
            version="0.16.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=31,
                    ),
                    dependency_type=DependencyType.TRANSITIVE,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackageLockEntry(
                resolved=("https://registry.npmjs.org/@types/scheduler/-/scheduler-0.16.2.tgz"),
                integrity="sha1-GmL4lSVyPd4kuhsBsJK/XfitTTk=",
            ),
            p_url="pkg:npm/%40types/scheduler@0.16.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="csstype",
            version="3.1.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=37,
                    ),
                    dependency_type=DependencyType.TRANSITIVE,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackageLockEntry(
                resolved=("https://registry.npmjs.org/csstype/-/csstype-3.1.0.tgz"),
                integrity="sha1-TdysNxjXh8+d8NG30VAzklyPKfI=",
            ),
            p_url="pkg:npm/csstype@3.1.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
    ]
    expected_relations = [
        Relationship(
            from_=Package(
                name="@types/prop-types",
                version="15.7.5",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=(test_data_path),
                            file_system_id=None,
                            line=14,
                        ),
                        dependency_type=DependencyType.TRANSITIVE,
                        access_path=(test_data_path),
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=NpmPackageLockEntry(
                    resolved=(
                        "https://registry.npmjs.org/@types/prop-types/-/prop-types-15.7.5.tgz"
                    ),
                    integrity="sha1-XxnSuFqY6VWANvajysyIGUIPBc8=",
                ),
                p_url="pkg:npm/%40types/prop-types@15.7.5",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="@types/react",
                version="18.0.17",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=20,
                        ),
                        dependency_type=DependencyType.DIRECT,
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=NpmPackageLockEntry(
                    resolved=("https://registry.npmjs.org/@types/react/-/react-18.0.17.tgz"),
                    integrity="sha1-RYPZwyLWfv5LOak10iPtzHBQzPQ=",
                ),
                p_url="pkg:npm/%40types/react@18.0.17",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
        Relationship(
            from_=Package(
                name="@types/scheduler",
                version="0.16.2",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=(test_data_path),
                            file_system_id=None,
                            line=31,
                        ),
                        dependency_type=DependencyType.TRANSITIVE,
                        access_path=(test_data_path),
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=NpmPackageLockEntry(
                    resolved=("https://registry.npmjs.org/@types/scheduler/-/scheduler-0.16.2.tgz"),
                    integrity="sha1-GmL4lSVyPd4kuhsBsJK/XfitTTk=",
                ),
                p_url="pkg:npm/%40types/scheduler@0.16.2",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="@types/react",
                version="18.0.17",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=(test_data_path),
                            file_system_id=None,
                            line=20,
                        ),
                        dependency_type=DependencyType.DIRECT,
                        access_path=(test_data_path),
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=NpmPackageLockEntry(
                    resolved=("https://registry.npmjs.org/@types/react/-/react-18.0.17.tgz"),
                    integrity="sha1-RYPZwyLWfv5LOak10iPtzHBQzPQ=",
                ),
                p_url="pkg:npm/%40types/react@18.0.17",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
        Relationship(
            from_=Package(
                name="csstype",
                version="3.1.0",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=37,
                        ),
                        dependency_type=DependencyType.TRANSITIVE,
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=NpmPackageLockEntry(
                    resolved=("https://registry.npmjs.org/csstype/-/csstype-3.1.0.tgz"),
                    integrity="sha1-TdysNxjXh8+d8NG30VAzklyPKfI=",
                ),
                p_url="pkg:npm/csstype@3.1.0",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="@types/react",
                version="18.0.17",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=20,
                        ),
                        dependency_type=DependencyType.DIRECT,
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=NpmPackageLockEntry(
                    resolved=("https://registry.npmjs.org/@types/react/-/react-18.0.17.tgz"),
                    integrity="sha1-RYPZwyLWfv5LOak10iPtzHBQzPQ=",
                ),
                p_url="pkg:npm/%40types/react@18.0.17",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
    ]
    with Path(test_data_path).open(
        encoding="utf-8",
    ) as reader:
        pkgs, relationships = parse_package_lock(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        for rel in relationships:
            rel.from_.health_metadata = None
            rel.from_.licenses = []
            rel.to_.health_metadata = None
            rel.to_.licenses = []
    assert pkgs == expected_packages
    assert relationships == expected_relations


def test_parse_package_lock_v3() -> None:
    test_data_path = get_test_data_path("dependencies/javascript/pkg-lock/package-lock-3.json")
    expected_packages = [
        Package(
            name="@types/prop-types",
            version="15.7.5",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=14,
                    ),
                    dependency_type=DependencyType.TRANSITIVE,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackageLockEntry(
                resolved=("https://registry.npmjs.org/@types/prop-types/-/prop-types-15.7.5.tgz"),
                integrity=(
                    "sha512-JCB8C6SnDoQf0cNycqd/35A7MjcnK+ZTqE7judS6o7u"
                    "txUCg6imJg3QK2qzHKszlTjcj2cn+NwMB2i96ubpj7w=="
                ),
            ),
            p_url="pkg:npm/%40types/prop-types@15.7.5",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="@types/react",
            version="18.0.20",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=19,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackageLockEntry(
                resolved=("https://registry.npmjs.org/@types/react/-/react-18.0.20.tgz"),
                integrity=(
                    "sha512-MWul1teSPxujEHVwZl4a5HxQ9vVNsjTchVA"
                    "+xRqv/VYGCuKGAU6UhfrTdF5aBefwD1BHUD8i/zq+O/vyCm/FrA=="
                ),
            ),
            p_url="pkg:npm/%40types/react@18.0.20",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="@types/scheduler",
            version="0.16.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=29,
                    ),
                    dependency_type=DependencyType.TRANSITIVE,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackageLockEntry(
                resolved=("https://registry.npmjs.org/@types/scheduler/-/scheduler-0.16.2.tgz"),
                integrity=(
                    "sha512-hppQEBDmlwhFAXKJX2KnWLYu5yMfi91yazPb2l"
                    "+lbJiwW+wdo1gNeRA+3RgNSO39WYX2euey41KEwnqesU2Jew=="
                ),
            ),
            p_url="pkg:npm/%40types/scheduler@0.16.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="csstype",
            version="3.1.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=34,
                    ),
                    dependency_type=DependencyType.TRANSITIVE,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackageLockEntry(
                resolved=("https://registry.npmjs.org/csstype/-/csstype-3.1.1.tgz"),
                integrity=(
                    "sha512-DJR/VvkAvSZW9bTouZue2sSxDwdTN92uHjqeKVm"
                    "+0dAqdfNykRzQ95tay8aXMBAAPpUiq4Qcug2L7neoRh2Egw=="
                ),
            ),
            p_url="pkg:npm/csstype@3.1.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
    ]

    expected_relations = [
        Relationship(
            from_=Package(
                name="@types/prop-types",
                version="15.7.5",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=14,
                        ),
                        dependency_type=DependencyType.TRANSITIVE,
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=NpmPackageLockEntry(
                    resolved=(
                        "https://registry.npmjs.org/@types/prop-types/-/prop-types-15.7.5.tgz"
                    ),
                    integrity=(
                        "sha512-JCB8C6SnDoQf0cNycqd/35A7MjcnK+ZTqE7judS"
                        "6o7utxUCg6imJg3QK2qzHKszlTjcj2cn+NwMB2i96ubpj7w=="
                    ),
                ),
                p_url="pkg:npm/%40types/prop-types@15.7.5",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="@types/react",
                version="18.0.20",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=19,
                        ),
                        dependency_type=DependencyType.DIRECT,
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=NpmPackageLockEntry(
                    resolved=("https://registry.npmjs.org/@types/react/-/react-18.0.20.tgz"),
                    integrity=(
                        "sha512-MWul1teSPxujEHVwZl4a5HxQ9vVNsjTchVA"
                        "+xRqv/VYGCuKGAU6UhfrTdF5aBefwD1BHUD8i/zq+O/vyCm/FrA=="
                    ),
                ),
                p_url="pkg:npm/%40types/react@18.0.20",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
        Relationship(
            from_=Package(
                name="@types/scheduler",
                version="0.16.2",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=29,
                        ),
                        dependency_type=DependencyType.TRANSITIVE,
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=NpmPackageLockEntry(
                    resolved=("https://registry.npmjs.org/@types/scheduler/-/scheduler-0.16.2.tgz"),
                    integrity=(
                        "sha512-hppQEBDmlwhFAXKJX2KnWLYu5yMfi91yazPb2l"
                        "+lbJiwW+wdo1gNeRA+3RgNSO39WYX2euey41KEwnqesU2Jew=="
                    ),
                ),
                p_url="pkg:npm/%40types/scheduler@0.16.2",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="@types/react",
                version="18.0.20",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=19,
                        ),
                        dependency_type=DependencyType.DIRECT,
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=NpmPackageLockEntry(
                    resolved=("https://registry.npmjs.org/@types/react/-/react-18.0.20.tgz"),
                    integrity=(
                        "sha512-MWul1teSPxujEHVwZl4a5HxQ9vVNsjTchVA"
                        "+xRqv/VYGCuKGAU6UhfrTdF5aBefwD1BHUD8i/zq+O/vyCm/FrA=="
                    ),
                ),
                p_url="pkg:npm/%40types/react@18.0.20",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
        Relationship(
            from_=Package(
                name="csstype",
                version="3.1.1",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=34,
                        ),
                        dependency_type=DependencyType.TRANSITIVE,
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=NpmPackageLockEntry(
                    resolved=("https://registry.npmjs.org/csstype/-/csstype-3.1.1.tgz"),
                    integrity=(
                        "sha512-DJR/VvkAvSZW9bTouZue2sSxDwdTN92uHjqeKVm"
                        "+0dAqdfNykRzQ95tay8aXMBAAPpUiq4Qcug2L7neoRh2Egw=="
                    ),
                ),
                p_url="pkg:npm/csstype@3.1.1",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="@types/react",
                version="18.0.20",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=19,
                        ),
                        dependency_type=DependencyType.DIRECT,
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=NpmPackageLockEntry(
                    resolved=("https://registry.npmjs.org/@types/react/-/react-18.0.20.tgz"),
                    integrity=(
                        "sha512-MWul1teSPxujEHVwZl4a5HxQ9vVNsjTchVA"
                        "+xRqv/VYGCuKGAU6UhfrTdF5aBefwD1BHUD8i/zq+O/vyCm/FrA=="
                    ),
                ),
                p_url="pkg:npm/%40types/react@18.0.20",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
    ]

    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, relationships = parse_package_lock(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        for rel in relationships:
            rel.from_.health_metadata = None
            rel.from_.licenses = []
            rel.to_.health_metadata = None
            rel.to_.licenses = []
    assert pkgs == expected_packages
    assert relationships == expected_relations


def test_get_direct_dependencies_with_invalid_details() -> None:
    package_lock = IndexedDict[str, ParsedValue]()
    dependencies = IndexedDict[str, ParsedValue]()

    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    dependencies[("invalid-package", position)] = (["requires", "transitive-package"], position)

    dependencies[("transitive-package", position)] = (IndexedDict[str, ParsedValue](), position)

    package_lock[("dependencies", position)] = (dependencies, position)

    result = get_direct_dependencies(package_lock)

    assert result == ["invalid-package", "transitive-package"]


def test_get_direct_dependencies_with_invalid_all_dependencies(
    caplog: pytest.LogCaptureFixture,
) -> None:
    package_lock = IndexedDict[str, ParsedValue]()

    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    package_lock[("packages", position)] = (["invalid-package"], position)

    with caplog.at_level(logging.WARNING):
        result = get_direct_dependencies_v2_v3(package_lock)
        assert "No direct deps found found in package JSON" in caplog.text
        assert result == []


def test_get_direct_dependencies_with_invalid_deps_candidate() -> None:
    package_lock = IndexedDict[str, ParsedValue]()
    packages = IndexedDict[str, ParsedValue]()

    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    package_details = IndexedDict[str, ParsedValue]()
    package_details[("dependencies", position)] = (["invalid-dependency"], position)
    packages[("", position)] = (package_details, position)

    package_lock[("packages", position)] = (packages, position)

    result = get_direct_dependencies_v2_v3(package_lock)
    assert result == []


def test_get_direct_dependencies_with_invalid_dev_deps_candidate() -> None:
    package_lock = IndexedDict[str, ParsedValue]()
    packages = IndexedDict[str, ParsedValue]()

    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    package_details = IndexedDict[str, ParsedValue]()
    package_details[("devDependencies", position)] = (["invalid-dev-dependency"], position)
    packages[("", position)] = (package_details, position)

    package_lock[("packages", position)] = (packages, position)

    result = get_direct_dependencies_v2_v3(package_lock)
    assert result == []


def test_get_direct_dependencies_with_invalid_dep_value() -> None:
    package_lock = IndexedDict[str, ParsedValue]()
    packages = IndexedDict[str, ParsedValue]()

    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    packages[("invalid-package", position)] = (["not-a-dict"], position)

    package_lock[("packages", position)] = (packages, position)

    result = get_direct_dependencies_v2_v3(package_lock)
    assert result == []


def test_solve_sub_dependencies_with_invalid_dep_value() -> None:
    reader = LocationReadCloser(
        location=new_location("test/path"),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    sub_deps = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    sub_deps[("invalid-package", position)] = (["not-a-dict"], position)

    result = _solve_sub_dependencies(reader, sub_deps)
    assert result == []


def test_solve_sub_dependencies_with_none_package() -> None:
    reader = LocationReadCloser(
        location=new_location("test/path"),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    sub_deps = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    package_details = IndexedDict[str, ParsedValue]()
    package_details[("name", position)] = (
        None,
        position,
    )
    sub_deps[("invalid-package", position)] = (package_details, position)

    result = _solve_sub_dependencies(reader, sub_deps)
    assert result == []


def test_handle_v1_with_invalid_deps(caplog: pytest.LogCaptureFixture) -> None:
    reader = LocationReadCloser(
        location=new_location("test/path"),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    package_json = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    dependencies = IndexedDict[str, ParsedValue]()
    dependencies[("invalid-dep", position)] = ("not-a-dict", position)
    package_json[("dependencies", position)] = (dependencies, position)

    with caplog.at_level(logging.WARNING):
        packages, relationships = handle_v1(reader, package_json)
        assert packages == []
        assert relationships == []


def test_handle_v1_with_non_dict_dependency_value() -> None:
    reader = LocationReadCloser(
        location=new_location("test/path"),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    package_json = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    dependencies = IndexedDict[str, ParsedValue]()
    dependencies[("test-package", position)] = (["not-a-dict"], position)
    package_json[("dependencies", position)] = (dependencies, position)

    packages, relationships = handle_v1(reader, package_json)
    assert packages == []
    assert relationships == []


def test_solve_sub_dependencies_with_non_dict_nested_deps() -> None:
    reader = LocationReadCloser(
        location=new_location("test/path"),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    sub_deps = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    package_details = IndexedDict[str, ParsedValue]()
    package_details[("dependencies", position)] = (["not-a-dict"], position)
    sub_deps[("test-package", position)] = (package_details, position)

    result = _solve_sub_dependencies(reader, sub_deps)
    assert result == []


def test_handle_v1_with_none_package() -> None:
    reader = LocationReadCloser(
        location=new_location("test/path"),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    package_json = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    dependencies = IndexedDict[str, ParsedValue]()
    package_details = IndexedDict[str, ParsedValue]()

    package_details[("name", position)] = (None, position)
    dependencies[("test-package", position)] = (package_details, position)
    package_json[("dependencies", position)] = (dependencies, position)

    packages, relationships = handle_v1(reader, package_json)
    assert packages == []
    assert relationships == []


def test_get_name_with_name_in_package_value() -> None:
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    package_value = IndexedDict[str, ParsedValue]()
    package_value[("name", position)] = ("test-package", position)

    result = _get_name("", package_value)
    assert result == "test-package"


def test_get_name_without_name_in_package_value() -> None:
    package_value = IndexedDict[str, ParsedValue]()

    result = _get_name("test-package", package_value)
    assert result == "test-package"


def test_get_name_returns_none() -> None:
    package_value = IndexedDict[str, ParsedValue]()

    result = _get_name("", package_value)
    assert result is None


def test_handle_v2_with_invalid_packages(caplog: pytest.LogCaptureFixture) -> None:
    reader = LocationReadCloser(
        location=new_location("test/path"),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    package_json = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    package_json[("packages", position)] = (["not-a-dict"], position)

    with caplog.at_level(logging.WARNING):
        packages, relationships = handle_v2(reader, package_json)
        assert "No packages found in package JSON" in caplog.text
        assert packages == []
        assert relationships == []


def test_handle_v2_with_none_package() -> None:
    reader = LocationReadCloser(
        location=new_location("test/path"),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    package_json = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    packages_dict = IndexedDict[str, ParsedValue]()
    package_details = IndexedDict[str, ParsedValue]()

    package_details[("name", position)] = (None, position)
    packages_dict[("test-package", position)] = (package_details, position)
    package_json[("packages", position)] = (packages_dict, position)

    result_packages, relationships = handle_v2(reader, package_json)
    assert result_packages == []
    assert relationships == []


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.cataloger.javascript.parse_package_lock,
            target="get_direct_dependencies",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_handle_v1_with_none_direct_dependencies(caplog: pytest.LogCaptureFixture) -> None:
    reader = LocationReadCloser(
        location=new_location("test/path"),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    package_json = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    package_json[("dependencies", position)] = (["not-a-dict"], position)

    with caplog.at_level(logging.WARNING):
        packages, relationships = handle_v1(reader, package_json)
        assert "No packages found in package JSON" in caplog.text
        assert packages == []
        assert relationships == []


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.cataloger.javascript.parse_package_lock,
            target="get_direct_dependencies_v2_v3",
            target_type="sync",
            expected=["test-package"],
        ),
        Mock(
            module=labels.parsers.cataloger.javascript.parse_package_lock,
            target="new_package_lock_v2",
            target_type="sync",
            expected=Package(
                name="test-package",
                version="1.0.0",
                language=Language.JAVASCRIPT,
                licenses=[],
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path="test/path",
                            file_system_id=None,
                            line=1,
                        ),
                        dependency_type=DependencyType.DIRECT,
                        access_path="test/path",
                        annotations={},
                    ),
                ],
                type=PackageType.NpmPkg,
                metadata=NpmPackageLockEntry(
                    resolved="https://registry.npmjs.org/test-package/-/test-package-1.0.0.tgz",
                    integrity="sha1-test",
                ),
                p_url="pkg:npm/test-package@1.0.0",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
        ),
    ],
)
async def test_handle_v2_with_non_dict_dependencies() -> None:
    reader = LocationReadCloser(
        location=new_location("test/path"),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    package_json = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    packages_dict = IndexedDict[str, ParsedValue]()
    package_details = IndexedDict[str, ParsedValue]()
    package_details[("name", position)] = ("test-package", position)
    package_details[("version", position)] = ("1.0.0", position)
    package_details[("dependencies", position)] = (["not-a-dict"], position)
    packages_dict[("test-package", position)] = (package_details, position)
    package_json[("packages", position)] = (packages_dict, position)

    _, relationships = handle_v2(reader, package_json)
    assert relationships == []


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.cataloger.javascript.parse_package_lock,
            target="new_package_lock_v2",
            target_type="sync",
            expected=Package(
                name="main-package",
                version="1.0.0",
                language=Language.JAVASCRIPT,
                licenses=[],
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path="test/path",
                            file_system_id=None,
                            line=1,
                        ),
                        dependency_type=DependencyType.DIRECT,
                        access_path="test/path",
                        annotations={},
                    ),
                ],
                type=PackageType.NpmPkg,
                metadata=NpmPackageLockEntry(
                    resolved="https://registry.npmjs.org/main-package/-/main-package-1.0.0.tgz",
                    integrity="sha1-test",
                ),
                p_url="pkg:npm/main-package@1.0.0",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
        ),
    ],
)
async def test_handle_v2_with_missing_dependency_package() -> None:
    reader = LocationReadCloser(
        location=new_location("test/path"),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    package_json = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )

    packages_dict = IndexedDict[str, ParsedValue]()
    package_details = IndexedDict[str, ParsedValue]()

    package_details[("name", position)] = ("main-package", position)
    package_details[("version", position)] = ("1.0.0", position)

    dependencies = IndexedDict[str, ParsedValue]()
    dependencies[("missing-dependency", position)] = ("1.0.0", position)
    package_details[("dependencies", position)] = (dependencies, position)

    packages_dict[("main-package", position)] = (package_details, position)
    package_json[("packages", position)] = (packages_dict, position)

    packages, relationships = handle_v2(reader, package_json)

    assert len(relationships) == 0
    assert len(packages) == 1


def test_parse_package_lock_with_invalid_version() -> None:
    package_json = {
        "lockfileVersion": 999,
        "dependencies": {
            "test-package": {
                "version": "1.0.0",
            },
        },
    }

    json_str = json.dumps(package_json)
    reader = LocationReadCloser(
        location=new_location("test/path"),
        read_closer=TextIOWrapper(BytesIO(json_str.encode())),
    )

    packages, relationships = parse_package_lock(
        None,
        None,
        reader,
    )

    assert len(packages) == 0
    assert len(relationships) == 0
