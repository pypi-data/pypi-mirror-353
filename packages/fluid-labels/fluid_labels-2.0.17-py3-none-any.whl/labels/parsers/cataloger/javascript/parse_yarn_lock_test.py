from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship, RelationshipType
from labels.parsers.cataloger.javascript.model import YarnLockEntry
from labels.parsers.cataloger.javascript.parse_yarn_lock import (
    YarnPackage,
    _extract_packages,
    _extract_relationships,
    parse_yarn_lock,
)
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_yarn_lock() -> None:
    test_data_path = get_test_data_path("dependencies/javascript/yarn/yarn.lock")
    expected_packages = [
        Package(
            name="@babel/code-frame",
            version="7.10.4",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=5,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(
                resolved=(
                    "https://registry.yarnpkg.com/@babel/code-frame/-"
                    "/code-frame-7.10.4.tgz"
                    "#168da1a36e90da68ae8d49c0f1b48c7c6249213a"
                ),
                integrity=(
                    "sha512-vG6SvB6oYEhvgisZNFRmRCUkLz11c7rp+tbNTynGqc6m"
                    "S1d5ATd/sGyV6W0KZZnXRKMTzZDRgQT3Ou9jhpAfUg=="
                ),
            ),
            p_url="pkg:npm/%40babel/code-frame@7.10.4",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="@types/minimatch",
            version="3.0.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=12,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(
                resolved=(
                    "https://registry.yarnpkg.com/@types"
                    "/minimatch/-/minimatch-3.0.3.tgz"
                    "#3dca0e3f33b200fc7d1139c0cd96c1268cadfd9d"
                ),
                integrity=(
                    "sha512-tHq6qdbT9U1IRSGf14CL0pUlULksvY9OZ+5eEgl1N7t+"
                    "OA3tGvNpxJCzuKQlsNgCVwbAs670L1vcVQi8j9HjnA=="
                ),
            ),
            p_url="pkg:npm/%40types/minimatch@3.0.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="@types/qs",
            version="6.9.4",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=22,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(
                resolved=(
                    "https://registry.yarnpkg.com/@types"
                    "/qs/-/qs-6.9.4.tgz"
                    "#a59e851c1ba16c0513ea123830dd639a0a15cb6a"
                ),
                integrity=(
                    "sha512-+wYo+L6ZF6BMoEjtf8zB2esQsqdV6WsjRK/GP9WOgLP"
                    "rq87PbNWgIxS76dS5uvl/QXtHGakZmwTznIfcPXcKlQ=="
                ),
            ),
            p_url="pkg:npm/%40types/qs@6.9.4",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="ajv",
            version="6.12.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=27,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(
                resolved=(
                    "https://registry.yarnpkg.com/ajv/-/ajv-6.12.3.tgz"
                    "#18c5af38a111ddeb4f2697bd78d68abc1cabd706"
                ),
                integrity=(
                    "sha512-4K0cK3L1hsqk9xIb2z9vs/XU+PGJZ9PNpJRDS9YLzmNdX6jmVP"
                    "famLvTJr0aDAusnHyCHO6MjzlkAsgtqp9teA=="
                ),
            ),
            p_url="pkg:npm/ajv@6.12.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="atob",
            version="2.1.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=42,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(
                resolved=(
                    "https://registry.yarnpkg.com/atob/-/atob-2.1.2.tgz"
                    "#6d9517eb9e030d2436666651e86bd9f6f13533c9"
                ),
                integrity=(
                    "sha512-Wm6ukoaOGJi/73p/cl2GvLjTI5JM1k/O14isD73YM"
                    "L8StrH/7/lRFgmg8nICZgD3bZZvjwCGxtMOD3wWNAu8cg=="
                ),
            ),
            p_url="pkg:npm/atob@2.1.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="aws-sdk",
            version="2.706.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=47,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(
                resolved=(
                    "https://registry.yarnpkg.com/aws-sdk/-"
                    "/aws-sdk-2.706.0.tgz"
                    "#09f65e9a91ecac5a635daf934082abae30eca953"
                ),
                integrity=(
                    "sha512-7GT+yrB5Wb/zOReRdv/Pzkb2Qt+hz6B/8FGMVaoys"
                    "X3NryHvQUdz7EQWi5yhg9CxOjKxdw5lFwYSs69YlSp1KA=="
                ),
            ),
            p_url="pkg:npm/aws-sdk@2.706.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="jhipster-core",
            version="7.3.4",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=62,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(
                resolved=(
                    "https://registry.yarnpkg.com/jhipster-core/-"
                    "/jhipster-core-7.3.4.tgz"
                    "#c34b8c97c7f4e8b7518dae015517e2112c73cc80"
                ),
                integrity=(
                    "sha512-AUhT69kNkqppaJZVfan/xnKG4Gs9Ggj7YLtTZFVe+xg"
                    "+THrbMb5Ng7PL07PDlDw4KAEA33GMCwuAf65E8EpC4g=="
                ),
            ),
            p_url="pkg:npm/jhipster-core@7.3.4",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="asn1.js",
            version="4.10.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=72,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(
                resolved=(
                    "https://registry.yarnpkg.com/asn1.js/-"
                    "/asn1.js-4.10.1.tgz"
                    "#b9c2bf5805f1e64aadeed6df3a2bfafb5a73f5a0"
                ),
                integrity=(
                    "sha512-p32cOF5q0Zqs9uBiONKYLm6BClCoBCM5O9JfeUSlnQL"
                    "BTxYdTK+pW+nXflm8UkKd2UYlEbYz5qEi0JuZR9ckSw=="
                ),
            ),
            p_url="pkg:npm/asn1.js@4.10.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="c0n-fab_u.laTION",
            version="7.7.7",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=81,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(
                resolved=(
                    "https://registry.yarnpkg.com/something-i-made-up/-"
                    "/c0n-fab_u.laTION-7.7.7.tgz"
                    "#b9c2bf5805f1e64aadeed6df3a2bfafb5a73f5a0"
                ),
                integrity=(
                    "sha512-p32cOF5q0Zqs9uBiONKYLm6BClCoBCM5O9JfeUSlnQL"
                    "BTxYdTK+pW+nXflm8UkKd2UYlEbYz5qEi0JuZR9ckSw=="
                ),
            ),
            p_url="pkg:npm/c0n-fab_u.laTION@7.7.7",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_yarn_lock(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        assert pkgs == expected_packages


def test_parse_yarn_berry() -> None:
    test_data_path = get_test_data_path("dependencies/javascript/yarn-berry/yarn.lock")
    expected_packages = [
        Package(
            name="@babel/code-frame",
            version="7.10.4",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=8,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(resolved=None, integrity=None),
            p_url="pkg:npm/%40babel/code-frame@7.10.4",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="@types/minimatch",
            version="3.0.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=17,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(resolved=None, integrity=None),
            p_url="pkg:npm/%40types/minimatch@3.0.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="@types/qs",
            version="6.9.4",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=31,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(resolved=None, integrity=None),
            p_url="pkg:npm/%40types/qs@6.9.4",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="ajv",
            version="6.12.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=38,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(resolved=None, integrity=None),
            p_url="pkg:npm/ajv@6.12.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="atob",
            version="2.1.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=50,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(resolved=None, integrity=None),
            p_url="pkg:npm/atob@2.1.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="aws-sdk",
            version="2.706.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=59,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(resolved=None, integrity=None),
            p_url="pkg:npm/aws-sdk@2.706.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="jhipster-core",
            version="7.3.4",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=76,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(resolved=None, integrity=None),
            p_url="pkg:npm/jhipster-core@7.3.4",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="asn1.js",
            version="4.10.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=88,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(resolved=None, integrity=None),
            p_url="pkg:npm/asn1.js@4.10.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="newtest",
            version="7.7.7",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=99,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=YarnLockEntry(resolved=None, integrity=None),
            p_url="pkg:npm/newtest@7.7.7",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
    ]

    expected_relationships = [
        Relationship(
            from_=Package(
                name="@babel/code-frame",
                version="7.10.4",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=8,
                        ),
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=YarnLockEntry(resolved=None, integrity=None),
                p_url="pkg:npm/%40babel/code-frame@7.10.4",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="newtest",
                version="7.7.7",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=99,
                        ),
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=YarnLockEntry(resolved=None, integrity=None),
                p_url="pkg:npm/newtest@7.7.7",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
        Relationship(
            from_=Package(
                name="@types/minimatch",
                version="3.0.3",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=17,
                        ),
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=YarnLockEntry(resolved=None, integrity=None),
                p_url="pkg:npm/%40types/minimatch@3.0.3",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="newtest",
                version="7.7.7",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=99,
                        ),
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=YarnLockEntry(resolved=None, integrity=None),
                p_url="pkg:npm/newtest@7.7.7",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
        Relationship(
            from_=Package(
                name="@types/qs",
                version="6.9.4",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=31,
                        ),
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=YarnLockEntry(resolved=None, integrity=None),
                p_url="pkg:npm/%40types/qs@6.9.4",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="newtest",
                version="7.7.7",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=99,
                        ),
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=YarnLockEntry(resolved=None, integrity=None),
                p_url="pkg:npm/newtest@7.7.7",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
        Relationship(
            from_=Package(
                name="ajv",
                version="6.12.3",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=38,
                        ),
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=YarnLockEntry(resolved=None, integrity=None),
                p_url="pkg:npm/ajv@6.12.3",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="newtest",
                version="7.7.7",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=99,
                        ),
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=YarnLockEntry(resolved=None, integrity=None),
                p_url="pkg:npm/newtest@7.7.7",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
        Relationship(
            from_=Package(
                name="asn1.js",
                version="4.10.1",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=88,
                        ),
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=YarnLockEntry(resolved=None, integrity=None),
                p_url="pkg:npm/asn1.js@4.10.1",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="newtest",
                version="7.7.7",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=99,
                        ),
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=YarnLockEntry(resolved=None, integrity=None),
                p_url="pkg:npm/newtest@7.7.7",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
        Relationship(
            from_=Package(
                name="atob",
                version="2.1.2",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=50,
                        ),
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=YarnLockEntry(resolved=None, integrity=None),
                p_url="pkg:npm/atob@2.1.2",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="newtest",
                version="7.7.7",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=99,
                        ),
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                metadata=YarnLockEntry(resolved=None, integrity=None),
                p_url="pkg:npm/newtest@7.7.7",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
    ]

    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, relationships = parse_yarn_lock(
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
        assert relationships == expected_relationships


def test_parse_yarn_lock_with_none_name() -> None:
    test_data_path = get_test_data_path("dependencies/javascript/yarn/yarn.lock")
    reader = TextIOWrapper(BytesIO(b"test"))
    yarn_package: YarnPackage = {"version": "", "line": 1, "checksum": ""}
    parsed_yarn_lock = {("pkg", "1.0.0"): yarn_package}
    pkgs = _extract_packages(
        parsed_yarn_lock,
        LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
    )
    assert len(pkgs) == 0


def test_parse_yarn_lock_with_no_coordinates() -> None:
    test_data_path = get_test_data_path("dependencies/javascript/yarn/yarn.lock")
    reader = TextIOWrapper(BytesIO(b"test"))
    yarn_package: YarnPackage = {"version": "1.0.0", "line": 1, "checksum": ""}
    parsed_yarn_lock = {("pkg", "1.0.0"): yarn_package}
    location = new_location(test_data_path)
    location.coordinates = None
    pkgs = _extract_packages(
        parsed_yarn_lock,
        LocationReadCloser(location=location, read_closer=reader),
    )
    assert len(pkgs) == 1
    assert pkgs[0].locations[0].coordinates is None


def test_extract_relationships_with_none_package() -> None:
    yarn_package: YarnPackage = {
        "version": "1.0.0",
        "line": 1,
        "checksum": "",
        "dependencies": [("dep", "1.0.0")],
    }
    parsed_yarn_lock = {("pkg", "1.0.0"): yarn_package}
    packages: list[Package] = []
    relationships = _extract_relationships(parsed_yarn_lock, packages)
    assert len(relationships) == 0


def test_extract_packages_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    test_data_path = get_test_data_path("dependencies/javascript/yarn/yarn.lock")
    reader = TextIOWrapper(BytesIO(b"test"))
    yarn_package: YarnPackage = {"version": "1.0.0", "line": 1, "checksum": ""}
    parsed_yarn_lock = {("pkg", "1.0.0"): yarn_package}

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

        pkgs = _extract_packages(
            parsed_yarn_lock,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )

        assert len(pkgs) == 0
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )
