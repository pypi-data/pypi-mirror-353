import logging
import os
import tempfile
import zipfile
from io import TextIOWrapper
from pathlib import Path
from unittest.mock import patch

import pytest
from _pytest.logging import LogCaptureFixture
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.java.parse_android_apk import is_safe_path, parse_apk, safe_extract
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_apk() -> None:
    test_data_path = get_test_data_path("dependencies/java/android/antennapod_3080095.apk")
    expected_packages = [
        Package(
            name="preference",
            version="1.1.1",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=None,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:maven/androidx.preference/preference@1.1.1",
        ),
        Package(
            name="annotation-experimental",
            version="1.4.0",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=None,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:maven/androidx.annotation/annotation-experimental@1.4.0",
        ),
        Package(
            name="versionedparcelable",
            version="1.1.1",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=None,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:maven/androidxedparcelable/versionedparcelable@1.1.1",
        ),
        Package(
            name="core-ktx",
            version="1.13.0",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=None,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:maven/androidx.core/core-ktx@1.13.0",
        ),
        Package(
            name="transition",
            version="1.5.0",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=None,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:maven/androidx.transition/transition@1.5.0",
        ),
    ]

    with Path(test_data_path).open("rb") as binary_reader:
        reader = TextIOWrapper(binary_reader)
        pkgs, relations = parse_apk(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )

        for expected_pkg in expected_packages:
            assert any(
                p.name == expected_pkg.name
                and p.version == expected_pkg.version
                and p.p_url == expected_pkg.p_url
                for p in pkgs
            ), f"No se encontró el paquete {expected_pkg.name} versión {expected_pkg.version}"
        assert relations == []


def test_is_safe_path() -> None:
    assert is_safe_path("/tmp", "/tmp/file.txt")  # noqa: S108
    assert is_safe_path("/tmp", "/tmp/subdir/file.txt")  # noqa: S108
    assert is_safe_path("/tmp", "/tmp")  # noqa: S108

    assert not is_safe_path("/tmp", "/etc/passwd")  # noqa: S108
    assert not is_safe_path("/tmp", "/var/log/syslog")  # noqa: S108
    assert not is_safe_path("/tmp", "/root/.ssh/id_rsa")  # noqa: S108


def test_safe_extract_path_validation() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "test.zip")
        extract_dir = os.path.join(temp_dir, "extract")
        Path(extract_dir).mkdir(parents=True)

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("/etc/passwd", "malicious content 1")
            zf.writestr("/var/log/syslog", "malicious content 2")
            zf.writestr("C:\\Windows\\System32\\config", "malicious content 3")

            zf.writestr("../malicious.txt", "malicious content 4")
            zf.writestr("../../malicious.txt", "malicious content 5")

            zf.writestr("./malicious.txt", "malicious content 6")
            zf.writestr("./../malicious.txt", "malicious content 7")

            zf.writestr("safe.txt", "safe content 1")
            zf.writestr("subdir/safe.txt", "safe content 2")

        with zipfile.ZipFile(zip_path, "r") as zf:
            safe_extract(zf, extract_dir)

        assert not Path(extract_dir).joinpath("etc/passwd").exists()
        assert not Path(extract_dir).joinpath("var/log/syslog").exists()
        assert not Path(extract_dir).joinpath("Windows/System32/config").exists()
        assert not Path(extract_dir).joinpath("../malicious.txt").exists()
        assert not Path(extract_dir).joinpath("../../malicious.txt").exists()
        assert not Path(extract_dir).joinpath("./malicious.txt").exists()
        assert not Path(extract_dir).joinpath("./../malicious.txt").exists()

        assert Path(extract_dir).joinpath("safe.txt").exists()
        assert Path(extract_dir).joinpath("subdir/safe.txt").exists()


def test_safe_extract_exception_handling(caplog: LogCaptureFixture) -> None:
    caplog.set_level(logging.ERROR)
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "test.zip")
        extract_dir = os.path.join(temp_dir, "extract")
        Path(extract_dir).mkdir(parents=True)

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("normal.txt", "normal content")
            zf.writestr("invalid_file.txt", "invalid content")
            for info in zf.infolist():
                if info.filename == "invalid_file.txt":
                    info.external_attr = 0o777 << 16
                    info.CRC = 0

        with zipfile.ZipFile(zip_path, "r") as zf:
            safe_extract(zf, extract_dir)

        assert Path(extract_dir).joinpath("normal.txt").exists()
        assert "Error extracting invalid_file.txt" in caplog.text


def test_parse_apk_malformed_warning(caplog: pytest.LogCaptureFixture) -> None:
    test_data_path = get_test_data_path("dependencies/java/android/antennapod_3080095.apk")

    with Path(test_data_path).open("rb") as binary_reader:
        reader = TextIOWrapper(binary_reader)
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

            pkgs, relations = parse_apk(
                None,
                None,
                LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
            )

            assert pkgs == []
            assert relations == []
            assert (
                "Malformed package. Required fields are missing or data types are incorrect."
                in caplog.text
            )


def create_invalid_apk(temp_dir: str) -> str:
    apk_path = os.path.join(temp_dir, "invalid.apk")
    with zipfile.ZipFile(apk_path, "w") as zf:
        meta_inf = "META-INF"
        zf.writestr(f"{meta_inf}/group_.version", "1.0.0")
        zf.writestr(f"{meta_inf}/_artifact.version", "1.0.0")
        zf.writestr(f"{meta_inf}/group_artifact.version", "")
    return apk_path


def test_parse_apk_missing_required_values(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    with tempfile.TemporaryDirectory() as temp_dir:
        apk_path = create_invalid_apk(temp_dir)

        with Path(apk_path).open("rb") as binary_reader:
            reader = TextIOWrapper(binary_reader)
            pkgs, relations = parse_apk(
                None,
                None,
                LocationReadCloser(location=new_location(apk_path), read_closer=reader),
            )

        assert pkgs == []
        assert relations == []


def test_parse_apk_no_meta_inf() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        apk_path = os.path.join(temp_dir, "empty.apk")
        with zipfile.ZipFile(apk_path, "w") as zf:
            zf.writestr("AndroidManifest.xml", "<?xml version='1.0' encoding='utf-8'?>")

        with Path(apk_path).open("rb") as binary_reader:
            reader = TextIOWrapper(binary_reader)
            pkgs, relations = parse_apk(
                None,
                None,
                LocationReadCloser(location=new_location(apk_path), read_closer=reader),
            )

            assert pkgs == []
            assert relations == []


def test_parse_apk_invalid_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        invalid_apk_path = os.path.join(temp_dir, "invalid.apk")
        Path(invalid_apk_path).write_text("This is not a valid APK file")

        with Path(invalid_apk_path).open("rb") as binary_reader:
            reader = TextIOWrapper(binary_reader)
            pkgs, relations = parse_apk(
                None,
                None,
                LocationReadCloser(location=new_location(invalid_apk_path), read_closer=reader),
            )

            assert pkgs == []
            assert relations == []


def test_safe_extract_unsafe_path() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "test.zip")
        extract_dir = os.path.join(temp_dir, "extract")
        Path(extract_dir).mkdir(parents=True)

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("subdir/../../etc/passwd", "malicious content")
            zf.writestr("safe.txt", "safe content")

        with zipfile.ZipFile(zip_path, "r") as zf:
            safe_extract(zf, extract_dir)

        assert not Path(extract_dir).joinpath("subdir/../../etc/passwd").exists()
        assert Path(extract_dir).joinpath("safe.txt").exists()
