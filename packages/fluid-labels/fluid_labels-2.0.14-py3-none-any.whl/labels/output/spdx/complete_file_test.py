from unittest.mock import MagicMock

from license_expression import AND, ExpressionError, LicenseExpression, LicenseSymbol
from spdx_tools.spdx.model.actor import Actor, ActorType
from spdx_tools.spdx.model.checksum import ChecksumAlgorithm
from spdx_tools.spdx.model.document import Document
from spdx_tools.spdx.model.package import ExternalPackageRef, ExternalPackageRefCategory

import labels.output.spdx.complete_file
from labels.model.advisories import Advisory
from labels.model.file import Coordinates, DependencyType, Location, Scope
from labels.model.package import Artifact, Digest, HealthMetadata, Language, Package, PackageType
from labels.output.spdx.complete_file import (
    NAMESPACE,
    NOASSERTION,
    add_authors,
    add_empty_package,
    add_external_refs,
    add_health_metadata_external_refs,
    add_integrity,
    add_license,
    add_locations_external_refs,
    add_vulnerabilities_spdx,
    get_spdx_id,
)
from labels.testing.mocks import Mock, mocks


def test_add_vulnerabilities_spdx() -> None:
    test_advisory = Advisory(
        id="TEST-1",
        urls=["https://test.com", "https://test2.com", "MANUAL"],
        severity="HIGH",
        epss=0.8,
        percentile=85,
        version_constraint=">=1.0.0",
        description="Test vulnerability",
        cpes=["cpe:2.3:a:test:package:1.0.0:*:*:*:*:*:*:*"],
        namespace="npm",
        cvss3="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        cvss4="CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H",
    )

    test_package = Package(
        name="test-package",
        version="1.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[],
        licenses=[],
        p_url="pkg:npm/test-package@1.0.0",
        advisories=[test_advisory],
    )

    refs = add_vulnerabilities_spdx(test_package)
    assert len(refs) == 1
    assert refs[0].category == ExternalPackageRefCategory.SECURITY
    assert refs[0].reference_type == "advisory"
    assert refs[0].locator == "https://test.com, https://test2.com"
    assert refs[0].comment is not None
    assert "Severity: HIGH" in refs[0].comment
    assert "EPSs: 0.8" in refs[0].comment
    assert "Score: 85" in refs[0].comment
    assert "Affected Version: 1.0.0" in refs[0].comment
    assert "Affected Version Range: >=1.0.0" in refs[0].comment
    assert "Description: Test vulnerability" in refs[0].comment


def test_add_vulnerabilities_spdx_invalid_urls() -> None:
    test_advisory = Advisory(
        id="test-advisory",
        urls=["https://osv-vulnerabilities", "https://valid-url.com", "MANUAL"],
        severity="HIGH",
        epss=0.75,
        percentile=8.5,
        description="Test advisory description",
        version_constraint=">=1.0.0",
        cpes=[],
        namespace="github",
        cvss3=None,
        cvss4=None,
    )

    test_package = Package(
        name="test-package",
        version="1.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[],
        licenses=[],
        p_url="pkg:npm/test-package@1.0.0",
        advisories=[test_advisory],
    )

    refs = add_vulnerabilities_spdx(test_package)
    assert len(refs) == 1
    assert refs[0].locator == "https://valid-url.com"
    assert refs[0].comment is not None
    assert "Severity: HIGH" in refs[0].comment

    test_advisory_invalid = Advisory(
        id="test-advisory",
        urls=["https://osv-vulnerabilities", "MANUAL"],
        severity="HIGH",
        epss=0.75,
        percentile=8.5,
        description="Test advisory description",
        version_constraint=">=1.0.0",
        cpes=[],
        namespace="github",
        cvss3=None,
        cvss4=None,
    )
    test_package.advisories = [test_advisory_invalid]

    refs = add_vulnerabilities_spdx(test_package)
    assert len(refs) == 1
    assert refs[0].locator == "https://fluidattacks.com"


def test_add_authors_complete() -> None:
    test_metadata = HealthMetadata(
        authors="Test Author, Another Author <another@example.com>",
    )

    result = add_authors(test_metadata)
    assert isinstance(result, Actor)
    assert result.actor_type == ActorType.PERSON
    assert result.name == "Test Author, Another Author"
    assert result.email == "another@example.com"

    assert add_authors(None) == NOASSERTION


def test_add_authors_just_email() -> None:
    test_metadata = HealthMetadata(
        authors="<test@example.com>",
    )

    result = add_authors(test_metadata)

    assert isinstance(result, Actor)
    assert result.actor_type == ActorType.PERSON
    assert result.name == ""
    assert result.email == "test@example.com"


def test_add_authors_just_name() -> None:
    test_metadata = HealthMetadata(
        authors="Test Author",
    )

    result = add_authors(test_metadata)

    assert isinstance(result, Actor)
    assert result.actor_type == ActorType.PERSON
    assert result.name == "Test Author"
    assert result.email is None


def test_add_locations_external_refs() -> None:
    locations = [
        Location(
            coordinates=Coordinates(
                real_path="/test/path",
                line=42,
                file_system_id="layer123",
            ),
            scope=Scope.PROD,
            dependency_type=DependencyType.DIRECT,
        ),
    ]

    refs = add_locations_external_refs(locations)
    assert len(refs) == 3

    path_ref = next(r for r in refs if r.reference_type.endswith(":path"))
    assert path_ref.locator == "/test/path"

    line_ref = next(r for r in refs if r.reference_type.endswith(":line"))
    assert line_ref.locator == "42"

    layer_ref = next(r for r in refs if r.reference_type.endswith(":layer"))
    assert layer_ref.locator == "layer123"

    assert add_locations_external_refs([]) == []


def test_add_locations_external_refs_no_line() -> None:
    location_without_line = Location(
        coordinates=Coordinates(
            real_path="/test/path",
            line=None,
            file_system_id="layer123",
        ),
        scope=Scope.PROD,
        dependency_type=DependencyType.DIRECT,
    )
    refs = add_locations_external_refs([location_without_line])
    assert len(refs) == 2
    assert all(not r.reference_type.endswith(":line") for r in refs)


def test_add_locations_external_refs_no_layer() -> None:
    location_without_layer = Location(
        coordinates=Coordinates(
            real_path="/test/path",
            line=42,
            file_system_id=None,
        ),
        scope=Scope.PROD,
        dependency_type=DependencyType.DIRECT,
    )
    refs = add_locations_external_refs([location_without_layer])
    assert len(refs) == 2
    assert all(not r.reference_type.endswith(":layer") for r in refs)


def test_add_external_refs_with_health_metadata() -> None:
    health_metadata = HealthMetadata(
        latest_version="1.2.3",
        latest_version_created_at="2025-04-20T12:00:00",
    )

    external_refs: list[ExternalPackageRef] = add_health_metadata_external_refs(health_metadata)

    assert len(external_refs) == 2

    assert external_refs[0].reference_type == f"{NAMESPACE}:health_metadata:latest_version"
    assert external_refs[0].locator == "1.2.3"
    assert (
        external_refs[1].reference_type == f"{NAMESPACE}:health_metadata:latest_version_created_at"
    )
    assert external_refs[1].locator == "2025-04-20T12:00:00"


def test_add_health_metadata_external_refs_with_only_latest_version() -> None:
    health_metadata = HealthMetadata(
        latest_version="2.0.0",
        latest_version_created_at=None,
    )

    external_refs = add_health_metadata_external_refs(health_metadata)

    assert len(external_refs) == 1
    assert external_refs[0].reference_type == f"{NAMESPACE}:health_metadata:latest_version"
    assert external_refs[0].locator == "2.0.0"


def test_add_health_metadata_external_refs_with_only_latest_version_created_at() -> None:
    health_metadata = HealthMetadata(
        latest_version=None,
        latest_version_created_at="2025-04-22T09:30:00",
    )

    external_refs = add_health_metadata_external_refs(health_metadata)

    assert len(external_refs) == 1
    assert (
        external_refs[0].reference_type == f"{NAMESPACE}:health_metadata:latest_version_created_at"
    )
    assert external_refs[0].locator == "2025-04-22T09:30:00"


def test_add_health_metadata_external_refs_empty() -> None:
    health_metadata = HealthMetadata(
        latest_version=None,
        latest_version_created_at=None,
    )

    external_refs = add_health_metadata_external_refs(health_metadata)

    assert external_refs == []


def test_add_external_refs() -> None:
    package = Package(
        name="test-package",
        version="1.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        licenses=[],
        locations=[
            Location(
                coordinates=Coordinates(
                    real_path="/src/index.js",
                    line=12,
                    file_system_id="layerX",
                ),
                scope=Scope.PROD,
                dependency_type=DependencyType.DIRECT,
            ),
        ],
        p_url="pkg:npm/test-package@1.0.0",
        advisories=[
            Advisory(
                id="TEST-1",
                urls=[],
                severity="HIGH",
                epss=0.8,
                percentile=85,
                version_constraint=">=1.0.0",
                description=None,
                cpes=[],
                namespace="npm",
                cvss3=None,
                cvss4=None,
            ),
        ],
    )

    refs = add_external_refs(package)

    assert any(ref.reference_type == "purl" for ref in refs)
    assert any(ref.reference_type == "advisory" for ref in refs)
    assert any(ref.reference_type.endswith("language") for ref in refs)
    assert any(ref.reference_type.endswith(":path") for ref in refs)
    assert any(ref.reference_type.endswith(":line") for ref in refs)
    assert any(ref.reference_type.endswith(":layer") for ref in refs)


def test_add_integrity() -> None:
    test_metadata = HealthMetadata(
        artifact=Artifact(
            integrity=Digest(
                algorithm="sha256",
                value="1234567890abcdef",
            ),
            url="https://test.com",
        ),
    )

    checksums = add_integrity(test_metadata)
    assert len(checksums) == 1
    assert checksums[0].algorithm == ChecksumAlgorithm.SHA256
    assert checksums[0].value == "1234567890abcdef"


def test_add_integrity_not_complete() -> None:
    assert add_integrity(None) == []

    test_metadata_empty_artifact = HealthMetadata(artifact=None)
    assert add_integrity(test_metadata_empty_artifact) == []

    test_metadata_incomplete = HealthMetadata(
        artifact=Artifact(
            integrity=Digest(algorithm=None, value="1234567890abcdef"),
            url="https://test.com",
        ),
    )
    assert add_integrity(test_metadata_incomplete) == []


def test_add_empty_package() -> None:
    doc = MagicMock(spec=Document)

    add_empty_package(doc)
    assert len(doc.packages) == 1
    assert doc.packages[0].name == "NONE"
    assert doc.packages[0].spdx_id == "SPDXRef-Package-NONE"
    assert doc.relationships == []

    expected_comment = "No packages or relationships were found in the resource."
    assert doc.creation_info.document_comment == expected_comment


def test_get_spdx_id() -> None:
    test_package = Package(
        name="test-package",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        licenses=[],
        p_url="pkg:npm/test-package@1.0.0",
        version="1.0.0",
        locations=[],
    )

    spdx_id = get_spdx_id(test_package)
    assert spdx_id == f"SPDXRef-Package-npm-test-package-{test_package.id_}"


def test_add_license() -> None:
    licenses = ["MIT", "Apache-2.0"]
    result = add_license(licenses)
    assert isinstance(result, LicenseExpression)
    assert result == AND(
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


@mocks(
    mocks=[
        Mock(
            module=labels.output.spdx.complete_file,
            target="get_spdx_licensing",
            target_type="sync",
            expected=MagicMock(
                parse=MagicMock(
                    side_effect=ExpressionError("Invalid license expression"),
                ),
            ),
        ),
    ],
)
async def test_add_license_exception() -> None:
    licenses = ["INVALID-LICENSE"]
    add_license(licenses)

    assert add_license(licenses) == NOASSERTION
