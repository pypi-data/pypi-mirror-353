import json
from unittest.mock import MagicMock

from pydantic import ValidationError

from labels.model.package import HealthMetadata, Language, Package, PackageType, Platform
from labels.testing.mocks import Mock, mocks
from labels.testing.utils import raises


def test_get_platform_value() -> None:
    assert PackageType.PythonPkg.get_platform_value() == Platform.PIP.value
    assert PackageType.NpmPkg.get_platform_value() == Platform.NPM.value
    assert PackageType.RustPkg.get_platform_value() == Platform.CARGO.value
    assert PackageType.DebPkg.get_platform_value() == Platform.DEBIAN.value
    assert PackageType.ApkPkg.get_platform_value() == Platform.APK.value
    assert PackageType.UnknownPkg.get_platform_value() is None


def test_health_metadata_latest_version_created_at_validation() -> None:
    with raises(ValidationError):
        HealthMetadata(
            latest_version="1.0.0",
            latest_version_created_at="",
            authors="Author Name",
        )

    assert HealthMetadata(
        latest_version="1.0.0",
        latest_version_created_at="2025-01-01T12:00:00+00:00",
        authors="Author Name",
    )


def test_check_licenses_min_length() -> None:
    with raises(ValidationError):
        Package(
            name="test-package",
            version="1.0.0",
            language=Language.PYTHON,
            licenses=[""],
            locations=[],
            type=PackageType.PythonPkg,
            p_url="pkg:python/test-package@1.0.0",
        )


@mocks(
    mocks=[
        Mock(
            module=json,
            target="dumps",
            target_type="function",
            expected=MagicMock(
                side_effect=Exception("Test error"),
            ),
        ),
    ],
)
async def test_id_by_hash_exception() -> None:
    package = Package(
        name="test-package",
        version="1.0.0",
        language=Language.PYTHON,
        licenses=["MIT"],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:python/test-package@1.0.0",
    )

    result = package.id_by_hash()
    assert result.startswith("Could not build ID for object=")
    assert "Test error" in result


def test_package_name_validation() -> None:
    with raises(ValidationError):
        Package(
            name="",
            version="1.0.0",
            language=Language.PYTHON,
            licenses=["MIT"],
            locations=[],
            type=PackageType.PythonPkg,
            p_url="pkg:python/test-package@1.0.0",
        )


def test_package_equality() -> None:
    package1 = Package(
        name="test-package",
        version="1.0.0",
        language=Language.PYTHON,
        licenses=["MIT"],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:python/test-package@1.0.0",
    )

    assert package1 != "not a package"
    assert package1 != None  # noqa: E711
    assert package1 != 123

    package2 = Package(
        name="test-package",
        version="1.0.0",
        language=Language.PYTHON,
        licenses=["MIT"],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:python/test-package@1.0.0",
    )
    assert package1 == package2

    different_package = Package(
        name="other-package",
        version="1.0.0",
        language=Language.PYTHON,
        licenses=["MIT"],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:python/other-package@1.0.0",
    )
    assert package1 != different_package

    different_version = Package(
        name="test-package",
        version="2.0.0",
        language=Language.PYTHON,
        licenses=["MIT"],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:python/test-package@2.0.0",
    )
    assert package1 != different_version


def test_package_hash() -> None:
    package1 = Package(
        name="test-package",
        version="1.0.0",
        language=Language.PYTHON,
        licenses=["MIT"],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:python/test-package@1.0.0",
    )

    different_package = Package(
        name="other-package",
        version="1.0.0",
        language=Language.PYTHON,
        licenses=["MIT"],
        locations=[],
        type=PackageType.PythonPkg,
        p_url="pkg:python/other-package@1.0.0",
    )

    assert hash(package1) != hash(different_package)

    duplicate_package = Package.model_validate_json(package1.model_dump_json())
    package_set = {package1, duplicate_package, different_package}
    assert len(package_set) == 2
