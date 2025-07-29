from datetime import UTC, datetime
from decimal import Decimal

from cyclonedx.model import HashType, Property, XsUri
from cyclonedx.model.license import DisjunctiveLicense, LicenseExpression
from cyclonedx.model.vulnerability import (
    BomTarget,
    VulnerabilityAdvisory,
    VulnerabilityRating,
    VulnerabilitySeverity,
)

from labels.model.advisories import Advisory
from labels.model.file import Coordinates, Location
from labels.model.package import (
    Artifact,
    Digest,
    HealthMetadata,
    Language,
    Package,
    PackageType,
)
from labels.output.cyclonedx.complete_file import (
    add_authors,
    add_component_properties,
    add_health_metadata_properties,
    add_integrity,
    add_language_property,
    add_locations_properties,
    add_vulnerabilities,
    get_licenses,
)


def test_add_vulnerabilities_empty() -> None:
    package = Package(
        name="test-package",
        version="1.0.0",
        language=Language.PYTHON,
        licenses=[],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:pypi/test-package@1.0.0",
        advisories=None,
    )

    result = add_vulnerabilities(package)

    assert isinstance(result, list)
    assert len(result) == 0


def test_add_vulnerabilities_with_data() -> None:
    package = Package(
        name="test-package",
        version="1.0.0",
        language=Language.PYTHON,
        licenses=[],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:pypi/test-package@1.0.0",
        advisories=[
            Advisory(
                id="CVE-2023-1234",
                description="Test vulnerability",
                severity="HIGH",
                percentile=8.9,
                urls=["https://example.com/cve-2023-1234"],
                version_constraint=">=1.0.0",
                epss=0.75,
                cpes=[],
                namespace="test-namespace",
                cvss3=None,
                cvss4=None,
            ),
        ],
    )

    result = add_vulnerabilities(package)

    assert isinstance(result, list)
    assert len(result) == 1

    vuln = result[0]
    assert vuln.id == "CVE-2023-1234"
    assert vuln.description == "Test vulnerability"
    assert isinstance(vuln.ratings[0], VulnerabilityRating)
    assert vuln.ratings[0].severity == VulnerabilitySeverity("high")
    assert vuln.ratings[0].score == Decimal("8.9")
    assert isinstance(vuln.advisories[0], VulnerabilityAdvisory)
    assert vuln.advisories[0].url == XsUri("https://example.com/cve-2023-1234")
    assert isinstance(vuln.affects[0], BomTarget)
    assert vuln.affects[0].ref == "test-package@1.0.0"
    assert vuln.affects[0].versions[0].version is None
    assert vuln.affects[0].versions[0].range == ">=1.0.0"
    assert vuln.properties[0].name == "fluid-attacks:advisory:epss"
    assert vuln.properties[0].value == "0.75"


def test_add_health_metadata_properties_empty() -> None:
    health_metadata = HealthMetadata(
        latest_version=None,
        latest_version_created_at=None,
        artifact=None,
    )

    result = add_health_metadata_properties(health_metadata)

    assert isinstance(result, list)
    assert len(result) == 0


def test_add_health_metadata_properties_with_data() -> None:
    health_metadata = HealthMetadata(
        latest_version="2.0.0",
        latest_version_created_at=datetime(2025, 1, 1, tzinfo=UTC),
        artifact=None,
    )

    result = add_health_metadata_properties(health_metadata)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].name == "fluid-attacks:health_metadata:latest_version"
    assert result[0].value == "2.0.0"
    assert result[1].name == "fluid-attacks:health_metadata:latest_version_created_at"
    assert result[1].value == "2025-01-01 00:00:00+00:00"


def test_add_locations_properties() -> None:
    locations = [
        Location(
            coordinates=Coordinates(
                real_path="/test/path",
                file_system_id="layer-1",
                line=10,
            ),
            access_path="/test/path",
        ),
    ]

    result = add_locations_properties(locations)

    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0].name == "fluid-attacks:locations:0:path"
    assert result[0].value == "/test/path"
    assert result[1].name == "fluid-attacks:locations:0:line"
    assert result[1].value == "10"
    assert result[2].name == "fluid-attacks:locations:0:layer"
    assert result[2].value == "layer-1"


def test_add_locations_properties_empty() -> None:
    result = add_locations_properties([])

    assert isinstance(result, list)
    assert len(result) == 0


def test_add_locations_properties_partial_data() -> None:
    locations = [
        Location(
            coordinates=Coordinates(
                real_path="/test/path",
                file_system_id=None,
                line=None,
            ),
            access_path="/test/path",
        ),
    ]

    result = add_locations_properties(locations)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].name == "fluid-attacks:locations:0:path"
    assert result[0].value == "/test/path"


def test_add_language_property() -> None:
    result = add_language_property("python")

    assert isinstance(result, Property)
    assert result.name == "fluid-attacks:language"
    assert result.value == "python"


def test_add_integrity_empty() -> None:
    health_metadata = HealthMetadata(
        latest_version=None,
        latest_version_created_at=None,
        artifact=None,
    )

    result = add_integrity(health_metadata)

    assert result is None


def test_add_integrity_with_data() -> None:
    health_metadata = HealthMetadata(
        latest_version="2.0.0",
        latest_version_created_at=datetime(2025, 1, 1, tzinfo=UTC),
        artifact=Artifact(
            url="https://example.com/package",
            integrity=Digest(
                algorithm="sha256",
                value="abc123",
            ),
        ),
    )

    result = add_integrity(health_metadata)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], HashType)
    assert result[0].alg == "SHA-256"
    assert result[0].content == "abc123"


def test_add_integrity_incomplete_data() -> None:
    health_metadata = HealthMetadata(
        latest_version="2.0.0",
        latest_version_created_at=datetime(2025, 1, 1, tzinfo=UTC),
        artifact=Artifact(
            url="https://example.com/package",
            integrity=Digest(
                algorithm=None,
                value="abc123",
            ),
        ),
    )

    result = add_integrity(health_metadata)

    assert result is None


def test_get_licenses_empty() -> None:
    result = get_licenses([])

    assert isinstance(result, list)
    assert len(result) == 0


def test_get_licenses_with_mixed_licenses() -> None:
    package_licenses = [
        "MIT",
        "MIT OR Apache-2.0",
        "GPL-2.0-only",
        "GPL-2.0-only AND MIT",
    ]
    result = get_licenses(package_licenses)

    assert len(result) == 4

    simple_licenses = [lic for lic in result if isinstance(lic, DisjunctiveLicense)]
    expressions = [lic for lic in result if isinstance(lic, LicenseExpression)]

    assert len(simple_licenses) == 2
    assert any(license_obj.id == "MIT" for license_obj in simple_licenses)
    assert any(license_obj.id == "GPL-2.0-only" for license_obj in simple_licenses)

    assert len(expressions) == 2
    assert any("MIT" in str(expr) and "Apache-2.0" in str(expr) for expr in expressions)
    assert any("GPL-2.0-only" in str(expr) and "MIT" in str(expr) for expr in expressions)


def test_add_minimal_component_properties() -> None:
    package = Package(
        name="test-package",
        version="1.0.0",
        language=Language.PYTHON,
        licenses=[],
        locations=[
            Location(
                coordinates=Coordinates(
                    real_path="/test/path",
                    file_system_id="layer-1",
                    line=10,
                ),
                access_path="/test/path",
            ),
        ],
        type=PackageType.PythonPkg,
        p_url="pkg:pypi/test-package@1.0.0",
    )

    result = add_component_properties(package)

    assert isinstance(result, list)
    assert len(result) == 4
    assert result[0].name == "fluid-attacks:language"
    assert result[0].value == "python"
    assert result[1].name == "fluid-attacks:locations:0:path"
    assert result[1].value == "/test/path"
    assert result[2].name == "fluid-attacks:locations:0:line"
    assert result[2].value == "10"
    assert result[3].name == "fluid-attacks:locations:0:layer"
    assert result[3].value == "layer-1"


def test_add_component_properties_with_metadata() -> None:
    package = Package(
        name="test-package",
        version="1.0.0",
        language=Language.PYTHON,
        licenses=[],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:pypi/test-package@1.0.0",
        health_metadata=HealthMetadata(
            latest_version="2.0.0",
            latest_version_created_at=datetime(2025, 1, 1, tzinfo=UTC),
            artifact=None,
        ),
    )

    result = add_component_properties(package)

    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0].name == "fluid-attacks:language"
    assert result[0].value == "python"
    assert result[1].name == "fluid-attacks:health_metadata:latest_version"
    assert result[1].value == "2.0.0"
    assert result[2].name == "fluid-attacks:health_metadata:latest_version_created_at"
    assert result[2].value == "2025-01-01 00:00:00+00:00"


def test_add_authors_empty() -> None:
    health_metadata = HealthMetadata(
        latest_version=None,
        latest_version_created_at=None,
        artifact=None,
        authors=None,
    )

    result = add_authors(health_metadata)

    assert isinstance(result, list)
    assert len(result) == 0


def test_add_authors_with_data() -> None:
    health_metadata = HealthMetadata(
        latest_version="2.0.0",
        latest_version_created_at=datetime(2025, 1, 1, tzinfo=UTC),
        artifact=None,
        authors="John Doe <john@example.com>, Jane Smith <jane@example.com>",
    )

    result = add_authors(health_metadata)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].name == "John Doe"
    assert result[0].email == "john@example.com"
    assert result[1].name == "Jane Smith"
    assert result[1].email == "jane@example.com"


def test_add_authors_with_invalid_email() -> None:
    health_metadata = HealthMetadata(
        latest_version="2.0.0",
        latest_version_created_at=datetime(2025, 1, 1, tzinfo=UTC),
        artifact=None,
        authors="John Doe, Jane Smith",
    )

    result = add_authors(health_metadata)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].name == "John Doe"
    assert result[0].email is None
    assert result[1].name == "Jane Smith"
    assert result[1].email is None
