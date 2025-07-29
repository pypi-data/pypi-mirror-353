from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, Location
from labels.model.release import Release
from labels.parsers.cataloger.alpine.package import ApkDBEntry, ParsedData, new_package, package_url


def test_package_url_basic() -> None:
    entry = ApkDBEntry(
        package="nginx",
        origin_package=None,
        maintainer="Nginx Maintainer <dev@nginx.com>",
        version="1.24.0-r14",
        architecture="x86_64",
        url="https://nginx.org/",
        description="HTTP and reverse proxy server",
        size="1000000",
        installed_size="2000000",
        dependencies=[],
        provides=[],
        checksum="abcdef123456",
        git_commit=None,
        files=[],
    )

    url = package_url(entry, None)
    assert url == "pkg:apk/nginx@1.24.0-r14?arch=x86_64"


def test_package_url_with_distro() -> None:
    entry = ApkDBEntry(
        package="nginx",
        origin_package=None,
        maintainer="Nginx Maintainer <dev@nginx.com>",
        version="1.24.0-r14",
        architecture="x86_64",
        url="https://nginx.org/",
        description="HTTP and reverse proxy server",
        size="1000000",
        installed_size="2000000",
        dependencies=[],
        provides=[],
        checksum="abcdef123456",
        git_commit=None,
        files=[],
    )

    distro = Release(
        id_="alpine",
        version_id="3.18.0",
        build_id=None,
    )

    url = package_url(entry, distro)
    assert url == (
        "pkg:apk/alpine/nginx@1.24.0-r14?arch=x86_64"
        "&distro=alpine-3.18.0&distro_id=alpine&distro_version_id=3.18.0"
    )


def test_package_url_with_origin_package() -> None:
    entry = ApkDBEntry(
        package="py3-pip",
        origin_package="python3",
        maintainer="Python Maintainers <python@alpine.org>",
        version="23.0.1-r0",
        architecture="x86_64",
        url="https://pip.pypa.io/",
        description="The PyPA recommended tool for installing Python packages",
        size="1000000",
        installed_size="2000000",
        dependencies=[],
        provides=[],
        checksum="abcdef123456",
        git_commit=None,
        files=[],
    )

    distro = Release(
        id_="alpine",
        version_id="3.18.0",
        build_id=None,
    )

    url = package_url(entry, distro)
    assert url == (
        "pkg:apk/alpine/py3-pip@23.0.1-r0?arch=x86_64"
        "&distro=alpine-3.18.0&distro_id=alpine&distro_version_id=3.18.0"
        "&upstream=python3"
    )


def test_package_url_with_build_id() -> None:
    entry = ApkDBEntry(
        package="nginx",
        origin_package=None,
        maintainer="Nginx Maintainer <dev@nginx.com>",
        version="1.24.0-r14",
        architecture="x86_64",
        url="https://nginx.org/",
        description="HTTP and reverse proxy server",
        size="1000000",
        installed_size="2000000",
        dependencies=[],
        provides=[],
        checksum="abcdef123456",
        git_commit=None,
        files=[],
    )

    distro = Release(
        id_="alpine",
        version_id="",
        build_id="20230901",
    )

    url = package_url(entry, distro)
    assert (
        url == "pkg:apk/alpine/nginx@1.24.0-r14?arch=x86_64&distro=alpine-20230901&distro_id=alpine"
    )


def test_new_package_empty_name_and_version() -> None:
    data = ParsedData(
        license=None,
        apk_db_entry=ApkDBEntry(
            package="",
            origin_package="alpine-baselayout",
            maintainer="Natanael Copa <ncopa@alpinelinux.org>",
            version="",
            description="Alpine base dir structure and init scripts",
            architecture="x86_64",
            url=("https://git.alpinelinux.org/cgit/aports/tree/main/alpine-baselayout"),
            size="11664",
            installed_size="77824",
            dependencies=[],
            provides=[],
            checksum="Q15ffjKT28lB7iSXjzpI/eDdYRCwM=",
            git_commit="bd965a7ebf7fd8f07d7a0cc0d7375bf3e4eb9b24",
            files=[],
        ),
    )

    assert new_package(data=data, release=None, db_location=Location()) is None


async def test_new_package_malformed_warning(caplog: pytest.LogCaptureFixture) -> None:
    data = ParsedData(
        license=None,
        apk_db_entry=ApkDBEntry(
            package="test-package",
            origin_package="alpine-baselayout",
            maintainer="Natanael Copa <ncopa@alpinelinux.org>",
            version="version",
            description="Alpine base dir structure and init scripts",
            architecture="x86_64",
            url=("https://git.alpinelinux.org/cgit/aports/tree/main/alpine-baselayout"),
            size="11664",
            installed_size="77824",
            dependencies=[],
            provides=[],
            checksum="Q15ffjKT28lB7iSXjzpI/eDdYRCwM=",
            git_commit="bd965a7ebf7fd8f07d7a0cc0d7375bf3e4eb9b24",
            files=[],
        ),
    )

    dummy_location = Location(access_path="./", coordinates=Coordinates(real_path="./"))

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

        assert new_package(data=data, release=None, db_location=dummy_location) is None
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )
