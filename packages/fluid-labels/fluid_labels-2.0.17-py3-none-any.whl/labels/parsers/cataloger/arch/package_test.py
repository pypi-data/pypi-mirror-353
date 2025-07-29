from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, Location
from labels.model.release import Release
from labels.parsers.cataloger.arch import package as alpm_package
from labels.parsers.cataloger.arch.package import AlpmDBEntry, new_package, package_url
from labels.testing.mocks import Mock, mocks


def test_package_url_basic() -> None:
    entry = AlpmDBEntry(
        package="pacman",
        base_package="",
        packager="Pacman Maintainer <dev@archlinux.org>",
        version="6.0.2-1",
        architecture="x86_64",
        url="https://archlinux.org/",
        description="A library-based package manager",
        size=1000000,
        files=[],
    )

    url = package_url(entry, None)
    assert url == "pkg:alpm/pacman@6.0.2-1?arch=x86_64"


def test_package_url_with_distro() -> None:
    entry = AlpmDBEntry(
        package="pacman",
        base_package="",
        packager="Pacman Maintainer <dev@archlinux.org>",
        version="6.0.2-1",
        architecture="x86_64",
        url="https://archlinux.org/",
        description="A library-based package manager",
        size=1000000,
        files=[],
    )

    distro = Release(
        id_="arch",
        version_id="2025.05.01",
        build_id=None,
    )

    url = package_url(entry, distro)
    assert url == "pkg:alpm/pacman@6.0.2-1?arch=x86_64&distro=arch-2025.05.01"


def test_new_package_empty_name_and_version() -> None:
    entry = AlpmDBEntry(
        package="",
        base_package="base",
        packager="Arch Maintainer <dev@archlinux.org>",
        version="",
        description="Base package",
        architecture="x86_64",
        url="https://archlinux.org/",
        size=1000000,
        files=[],
    )

    assert new_package(entry=entry, release=None, db_location=Location()) is None


@mocks(
    mocks=[
        Mock(
            module=alpm_package,
            target="package_url",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_new_package_malformed_warning(caplog: pytest.LogCaptureFixture) -> None:
    entry = AlpmDBEntry(
        package="test-package",
        base_package="base",
        packager="Arch Maintainer <dev@archlinux.org>",
        version="version",
        description="Base package",
        architecture="x86_64",
        url="https://archlinux.org/",
        size=1000000,
        files=[],
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

        assert new_package(entry=entry, release=None, db_location=dummy_location) is None
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


def test_package_url_with_base_package() -> None:
    entry = AlpmDBEntry(
        package="pacman",
        base_package="base-pacman",
        packager="Pacman Maintainer <dev@archlinux.org>",
        version="6.0.2-1",
        architecture="x86_64",
        url="https://archlinux.org/",
        description="A library-based package manager",
        size=1000000,
        files=[],
    )

    url = package_url(entry, None)
    assert url == "pkg:alpm/pacman@6.0.2-1?arch=x86_64&upstream=base-pacman"
