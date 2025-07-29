from pydantic import ValidationError

from labels.model.advisories import Advisory
from labels.testing.utils.pytest_methods import raises


def test_invalid_cpes() -> None:
    with raises(ValidationError):
        Advisory(
            cpes=[""],
            epss=0.5,
            id="TEST-3",
            namespace="test",
            percentile=75.0,
            severity="LOW",
            urls=["https://example.com"],
            description="Test vulnerability",
            version_constraint=">=1.0.0",
            cvss3="5.0",
            cvss4="3.0",
        )


def test_invalid_urls() -> None:
    with raises(ValidationError):
        Advisory(
            cpes=["cpe:2.3:a:vendor:product:1.0"],
            epss=0.5,
            id="TEST-4",
            namespace="test",
            percentile=75.0,
            severity="LOW",
            urls=[""],
            description="Test vulnerability",
            version_constraint=">=1.0.0",
            cvss3="5.0",
            cvss4="3.0",
        )


def test_get_info_count() -> None:
    advisory_full = Advisory(
        cpes=["cpe:2.3:a:vendor:product:1.0"],
        description="Test",
        epss=0.5,
        id="TEST-5",
        namespace="test",
        percentile=75.0,
        severity="HIGH",
        urls=["https://example.com"],
        version_constraint=">=1.0.0",
        cvss3="7.5",
        cvss4="4.0",
    )
    assert advisory_full.get_info_count() == 4

    advisory_minimal = Advisory(
        cpes=[],
        epss=0.5,
        id="TEST-6",
        namespace="test",
        percentile=75.0,
        severity="LOW",
        urls=[],
        description="Test vulnerability",
        version_constraint=None,
        cvss3="5.0",
        cvss4="3.0",
    )
    assert advisory_minimal.get_info_count() == 1


def test_advisory_repr() -> None:
    advisory = Advisory(
        cpes=["cpe:2.3:a:vendor:product:1.0"],
        epss=0.5,
        id="TEST-7",
        namespace="test-namespace",
        percentile=75.0,
        severity="CRITICAL",
        urls=["https://example.com"],
        description="Test vulnerability",
        version_constraint=">=1.0.0",
        cvss3="9.0",
        cvss4="4.0",
    )
    expected_repr = "Advisory(id=TEST-7, namespace=test-namespace, severity=CRITICAL)"
    assert repr(advisory) == expected_repr
