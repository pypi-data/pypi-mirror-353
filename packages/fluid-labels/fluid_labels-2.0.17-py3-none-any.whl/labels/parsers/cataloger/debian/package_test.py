from io import StringIO
from typing import cast
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

import labels.parsers.cataloger.debian.parse_copyright
import labels.utils.licenses.validation
from labels.model.file import Coordinates, Location
from labels.model.package import Digest, Language, Package, PackageType
from labels.model.release import Release
from labels.parsers.cataloger.debian.model import DpkgDBEntry, DpkgFileRecord
from labels.parsers.cataloger.debian.package import (
    add_licenses,
    fetch_conffile_contents,
    fetch_copyright_contents,
    fetch_md5_content,
    get_additional_file_listing,
    md5_key,
    merge_file_listing,
    new_dpkg_package,
    package_url,
)
from labels.resolvers.directory import Directory
from labels.testing.utils.pytest_marks import parametrize_sync

MOCK_MD5_CONTENT = (
    "d41d8cd98f00b204e9800998ecf8427e  /etc/test.conf\n"
    "b026324c6904b2a9cb4b88d6d61c81d1  /usr/bin/test\n"
)

DPKG_STATUS_PATH = "/var/lib/dpkg/status"
DPKG_MD5SUMS_PATH = "/var/lib/dpkg/info/test-pkg:amd64.md5sums"


@parametrize_sync(
    args=["distro", "metadata", "expected"],
    cases=[
        [
            Release(id_="debian", version_id="11", id_like=["debian"]),
            DpkgDBEntry(package="p", version="v"),
            "pkg:deb/debian/p@v?distro=debian-11&distro_id=debian&distro_version_id=11",
        ],
        [
            Release(id_="debian", version_id="11"),
            DpkgDBEntry(package="p", version="v"),
            "pkg:deb/debian/p@v?distro=debian-11&distro_id=debian&distro_version_id=11",
        ],
        [
            Release(id_="ubuntu", version_id="16.04", id_like=["debian"]),
            DpkgDBEntry(package="p", version="v", architecture="a"),
            "pkg:deb/ubuntu/p@v?arch=a&distro=ubuntu-16.04&distro_id=ubuntu&distro_version_id=16.04",
        ],
        [
            Release(id_="debian", version_id="11", id_like=["debian"]),
            DpkgDBEntry(package="p", source="s", version="v"),
            "pkg:deb/debian/p@v?distro=debian-11&distro_id=debian&distro_version_id=11&upstream=s",
        ],
        [
            Release(id_="debian", version_id="11", id_like=["debian"]),
            DpkgDBEntry(package="p", source="s", version="v", source_version="2.3"),
            "pkg:deb/debian/p@v?distro=debian-11&distro_id=debian&distro_version_id=11&upstream=s%402.3",
        ],
        [
            Release(id_="debian", version_id=""),
            DpkgDBEntry(package="p", version="v"),
            "pkg:deb/debian/p@v?distro=debian&distro_id=debian",
        ],
    ],
)
def test_package_url(distro: Release, metadata: DpkgDBEntry, expected: str | None) -> None:
    actual = package_url(metadata, distro)
    assert expected == actual


@parametrize_sync(
    args=["metadata", "expected"],
    cases=[
        [
            DpkgDBEntry(package="test-pkg", architecture="amd64"),
            "test-pkg:amd64",
        ],
        [
            DpkgDBEntry(package="test-pkg", architecture="all"),
            "test-pkg",
        ],
        [
            DpkgDBEntry(package="test-pkg", architecture=""),
            "test-pkg",
        ],
    ],
)
def test_md5_key(metadata: DpkgDBEntry, expected: str) -> None:
    result = md5_key(metadata)
    assert result == expected


def test_fetch_md5_content() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())

    with (
        patch.object(
            Directory,
            "relative_file_path",
            return_value=Location(coordinates=Coordinates(real_path=DPKG_MD5SUMS_PATH)),
        ),
        patch.object(
            Directory,
            "file_contents_by_location",
            return_value=StringIO(MOCK_MD5_CONTENT),
        ),
    ):
        result = fetch_md5_content(resolver, location, entry)
        assert result is not None
        reader, loc = result
        assert reader is not None
        assert loc is not None
        assert loc.coordinates is not None
        assert loc.coordinates.real_path == DPKG_MD5SUMS_PATH


def test_fetch_md5_content_status_d_path() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path="/var/lib/dpkg/status.d/status"))
    resolver = Directory("/", exclude=())

    with (
        patch.object(
            Directory,
            "relative_file_path",
            return_value=Location(
                coordinates=Coordinates(real_path="/var/lib/dpkg/status.d/test-pkg:amd64.md5sums"),
            ),
        ),
        patch.object(
            Directory,
            "file_contents_by_location",
            return_value=StringIO(MOCK_MD5_CONTENT),
        ),
    ):
        result = fetch_md5_content(resolver, location, entry)
        assert result is not None
        reader, loc = result
        assert reader is not None
        assert loc is not None
        assert loc.coordinates is not None
        assert loc.coordinates.real_path == "/var/lib/dpkg/status.d/test-pkg:amd64.md5sums"


def test_fetch_md5_content_non_status_d() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path="/var/lib/dpkg/other/status"))
    resolver = Directory("/", exclude=())

    with (
        patch.object(
            Directory,
            "relative_file_path",
            return_value=Location(
                coordinates=Coordinates(
                    real_path="/var/lib/dpkg/other/info/test-pkg:amd64.md5sums",
                ),
            ),
        ),
        patch.object(
            Directory,
            "file_contents_by_location",
            return_value=StringIO(MOCK_MD5_CONTENT),
        ),
    ):
        result = fetch_md5_content(resolver, location, entry)
        assert result is not None
        reader, loc = result
        assert reader is not None
        assert loc is not None
        assert loc.coordinates is not None
        assert loc.coordinates.real_path == "/var/lib/dpkg/other/info/test-pkg:amd64.md5sums"


def test_fetch_md5_content_no_coordinates() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=None)
    resolver = Directory("/", exclude=())

    result = fetch_md5_content(resolver, location, entry)
    assert result is None


def test_fetch_md5_content_no_file() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())

    with patch.object(Directory, "relative_file_path", return_value=None):
        result = fetch_md5_content(resolver, location, entry)
        assert result is None


def test_fetch_md5_content_read_failure() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())

    with (
        patch.object(
            Directory,
            "relative_file_path",
            return_value=Location(coordinates=Coordinates(real_path=DPKG_MD5SUMS_PATH)),
        ),
        patch.object(Directory, "file_contents_by_location", return_value=None),
    ):
        result = fetch_md5_content(resolver, location, entry)
        assert result is not None
        reader, loc = result
        assert reader is None
        assert loc is not None


def test_fetch_conffile_contents() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())

    with (
        patch.object(
            Directory,
            "relative_file_path",
            return_value=Location(
                coordinates=Coordinates(real_path="/var/lib/dpkg/info/test-pkg:amd64.conffiles"),
            ),
        ),
        patch.object(Directory, "file_contents_by_location", return_value=StringIO("test content")),
    ):
        result = fetch_conffile_contents(resolver, location, entry)
        assert result is not None
        reader, loc = result
        assert reader is not None
        assert loc is not None


def test_fetch_conffile_contents_no_coordinates() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=None)
    resolver = Directory("/", exclude=())

    result = fetch_conffile_contents(resolver, location, entry)
    assert result is None


def test_fetch_conffile_contents_read_failure() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())

    with (
        patch.object(
            Directory,
            "relative_file_path",
            return_value=Location(
                coordinates=Coordinates(real_path="/var/lib/dpkg/info/test-pkg:amd64.conffiles"),
            ),
        ),
        patch.object(Directory, "file_contents_by_location", return_value=None),
    ):
        result = fetch_conffile_contents(resolver, location, entry)
        assert result is not None
        reader, loc = result
        assert reader is None
        assert loc is not None


def test_get_additional_file_listing() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())

    with (
        patch.object(
            Directory,
            "relative_file_path",
            return_value=Location(coordinates=Coordinates(real_path=DPKG_MD5SUMS_PATH)),
        ),
        patch.object(
            Directory,
            "file_contents_by_location",
            return_value=StringIO(MOCK_MD5_CONTENT),
        ),
    ):
        files, locations = get_additional_file_listing(resolver, location, entry)
        assert len(files) > 0
        assert len(locations) > 0


def test_get_additional_file_listing_no_conffiles() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())

    side_effects: list[Location | None] = [
        Location(coordinates=Coordinates(real_path=DPKG_MD5SUMS_PATH)),
        None,
        None,
    ]

    with (
        patch.object(Directory, "relative_file_path", side_effect=side_effects),
        patch.object(
            Directory,
            "file_contents_by_location",
            return_value=StringIO(MOCK_MD5_CONTENT),
        ),
    ):
        files, locations = get_additional_file_listing(resolver, location, entry)
        assert len(files) == 2
        assert len(locations) == 1
        assert all(f.path in ["/etc/test.conf", "/usr/bin/test"] for f in files)


def test_get_additional_file_listing_when_fetch_conffiles_returns_none() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())

    with (
        patch("labels.parsers.cataloger.debian.package.fetch_conffile_contents", return_value=None),
        patch.object(
            Directory,
            "relative_file_path",
            return_value=Location(coordinates=Coordinates(real_path=DPKG_MD5SUMS_PATH)),
        ),
        patch.object(
            Directory,
            "file_contents_by_location",
            return_value=StringIO(MOCK_MD5_CONTENT),
        ),
    ):
        files, locations = get_additional_file_listing(resolver, location, entry)
        assert len(files) == 2
        assert len(locations) == 1
        assert all(f.path in ["/etc/test.conf", "/usr/bin/test"] for f in files)


def test_get_additional_file_listing_when_md5_returns_none() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())

    with (
        patch(
            "labels.parsers.cataloger.debian.package.fetch_md5_content",
            return_value=(None, None),
        ),
        patch("labels.parsers.cataloger.debian.package.fetch_conffile_contents", return_value=None),
    ):
        files, locations = get_additional_file_listing(resolver, location, entry)
        assert len(files) == 0
        assert len(locations) == 0


def test_merge_file_listing() -> None:
    initial_file = DpkgFileRecord(path="/usr/bin/initial", digest=None)
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64", files=[initial_file])
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())
    pkg = Package(
        name="test-pkg",
        version="1.0.0",
        licenses=[],
        p_url="pkg:deb//test-pkg@1.0.0?arch=amd64",
        locations=[location],
        type=PackageType.DebPkg,
        language=Language.UNKNOWN_LANGUAGE,
        metadata=entry,
        found_by=None,
    )

    with (
        patch.object(
            Directory,
            "relative_file_path",
            return_value=Location(coordinates=Coordinates(real_path=DPKG_MD5SUMS_PATH)),
        ),
        patch.object(
            Directory,
            "file_contents_by_location",
            return_value=StringIO(MOCK_MD5_CONTENT),
        ),
    ):
        merge_file_listing(resolver, location, pkg)

        metadata = pkg.metadata
        assert metadata is not None
        assert isinstance(metadata, DpkgDBEntry)
        assert len(metadata.files or []) > 1
        assert len(pkg.locations) > 1


def test_merge_file_listing_no_metadata() -> None:
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())
    pkg = Package(
        name="test-pkg",
        version="1.0.0",
        licenses=[],
        p_url="pkg:deb//test-pkg@1.0.0?arch=amd64",
        locations=[location],
        type=PackageType.DebPkg,
        language=Language.UNKNOWN_LANGUAGE,
        metadata=DpkgDBEntry(package="test-pkg", architecture="amd64"),
        found_by=None,
    )

    with patch.object(Directory, "relative_file_path", return_value=None):
        merge_file_listing(resolver, location, pkg)
        assert isinstance(pkg.metadata, DpkgDBEntry)
        assert pkg.metadata.files is None or len(pkg.metadata.files) == 0


def test_merge_file_listing_no_files() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64", files=[])
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())
    pkg = Package(
        name="test-pkg",
        version="1.0.0",
        licenses=[],
        p_url="pkg:deb//test-pkg@1.0.0?arch=amd64",
        locations=[location],
        type=PackageType.DebPkg,
        language=Language.UNKNOWN_LANGUAGE,
        metadata=entry,
        found_by=None,
    )

    with (
        patch.object(
            Directory,
            "relative_file_path",
            return_value=Location(coordinates=Coordinates(real_path=DPKG_MD5SUMS_PATH)),
        ),
        patch.object(
            Directory,
            "file_contents_by_location",
            return_value=StringIO(MOCK_MD5_CONTENT),
        ),
    ):
        merge_file_listing(resolver, location, pkg)
        assert isinstance(pkg.metadata, DpkgDBEntry)
        assert pkg.metadata.files is not None
        assert len(pkg.metadata.files) > 0


def test_merge_file_listing_with_existing_files() -> None:
    existing_files = [
        DpkgFileRecord(path="/usr/bin/test", digest=Digest(value="123", algorithm="md5")),
        DpkgFileRecord(path="/etc/test.conf", digest=Digest(value="456", algorithm="md5")),
    ]
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64", files=existing_files)
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())
    pkg = Package(
        name="test-pkg",
        version="1.0.0",
        licenses=[],
        p_url="pkg:deb//test-pkg@1.0.0?arch=amd64",
        locations=[location],
        type=PackageType.DebPkg,
        language=Language.UNKNOWN_LANGUAGE,
        metadata=entry,
        found_by=None,
    )

    with (
        patch.object(
            Directory,
            "relative_file_path",
            return_value=Location(coordinates=Coordinates(real_path=DPKG_MD5SUMS_PATH)),
        ),
        patch.object(
            Directory,
            "file_contents_by_location",
            return_value=StringIO(MOCK_MD5_CONTENT),
        ),
    ):
        merge_file_listing(resolver, location, pkg)
        metadata = cast(DpkgDBEntry, pkg.metadata)
        assert metadata.files is not None
        assert len(metadata.files) == 2
        assert all(f.path in ["/usr/bin/test", "/etc/test.conf"] for f in metadata.files)
        assert metadata.files == sorted(metadata.files, key=get_path)


def test_add_licenses() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())
    pkg = Package(
        name="test-pkg",
        version="1.0.0",
        licenses=[],
        p_url="pkg:deb//test-pkg@1.0.0?arch=amd64",
        locations=[location],
        type=PackageType.DebPkg,
        language=Language.UNKNOWN_LANGUAGE,
        metadata=entry,
        found_by=None,
    )

    with (
        patch.object(
            Directory,
            "relative_file_path",
            return_value=Location(
                coordinates=Coordinates(real_path="/usr/share/doc/test-pkg/copyright"),
            ),
        ),
        patch.object(
            Directory,
            "file_contents_by_location",
            return_value=StringIO("License: MIT\nSome copyright text"),
        ),
        patch.object(
            labels.parsers.cataloger.debian.parse_copyright,
            "parse_licenses_from_copyright",
            return_value=cast(list[str], ["MIT"]),
        ),
        patch.object(
            labels.utils.licenses.validation,
            "validate_licenses",
            return_value=cast(list[str], ["MIT"]),
        ),
    ):
        add_licenses(resolver, location, pkg)
        assert pkg.licenses == ["MIT"]


async def test_add_licenses_no_copyright_file(caplog: pytest.LogCaptureFixture) -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())
    pkg = Package(
        name="test-pkg",
        version="1.0.0",
        licenses=[],
        p_url="pkg:deb//test-pkg@1.0.0?arch=amd64",
        locations=[location],
        type=PackageType.DebPkg,
        language=Language.UNKNOWN_LANGUAGE,
        metadata=entry,
        found_by=None,
    )

    with (
        patch.object(
            Directory,
            "relative_file_path",
            return_value=Location(
                coordinates=Coordinates(real_path="/usr/share/doc/test-pkg/copyright"),
            ),
        ),
        patch.object(Directory, "file_contents_by_location", return_value=None),
    ):
        add_licenses(resolver, location, pkg)
        assert pkg.licenses == []
        assert "Failed to fetch deb copyright contents (package=test-pkg)" in caplog.text


def test_fetch_copyright_contents() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())

    with (
        patch.object(
            Directory,
            "relative_file_path",
            return_value=Location(
                coordinates=Coordinates(real_path="/var/lib/dpkg/info/test-pkg:amd64.md5sums"),
            ),
        ),
        patch.object(
            Directory,
            "file_contents_by_location",
            return_value=StringIO("/etc/test.conf\n/usr/bin/test\n"),
        ),
    ):
        reader, loc = fetch_copyright_contents(resolver, location, entry)
        assert reader is not None
        assert loc is not None


def test_fetch_copyright_contents_no_coordinates() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=None)
    resolver = None

    result = fetch_copyright_contents(resolver, location, entry)
    assert result == (None, None)


def test_fetch_copyright_contents_no_file() -> None:
    entry = DpkgDBEntry(package="test-pkg", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())

    with patch.object(Directory, "relative_file_path", return_value=None):
        result = fetch_copyright_contents(resolver, location, entry)
        assert result == (None, None)


@parametrize_sync(
    args=["entry", "expected_result"],
    cases=[
        [
            DpkgDBEntry(
                package="test-pkg",
                version="1.0.0",
                architecture="amd64",
                source="src-pkg",
                source_version="2.0.0",
            ),
            True,
        ],
        [
            DpkgDBEntry(
                package="test-pkg",
                version="1.0.0",
                architecture="amd64",
            ),
            False,
        ],
        [
            DpkgDBEntry(
                package="",
                version="",
            ),
            None,
        ],
    ],
)
def test_new_dpkg_package_variations(entry: DpkgDBEntry, expected_result: bool | None) -> None:
    result = new_dpkg_package(entry, Location(), None)

    if expected_result is None:
        assert result is None
    elif expected_result:
        assert isinstance(result, tuple)
        binary_pkg, source_pkg = result
        assert isinstance(binary_pkg, Package)
        assert isinstance(source_pkg, Package)
        assert binary_pkg.name == entry.package
        assert source_pkg.name == entry.source
    else:
        assert isinstance(result, Package)
        assert result.name == entry.package


def test_new_dpkg_package_calls_merge_and_licenses() -> None:
    entry = DpkgDBEntry(package="test-pkg", version="1.0.0", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))
    resolver = Directory("/", exclude=())

    with (
        patch("labels.parsers.cataloger.debian.package.merge_file_listing") as mock_merge,
        patch("labels.parsers.cataloger.debian.package.add_licenses") as mock_licenses,
    ):
        result = new_dpkg_package(entry, location, resolver)

        assert isinstance(result, Package)
        mock_merge.assert_called_once_with(resolver, location, result)
        mock_licenses.assert_called_once_with(resolver, location, result)


def test_new_dpkg_package_no_resolver_skips_merge_and_licenses() -> None:
    entry = DpkgDBEntry(package="test-pkg", version="1.0.0", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))

    with (
        patch("labels.parsers.cataloger.debian.package.merge_file_listing") as mock_merge,
        patch("labels.parsers.cataloger.debian.package.add_licenses") as mock_licenses,
    ):
        result = new_dpkg_package(entry, location, None)

        assert isinstance(result, Package)
        mock_merge.assert_not_called()
        mock_licenses.assert_not_called()


async def test_new_dpkg_package_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    entry = DpkgDBEntry(package="test-pkg", version="1.0.0", architecture="amd64")
    location = Location(coordinates=Coordinates(real_path=DPKG_STATUS_PATH))

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
        result = new_dpkg_package(entry, location, None)
        assert result is None
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


def get_path(record: DpkgFileRecord) -> str:
    return record.path
