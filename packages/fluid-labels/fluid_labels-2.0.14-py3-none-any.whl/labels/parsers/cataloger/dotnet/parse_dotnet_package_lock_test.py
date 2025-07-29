from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser
from labels.model.indexables import FileCoordinate, IndexedDict, ParsedValue, Position
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship, RelationshipType
from labels.parsers.cataloger.dotnet.parse_dotnet_package_lock import (
    _get_relationships,
    parse_dotnet_package_lock,
)
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_dotnet_package_lock() -> None:
    test_data_path = get_test_data_path("dependencies/dotnet/packages.lock.json")
    expected_packages = [
        Package(
            name="Grpc.Core",
            version="2.44.0",
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
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/Grpc.Core@2.44.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="Grpc.Core.Api",
            version="2.44.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=13,
                    ),
                    dependency_type=DependencyType.TRANSITIVE,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/Grpc.Core.Api@2.44.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="Microsoft.Extensions.DependencyInjection.Abstractions",
            version="5.0.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=21,
                    ),
                    dependency_type=DependencyType.TRANSITIVE,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url=("pkg:nuget/Microsoft.Extensions.DependencyInjection.Abstractions@5.0.0"),
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="Serilog",
            version="2.10.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=26,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/Serilog@2.10.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="System.Memory",
            version="4.5.3",
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
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/System.Memory@4.5.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="Wire",
            version="1.0.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=37,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/Wire@1.0.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="dep1",
            version="1.0.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=42,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/dep1@1.0.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="dep2",
            version="2.0.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=50,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/dep2@2.0.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
    ]

    expected_relations = [
        Relationship(
            from_=Package(
                name="Grpc.Core.Api",
                version="2.44.0",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=13,
                        ),
                        dependency_type=DependencyType.TRANSITIVE,
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.DOTNET,
                licenses=[],
                type=PackageType.DotnetPkg,
                metadata=None,
                p_url="pkg:nuget/Grpc.Core.Api@2.44.0",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="Grpc.Core",
                version="2.44.0",
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
                language=Language.DOTNET,
                licenses=[],
                type=PackageType.DotnetPkg,
                metadata=None,
                p_url="pkg:nuget/Grpc.Core@2.44.0",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
        Relationship(
            from_=Package(
                name="System.Memory",
                version="4.5.3",
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
                language=Language.DOTNET,
                licenses=[],
                type=PackageType.DotnetPkg,
                metadata=None,
                p_url="pkg:nuget/System.Memory@4.5.3",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="Grpc.Core",
                version="2.44.0",
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
                language=Language.DOTNET,
                licenses=[],
                type=PackageType.DotnetPkg,
                metadata=None,
                p_url="pkg:nuget/Grpc.Core@2.44.0",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
        Relationship(
            from_=Package(
                name="System.Memory",
                version="4.5.3",
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
                language=Language.DOTNET,
                licenses=[],
                type=PackageType.DotnetPkg,
                metadata=None,
                p_url="pkg:nuget/System.Memory@4.5.3",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="Grpc.Core.Api",
                version="2.44.0",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=13,
                        ),
                        dependency_type=DependencyType.TRANSITIVE,
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.DOTNET,
                licenses=[],
                type=PackageType.DotnetPkg,
                metadata=None,
                p_url="pkg:nuget/Grpc.Core.Api@2.44.0",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
        Relationship(
            from_=Package(
                name="Grpc.Core",
                version="2.44.0",
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
                language=Language.DOTNET,
                licenses=[],
                type=PackageType.DotnetPkg,
                metadata=None,
                p_url="pkg:nuget/Grpc.Core@2.44.0",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="dep1",
                version="1.0.0",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=42,
                        ),
                        dependency_type=DependencyType.DIRECT,
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.DOTNET,
                licenses=[],
                type=PackageType.DotnetPkg,
                metadata=None,
                p_url="pkg:nuget/dep1@1.0.0",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
        Relationship(
            from_=Package(
                name="Microsoft.Extensions.DependencyInjection.Abstractions",
                version="5.0.0",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=21,
                        ),
                        dependency_type=DependencyType.TRANSITIVE,
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.DOTNET,
                licenses=[],
                type=PackageType.DotnetPkg,
                metadata=None,
                p_url=("pkg:nuget/Microsoft.Extensions.DependencyInjection.Abstractions@5.0.0"),
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            to_=Package(
                name="dep2",
                version="2.0.0",
                locations=[
                    Location(
                        coordinates=Coordinates(
                            real_path=test_data_path,
                            file_system_id=None,
                            line=50,
                        ),
                        dependency_type=DependencyType.DIRECT,
                        access_path=test_data_path,
                        annotations={},
                    ),
                ],
                language=Language.DOTNET,
                licenses=[],
                type=PackageType.DotnetPkg,
                metadata=None,
                p_url="pkg:nuget/dep2@2.0.0",
                dependencies=None,
                found_by=None,
                health_metadata=None,
            ),
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, relations = parse_dotnet_package_lock(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        for rel in relations:
            rel.from_.health_metadata = None
            rel.from_.licenses = []
            rel.to_.health_metadata = None
            rel.to_.licenses = []
        assert pkgs == expected_packages
        assert relations == expected_relations


def test_get_relationships() -> None:
    packages = [
        Package(
            name="pkg1",
            version="1.0.0",
            locations=[],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/pkg1@1.0.0",
        ),
        Package(
            name="pkg2",
            version="2.0.0",
            locations=[],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/pkg2@2.0.0",
        ),
    ]

    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=1),
    )

    pkg1_deps = IndexedDict[str, ParsedValue]()
    pkg1_deps[("pkg2", position)] = ("2.0.0", position)

    dependencies: dict[str, ParsedValue] = {
        "pkg1": pkg1_deps,
        "pkg2": IndexedDict[str, ParsedValue](),
    }

    relationships = _get_relationships(packages, dependencies)

    assert len(relationships) == 1
    relationship = relationships[0]
    assert relationship.from_.name == "pkg2"
    assert relationship.to_.name == "pkg1"
    assert relationship.type == RelationshipType.DEPENDENCY_OF_RELATIONSHIP

    invalid_dependencies: dict[str, ParsedValue] = {
        "pkg1": "not_an_indexed_dict",
        "pkg2": IndexedDict[str, ParsedValue](),
    }
    relationships = _get_relationships(packages, invalid_dependencies)
    assert len(relationships) == 0

    non_existent_dependencies: dict[str, ParsedValue] = {
        "non_existent_pkg": IndexedDict[str, ParsedValue](),
    }
    relationships = _get_relationships(packages, non_existent_dependencies)
    assert len(relationships) == 0


def test_parse_dotnet_package_lock_no_deps() -> None:
    json_content = '{"dependencies": "not_an_indexed_dict"}'

    json_bytes = json_content.encode("utf-8")
    json_io = BytesIO(json_bytes)
    reader = TextIOWrapper(json_io, encoding="utf-8")

    pkgs, relations = parse_dotnet_package_lock(
        None,
        None,
        LocationReadCloser(location=new_location("packages.lock.json"), read_closer=reader),
    )
    assert pkgs == []
    assert relations == []


def test_parse_dotnet_package_lock_invalid_package_value() -> None:
    json_content = """{
        "dependencies": {
            "target": {
                "package1": "not_an_indexed_dict",
                "package2": {
                    "type": "Transitive",
                    "resolved": "1.0.0"
                }
            }
        }
    }"""

    json_bytes = json_content.encode("utf-8")
    json_io = BytesIO(json_bytes)
    reader = TextIOWrapper(json_io, encoding="utf-8")

    pkgs, relations = parse_dotnet_package_lock(
        None,
        None,
        LocationReadCloser(location=new_location("packages.lock.json"), read_closer=reader),
    )
    assert len(pkgs) == 1
    assert pkgs[0].name == "package2"
    assert pkgs[0].version == "1.0.0"
    assert len(relations) == 0


def test_parse_dotnet_package_lock_no_coordinates() -> None:
    json_content = """{
        "dependencies": {
            "target": {
                "package1": {
                    "type": "Transitive",
                    "resolved": "1.0.0"
                }
            }
        }
    }"""

    location = Location(
        coordinates=None,
        dependency_type=DependencyType.DIRECT,
        access_path="packages.lock.json",
        annotations={},
    )

    json_bytes = json_content.encode("utf-8")
    json_io = BytesIO(json_bytes)
    reader = TextIOWrapper(json_io, encoding="utf-8")

    pkgs, relations = parse_dotnet_package_lock(
        None,
        None,
        LocationReadCloser(location=location, read_closer=reader),
    )
    assert len(pkgs) == 1
    assert pkgs[0].name == "package1"
    assert pkgs[0].version == "1.0.0"
    assert pkgs[0].locations[0].coordinates is None
    assert pkgs[0].locations[0].dependency_type == DependencyType.DIRECT
    assert len(relations) == 0


def test_parse_dotnet_package_lock_missing_name_or_version() -> None:
    json_content = """{
        "dependencies": {
            "target": {
                "": {
                    "type": "Transitive",
                    "resolved": "1.0.0"
                },
                "package2": {
                    "type": "Transitive",
                    "resolved": ""
                },
                "package3": {
                    "type": "Transitive"
                }
            }
        }
    }"""

    json_bytes = json_content.encode("utf-8")
    json_io = BytesIO(json_bytes)
    reader = TextIOWrapper(json_io, encoding="utf-8")

    pkgs, relations = parse_dotnet_package_lock(
        None,
        None,
        LocationReadCloser(location=new_location("packages.lock.json"), read_closer=reader),
    )
    assert len(pkgs) == 0
    assert len(relations) == 0


def test_parse_dotnet_package_lock_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    json_content = """{
        "dependencies": {
            "target": {
                "package1": {
                    "type": "Transitive",
                    "resolved": "1.0.0"
                }
            }
        }
    }"""

    json_bytes = json_content.encode("utf-8")
    json_io = BytesIO(json_bytes)
    reader = TextIOWrapper(json_io, encoding="utf-8")

    location = Location(
        coordinates=Coordinates(
            real_path="packages.lock.json",
            file_system_id=None,
            line=1,
        ),
        dependency_type=DependencyType.DIRECT,
        access_path="packages.lock.json",
        annotations={},
    )

    with patch("labels.model.package.Package.__init__") as mock_init:
        mock_init.side_effect = ValidationError.from_exception_data(
            title="",
            line_errors=[
                InitErrorDetails(
                    type="missing",
                    loc=("name",),
                    input=None,
                    ctx={},
                ),
            ],
        )

        pkgs, relations = parse_dotnet_package_lock(
            None,
            None,
            LocationReadCloser(location=location, read_closer=reader),
        )
        assert len(pkgs) == 0
        assert len(relations) == 0
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )
