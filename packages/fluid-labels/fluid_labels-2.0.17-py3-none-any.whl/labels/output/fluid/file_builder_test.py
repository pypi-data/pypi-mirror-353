from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel

from labels.model.file import Coordinates, DependencyType, Location, Scope
from labels.model.indexables import FileCoordinate, IndexedDict, IndexedList, Position
from labels.model.package import HealthMetadata, Language, Package, PackageType
from labels.model.relationship import Relationship, RelationshipType
from labels.output.fluid.file_builder import (
    EnumEncoder,
    build_relationship_map,
    build_sbom_metadata,
    serialize_package,
    serialize_packages,
    validate_pkgs,
)
from labels.testing.utils import raises


class TestEnum(Enum):
    TEST = "test"


class TestModel(BaseModel):
    field: str = "test"


def test_enum_encoder() -> None:
    encoder = EnumEncoder()

    assert encoder.default(TestEnum.TEST) == "test"

    indexed_list = IndexedList[str]()
    coord = FileCoordinate(line=1, column=1)
    indexed_list.append(("test", Position(start=coord, end=coord)))
    assert encoder.default(indexed_list) == ["test"]

    indexed_dict = IndexedDict[str, str]()
    coord = FileCoordinate(line=1, column=1)
    pos = Position(start=coord, end=coord)
    indexed_dict[("key", pos)] = ("value", pos)
    assert encoder.default(indexed_dict) == {"key": "value"}

    model = TestModel()
    assert encoder.default(model) == {"field": "test"}

    dt = datetime(2025, 1, 1, tzinfo=UTC)
    assert encoder.default(dt) == "2025-01-01T00:00:00+00:00"

    with raises(TypeError):
        encoder.default(object())


def test_serialize_package() -> None:
    package = Package(
        name="test-package",
        version="1.0.0",
        type=PackageType.PythonPkg,
        language=Language.PYTHON,
        locations=[
            Location(
                coordinates=Coordinates(
                    real_path="/test/path",
                    line=10,
                    file_system_id="fs-1",
                ),
                access_path="/test/path",
                dependency_type=DependencyType.DIRECT,
                scope=Scope.PROD,
            ),
        ],
        licenses=["MIT"],
        p_url="pkg:python/test-package@1.0.0",
        found_by="test-tool",
        health_metadata=HealthMetadata(
            latest_version="2.0.0",
            latest_version_created_at=datetime(2025, 1, 1, tzinfo=UTC),
            authors="Test Author",
            artifact=None,
        ),
        advisories=[],
    )

    result = serialize_package(package)

    assert result["id"] == package.id_by_hash()
    assert result["name"] == "test-package"
    assert result["version"] == "1.0.0"
    assert result["type"] == "python"
    assert result["language"] == "python"
    assert result["platform"] == "PIP"
    assert len(result["locations"]) == 1
    assert result["locations"][0]["path"] == "/test/path"
    assert result["locations"][0]["line"] == 10
    assert result["locations"][0]["layer"] == "fs-1"
    assert result["locations"][0]["dependency_type"] == "DIRECT"
    assert result["locations"][0]["scope"] == "PROD"
    assert result["licenses"] == ["MIT"]
    assert result["package_url"] == "pkg:python/test-package@1.0.0"
    assert result["found_by"] == "test-tool"
    assert result["health_metadata"] == {
        "latest_version": "2.0.0",
        "latest_version_created_at": datetime(2025, 1, 1, 0, 0, tzinfo=UTC),
        "authors": "Test Author",
        "artifact": None,
    }
    assert result["advisories"] == []


def test_serialize_packages() -> None:
    packages = [
        Package(
            name="test-package-1",
            version="1.0.0",
            type=PackageType.PythonPkg,
            language=Language.PYTHON,
            locations=[],
            licenses=[],
            p_url="pkg:python/test-package-1@1.0.0",
            found_by="test-tool",
            health_metadata=HealthMetadata(
                latest_version="2.0.0",
                latest_version_created_at=datetime(2025, 1, 1, tzinfo=UTC),
                authors=None,
                artifact=None,
            ),
        ),
        Package(
            name="test-package-2",
            version="2.0.0",
            type=PackageType.PythonPkg,
            language=Language.PYTHON,
            locations=[],
            licenses=[],
            p_url="pkg:python/test-package-2@2.0.0",
            found_by="test-tool",
        ),
    ]

    result = serialize_packages(packages)
    assert len(result) == 2

    pkg1 = result[0]
    assert pkg1["id"] == packages[0].id_by_hash()
    assert pkg1["name"] == "test-package-1"
    assert pkg1["version"] == "1.0.0"
    assert pkg1["type"] == "python"
    assert pkg1["language"] == "python"
    assert pkg1["platform"] == "PIP"
    assert pkg1["package_url"] == "pkg:python/test-package-1@1.0.0"
    assert pkg1["found_by"] == "test-tool"
    assert pkg1["advisories"] == []
    assert pkg1["locations"] == []

    assert pkg1["health_metadata"]["latest_version"] == "2.0.0"
    assert (
        pkg1["health_metadata"]["latest_version_created_at"]
        == datetime(2025, 1, 1, tzinfo=UTC).isoformat()
    )
    assert pkg1["health_metadata"]["authors"] is None
    assert pkg1["health_metadata"]["artifact"] is None

    pkg2 = result[1]
    assert pkg2["id"] == packages[1].id_by_hash()
    assert pkg2["name"] == "test-package-2"
    assert pkg2["version"] == "2.0.0"
    assert pkg2["type"] == "python"
    assert pkg2["language"] == "python"
    assert pkg2["platform"] == "PIP"
    assert pkg2["licenses"] == []
    assert pkg2["package_url"] == "pkg:python/test-package-2@2.0.0"
    assert pkg2["found_by"] == "test-tool"
    assert pkg2["advisories"] == []
    assert pkg2["locations"] == []
    assert pkg2["health_metadata"] is None


def test_validate_pkgs() -> None:
    valid_pkg_1: dict[str, Any] = {
        "id": "pkg-1",
        "created_at": datetime(2025, 1, 1, tzinfo=UTC),
        "type": PackageType.PythonPkg,
    }

    valid_pkg_2: dict[str, Any] = {
        "id": "pkg-2",
        "name": "another-pkg",
    }

    invalid_pkg: dict[str, Any] = {
        "id": "pkg-3",
        "invalid_field": object(),
    }

    input_pkgs = [valid_pkg_1, invalid_pkg, valid_pkg_2]

    result = validate_pkgs(input_pkgs)

    assert len(result) == 2

    assert result[0]["id"] == "pkg-1"
    assert result[1]["id"] == "pkg-2"

    assert isinstance(result[0]["created_at"], str)
    assert result[0]["created_at"] == datetime(2025, 1, 1, tzinfo=UTC).isoformat()

    assert result[0]["type"] == "python"


def test_build_relationship_map() -> None:
    pkg1 = Package(
        name="package1",
        version="1.0.0",
        type=PackageType.PythonPkg,
        language=Language.PYTHON,
        locations=[],
        licenses=[],
        p_url="pkg:python/package1@1.0.0",
        found_by="test-tool",
    )
    pkg2 = Package(
        name="package2",
        version="1.0.0",
        type=PackageType.PythonPkg,
        language=Language.PYTHON,
        locations=[],
        licenses=[],
        p_url="pkg:python/package2@1.0.0",
        found_by="test-tool",
    )

    relationships = [
        Relationship(from_=pkg1, to_=pkg2, type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP),
    ]

    result = build_relationship_map(relationships)
    assert len(result) == 1
    assert result[0]["from"] == pkg2.id_by_hash()
    assert result[0]["to"] == [pkg1.id_by_hash()]


def test_build_sbom_metadata() -> None:
    result = build_sbom_metadata("test-namespace", "1.0.0", "2025-01-01T00:00:00")

    assert result["name"] == "test-namespace"
    assert result["version"] == "1.0.0"
    assert result["timestamp"] == "2025-01-01T00:00:00"
    assert result["tool"] == "Fluid-Labels"
    assert result["organization"] == "Fluid attacks"
