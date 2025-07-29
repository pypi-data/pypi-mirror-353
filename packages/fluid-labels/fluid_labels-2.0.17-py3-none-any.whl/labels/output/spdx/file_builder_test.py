from unittest.mock import MagicMock

from license_expression import AND, LicenseSymbol
from spdx_tools.spdx.model.actor import Actor, ActorType
from spdx_tools.spdx.model.checksum import Checksum, ChecksumAlgorithm
from spdx_tools.spdx.model.document import Document
from spdx_tools.spdx.model.package import (
    ExternalPackageRef,
    ExternalPackageRefCategory,
    PackagePurpose,
)
from spdx_tools.spdx.model.package import Package as SPDX_Package
from spdx_tools.spdx.model.relationship import RelationshipType as SPDXRelationshipType

from labels.model.advisories import Advisory
from labels.model.file import Coordinates, DependencyType, Location, Scope
from labels.model.package import Artifact, Digest, HealthMetadata, Language, Package, PackageType
from labels.model.relationship import Relationship, RelationshipType
from labels.output.spdx.file_builder import (
    add_packages_and_relationships,
    create_document_relationships,
    create_package_cache,
    package_to_spdx_pkg,
    process_relationship,
)


def test_package_to_spdx_pkg() -> None:
    test_package = Package(
        name="test-package",
        version="1.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[
            Location(
                coordinates=Coordinates(real_path="/test/path"),
                scope=Scope.PROD,
                dependency_type=DependencyType.DIRECT,
            ),
        ],
        licenses=["MIT AND Apache-2.0"],
        p_url="pkg:npm/test-package@1.0.0",
        metadata={"id": "test-package"},
        health_metadata=HealthMetadata(
            authors="test-author <test@gmail.com>",
            artifact=Artifact(
                url="test-url",
                integrity=Digest(value="sha256:1234567890abcdef", algorithm="sha256"),
            ),
            latest_version="1.5.0",
            latest_version_created_at="2023-10-01T00:00:00Z",
        ),
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

    spdx_package = package_to_spdx_pkg(test_package)

    assert isinstance(spdx_package, SPDX_Package)
    assert spdx_package.spdx_id == f"SPDXRef-Package-npm-test-package-{test_package.id_}"
    assert spdx_package.name == "test-package"
    assert spdx_package.version == "1.0.0"
    assert spdx_package.license_declared == AND(
        LicenseSymbol(
            "MIT",
            aliases=(
                "LicenseRef-MIT-Bootstrap",
                "LicenseRef-MIT-Discord",
                "LicenseRef-MIT-TC",
                "LicenseRef-MIT-Diehl",
            ),
            is_exception=False,
        ),
        LicenseSymbol(
            "Apache-2.0",
            aliases=("LicenseRef-Apache", "LicenseRef-Apache-2.0"),
            is_exception=False,
        ),
    )
    assert spdx_package.originator == Actor(
        actor_type=ActorType.PERSON,
        name="test-author",
        email="test@gmail.com",
    )
    assert spdx_package.external_references == [
        ExternalPackageRef(
            category=ExternalPackageRefCategory.OTHER,
            reference_type="fluid-attacks:language",
            locator=Language.JAVASCRIPT,
            comment=None,
        ),
        ExternalPackageRef(
            category=ExternalPackageRefCategory.OTHER,
            reference_type="fluid-attacks:health_metadata:latest_version",
            locator="1.5.0",
            comment=None,
        ),
        ExternalPackageRef(
            category=ExternalPackageRefCategory.OTHER,
            reference_type="fluid-attacks:health_metadata:latest_version_created_at",
            locator="2023-10-01T00:00:00Z",
            comment=None,
        ),
        ExternalPackageRef(
            category=ExternalPackageRefCategory.PACKAGE_MANAGER,
            reference_type="purl",
            locator="pkg:npm/test-package@1.0.0",
            comment=None,
        ),
        ExternalPackageRef(
            category=ExternalPackageRefCategory.OTHER,
            reference_type="fluid-attacks:locations:0:path",
            locator="/test/path",
            comment=None,
        ),
        ExternalPackageRef(
            category=ExternalPackageRefCategory.SECURITY,
            reference_type="advisory",
            locator="https://fluidattacks.com",
            comment="Severity: HIGH; EPSs: 0.75; Score: 8.5; Affected Version: "
            "1.0.0; Affected Version Range: >=1.0.0; Description: Test "
            "advisory description",
        ),
    ]
    assert spdx_package.checksums == [
        Checksum(
            algorithm=ChecksumAlgorithm.SHA256,
            value="sha256:1234567890abcdef",
        ),
    ]


def test_create_package_cache() -> None:
    packages = [
        Package(
            name="pkg1",
            version="1.0.0",
            type=PackageType.NpmPkg,
            language=Language.JAVASCRIPT,
            locations=[],
            licenses=[],
            p_url="pkg:npm/pkg1@1.0.0",
        ),
        Package(
            name="pkg2",
            version="2.0.0",
            type=PackageType.NpmPkg,
            language=Language.JAVASCRIPT,
            locations=[],
            licenses=[],
            p_url="pkg:npm/pkg2@2.0.0",
        ),
    ]
    package_cache = create_package_cache(packages)

    assert len(package_cache) == 2
    assert all(isinstance(v, SPDX_Package) for v in package_cache.values())
    assert all(isinstance(k, Package) for k in package_cache)

    for original_pkg, spdx_pkg in package_cache.items():
        assert original_pkg.name == spdx_pkg.name
        assert original_pkg.version == spdx_pkg.version


def test_create_document_relationships() -> None:
    mock_doc = MagicMock(spec=Document)
    mock_doc.creation_info.spdx_id = "SPDXRef-DOCUMENT"

    spdx_packages = [
        SPDX_Package(
            spdx_id="SPDXRef-Package1",
            name="pkg1",
            download_location="NOASSERTION",
            version="1.0.0",
            primary_package_purpose=PackagePurpose.LIBRARY,
        ),
        SPDX_Package(
            spdx_id="SPDXRef-Package2",
            name="pkg2",
            download_location="NOASSERTION",
            version="2.0.0",
            primary_package_purpose=PackagePurpose.LIBRARY,
        ),
    ]

    relationships = create_document_relationships(mock_doc, spdx_packages)

    assert len(relationships) == 2
    for rel in relationships:
        assert rel.relationship_type == SPDXRelationshipType.DESCRIBES
        assert rel.spdx_element_id == "SPDXRef-DOCUMENT"
        assert rel.related_spdx_element_id in ["SPDXRef-Package1", "SPDXRef-Package2"]


def test_add_packages_and_relationships() -> None:
    mock_doc = MagicMock(spec=Document)
    mock_doc.creation_info.spdx_id = "SPDXRef-DOCUMENT"

    pkg1 = Package(
        name="pkg1",
        version="1.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[],
        licenses=[],
        p_url="pkg:npm/pkg1@1.0.0",
    )
    pkg2 = Package(
        name="pkg2",
        version="2.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[],
        licenses=[],
        p_url="pkg:npm/pkg2@2.0.0",
    )
    packages = [pkg1, pkg2]

    relationships = [
        Relationship(
            from_=pkg1,
            to_=pkg2,
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
    ]

    add_packages_and_relationships(mock_doc, packages, relationships)

    assert len(mock_doc.packages) == 2
    assert hasattr(mock_doc, "relationships")
    assert isinstance(mock_doc.packages[0], SPDX_Package)


def test_process_relationship() -> None:
    pkg1 = Package(
        name="pkg1",
        version="1.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[],
        licenses=[],
        p_url="pkg:npm/pkg1@1.0.0",
    )
    pkg2 = Package(
        name="pkg2",
        version="2.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[],
        licenses=[],
        p_url="pkg:npm/pkg2@2.0.0",
    )

    spdx_id_cache = {
        pkg1: "SPDXRef-Package1",
        pkg2: "SPDXRef-Package2",
    }

    relationship = Relationship(
        from_=pkg1,
        to_=pkg2,
        type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
    )
    result = process_relationship(relationship, spdx_id_cache)
    assert result is not None
    assert result.spdx_element_id == "SPDXRef-Package2"
    assert result.relationship_type == SPDXRelationshipType.DEPENDENCY_OF
    assert result.related_spdx_element_id == "SPDXRef-Package1"


def test_process_relationship_wrong_instance() -> None:
    pkg1 = Package(
        name="pkg1",
        version="1.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[],
        licenses=[],
        p_url="pkg:npm/pkg1@1.0.0",
    )
    pkg3 = Package(
        name="pkg3",
        version="3.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[],
        licenses=[],
        p_url="pkg:npm/pkg3@3.0.0",
    )

    spdx_id_cache = {
        pkg1: "SPDXRef-Package1",
    }

    relationship = Relationship(
        from_=pkg1,
        to_=pkg3,
        type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
    )
    result = process_relationship(relationship, spdx_id_cache)
    assert result is None
