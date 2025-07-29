from cyclonedx.model.bom import Bom
from cyclonedx.model.bom_ref import BomRef
from cyclonedx.model.component import Component, ComponentType

from labels.model.advisories import Advisory
from labels.model.file import Coordinates, DependencyType, Location, Scope
from labels.model.package import HealthMetadata, Language, Package, PackageType
from labels.model.relationship import Relationship, RelationshipType
from labels.output.cyclonedx.file_builder import (
    add_advisories_to_bom,
    add_components_to_bom,
    add_relationships_to_bom,
    create_bom,
    pkg_to_component,
)


def create_test_package() -> Package:
    return Package(
        name="test-package",
        version="1.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        licenses=["MIT"],
        p_url="pkg:npm/test-package@1.0.0",
        locations=[
            Location(
                coordinates=Coordinates(
                    real_path="/test/path/package.json",
                    file_system_id="layer:1234",
                    line=13,
                ),
                access_path="package.json",
                scope=Scope.PROD,
                dependency_type=DependencyType.DIRECT,
            ),
        ],
        metadata={"test": "value"},
        health_metadata=HealthMetadata(
            latest_version="2.0.0",
            latest_version_created_at="2025-01-01T00:00:00Z",
        ),
        found_by="test",
        advisories=[
            Advisory(
                id="test-advisory",
                urls=["test-url"],
                severity="HIGH",
                epss=0.75,
                percentile=8.5,
                description="Test advisory description",
                version_constraint=">=1.0.0",
                cpes=[],
                namespace="github",
                cvss3=None,
                cvss4=None,
            ),
        ],
    )


def test_create_bom() -> None:
    namespace = "test-namespace"
    version = "1.0.0"

    bom = create_bom(namespace, version)

    assert isinstance(bom, Bom)
    assert bom.metadata.component is not None
    assert bom.metadata.component.name == namespace
    assert bom.metadata.component.version == version
    assert bom.metadata.tools.tools
    assert len(bom.metadata.tools.tools) == 1
    tool = next(iter(bom.metadata.tools.tools))
    assert tool.vendor == "Fluid Attacks"
    assert tool.name == "Fluid-Labels"


def test_pkg_to_component() -> None:
    package = create_test_package()
    component = pkg_to_component(package)

    assert isinstance(component, Component)
    assert component.name == package.name
    assert component.version == package.version
    assert component.licenses
    assert len(component.licenses) == 1
    assert str(component.bom_ref) == f"{package.name}@{package.version}"
    assert component.purl is not None
    assert str(component.purl) == package.p_url
    assert component.properties

    assert any(p.name.endswith("latest_version") for p in component.properties)
    assert any(p.name.endswith(":latest_version") for p in component.properties)
    assert any(p.name.endswith(":line") for p in component.properties)
    assert any(p.name.endswith(":layer") for p in component.properties)
    assert any(p.name.endswith(":path") for p in component.properties)
    assert any(p.name.endswith(":language") for p in component.properties)


def test_add_components_to_bom() -> None:
    bom = Bom()
    package = create_test_package()
    component = pkg_to_component(package)
    component_cache = {package: component}

    add_components_to_bom(bom, component_cache)

    assert bom.components
    assert len(bom.components) == 1
    assert next(iter(bom.components)).name == package.name


def test_add_advisories_to_bom() -> None:
    bom = Bom()
    package = create_test_package()

    add_advisories_to_bom(bom, [package])

    assert bom.vulnerabilities
    assert len(bom.vulnerabilities) == 1
    vulnerability = next(iter(bom.vulnerabilities))
    assert vulnerability.id == "test-advisory"


def test_add_relationships_to_bom() -> None:
    namespace = "test-namespace"
    version = "1.0.0"
    bom = Bom()
    bom.metadata.component = Component(
        name=namespace,
        type=ComponentType.APPLICATION,
        licenses=[],
        bom_ref=BomRef(f"{namespace}@{version}"),
        version=version,
    )
    package1 = create_test_package()
    package2 = Package(
        name="test-package-2",
        version="1.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        licenses=[],
        p_url="pkg:npm/test-package-2@1.0.0",
        locations=[],
        found_by="test",
    )

    relationship = Relationship(
        from_=package1,
        to_=package2,
        type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
    )
    relationships = [relationship]

    component1 = pkg_to_component(package1)
    component2 = pkg_to_component(package2)
    component_cache = {
        package1: component1,
        package2: component2,
    }

    add_relationships_to_bom(bom, relationships, component_cache)

    assert bom.dependencies
    assert len(bom.dependencies) == 3
    assert next(d for d in bom.dependencies if str(d.ref) == "test-namespace@1.0.0")

    pkg2_dep = next(
        d for d in bom.dependencies if str(d.ref) == f"{package2.name}@{package2.version}"
    )
    assert len(pkg2_dep.dependencies) == 1
    assert str(next(iter(pkg2_dep.dependencies)).ref) == f"{package1.name}@{package1.version}"


def test_add_relationships_to_bom_empty_component() -> None:
    bom = Bom()
    bom.metadata.component = None
    add_relationships_to_bom(bom, [], {})

    assert not bom.dependencies
