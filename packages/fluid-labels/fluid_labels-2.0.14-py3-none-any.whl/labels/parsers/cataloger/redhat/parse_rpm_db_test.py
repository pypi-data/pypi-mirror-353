from io import BytesIO, TextIOWrapper
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

import labels.parsers.cataloger.redhat.parse_rpm_db
from labels.model.file import Coordinates, Location, LocationReadCloser
from labels.model.package import PackageType
from labels.model.release import Release
from labels.parsers.cataloger.generic.parser import Environment
from labels.parsers.cataloger.redhat.parse_rpm_db import (
    RpmDBEntry,
    create_rpm_file_record,
    new_redhat_package,
    package_url,
    parse_rpm_db,
    to_int,
)
from labels.parsers.cataloger.redhat.rpmdb.package import PackageInfo
from labels.resolvers.directory import Directory
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.pytest_marks import parametrize_sync


def test_package_url_basic() -> None:
    url = package_url(
        name="nginx",
        arch="x86_64",
        epoch=None,
        source_rpm="nginx-1.24.0-1.src.rpm",
        version="1.24.0",
        release="1",
        distro=None,
    )
    assert url == "pkg:rpm/nginx@1.24.0-1?arch=x86_64&upstream=nginx-1.24.0-1.src.rpm"


def test_package_url_with_distro() -> None:
    distro = Release(id_="redhat", version_id="8.6", build_id=None)
    url = package_url(
        name="nginx",
        arch="x86_64",
        epoch=1,
        source_rpm="nginx-1.24.0-1.src.rpm",
        version="1.24.0",
        release="1",
        distro=distro,
    )
    assert (
        url == "pkg:rpm/redhat/nginx@1.24.0-1?arch=x86_64&epoch=1&upstream=nginx-1.24.0-1.src.rpm"
    )


def test_package_url_with_epoch_only() -> None:
    url = package_url(
        name="nginx",
        arch=None,
        epoch=1,
        source_rpm="nginx-1.24.0-1.src.rpm",
        version="1.24.0",
        release="1",
        distro=None,
    )
    assert url == "pkg:rpm/nginx@1.24.0-1?epoch=1&upstream=nginx-1.24.0-1.src.rpm"


def test_package_url_without_arch_and_epoch() -> None:
    url = package_url(
        name="nginx",
        arch=None,
        epoch=None,
        source_rpm="nginx-1.24.0-1.src.rpm",
        version="1.24.0",
        release="1",
        distro=None,
    )
    assert url == "pkg:rpm/nginx@1.24.0-1?upstream=nginx-1.24.0-1.src.rpm"


def test_package_url_without_source() -> None:
    url = package_url(
        name="nginx",
        arch=None,
        epoch=None,
        source_rpm="",
        version="1.24.0",
        release="1",
        distro=None,
    )
    assert url == "pkg:rpm/nginx@1.24.0-1"


def test_new_redhat_package() -> None:
    entry = PackageInfo(
        name="nginx",
        version="1.24.0",
        epoch=None,
        arch="x86_64",
        release="1",
        source_rpm="nginx-1.24.0-1.src.rpm",
        vendor="Red Hat",
        size=12345,
        modularity_label="label",
        license="MIT",
    )

    location = Location(
        coordinates=Coordinates(real_path="./nginx.rpm", line=None),
    )
    resolver = Directory(root="./", exclude=())
    env = Environment(linux_release=Release(id_="redhat", version_id="8.6", build_id=None))

    package = new_redhat_package(
        entry=entry,
        resolver=resolver,
        location=location,
        env=env,
    )

    assert package
    assert package.name == "nginx"
    assert package.version == "1.24.0"
    assert package.type == PackageType.RpmPkg
    assert (
        package.p_url == "pkg:rpm/redhat/nginx@1.24.0-1?arch=x86_64&upstream=nginx-1.24.0-1.src.rpm"
    )
    metadata = package.metadata
    assert isinstance(metadata, RpmDBEntry)
    assert metadata.name == "nginx"
    assert metadata.version == "1.24.0"


def test_new_redhat_package_empty_name_and_version() -> None:
    entry = PackageInfo(
        name="",
        version="",
        epoch=None,
        arch="x86_64",
        release="1",
        source_rpm="nginx-1.24.0-1.src.rpm",
        vendor="Red Hat",
        size=12345,
        modularity_label="label",
        license="MIT",
    )

    location = Location(
        coordinates=Coordinates(real_path="./nginx.rpm", line=None),
    )
    resolver = Directory(root="./", exclude=())

    env = Environment(linux_release=Release(id_="redhat", version_id="8.6", build_id=None))

    package = new_redhat_package(
        entry=entry,
        resolver=resolver,
        location=location,
        env=env,
    )

    assert package is None


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.cataloger.redhat.parse_rpm_db,
            target="package_url",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_new_redhat_package_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    entry = PackageInfo(
        name="nginx",
        version="1.24.0",
        epoch=None,
        arch="x86_64",
        release="1",
        source_rpm="nginx-1.24.0-1.src.rpm",
        vendor="Red Hat",
        size=12345,
        modularity_label="label",
        license="MIT",
    )

    location = Location(
        coordinates=Coordinates(real_path="./nginx.rpm", line=None),
    )
    resolver = Directory(root="./", exclude=())

    env = Environment(linux_release=Release(id_="redhat", version_id="8.6", build_id=None))

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
        package = new_redhat_package(
            entry=entry,
            resolver=resolver,
            location=location,
            env=env,
        )

        assert package is None
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


@parametrize_sync(
    args=["value", "default", "expected"],
    cases=[
        [5, 0, 5],
        [None, 0, 0],
        [None, 10, 10],
        ["string", 3, 3],
    ],
)
def test_to_int(value: int | None, default: int, expected: int) -> None:
    assert to_int(value, default=default) == expected


def test_create_rpm_file_record_valid() -> None:
    resolver = MagicMock()
    resolver.files_by_path.return_value = True

    entry = MagicMock()
    entry.dir_names = ["/usr/lib"]

    attrs = (
        "libexample.so",
        0,
        "abcd1234",
        1,
        644,
        1024,
        "root",
        "root",
    )

    record = create_rpm_file_record(resolver, entry, attrs)

    assert record is not None
    assert record.path == "/usr/lib/libexample.so"
    assert record.mode == 644
    assert record.size == 1024
    assert record.digest.algorithm == "md5"
    assert record.digest.value == "abcd1234"
    assert record.username == "root"
    assert record.group_name == "root"


def test_create_rpm_file_record_invalid_dir_index() -> None:
    resolver = MagicMock()
    entry = MagicMock()
    entry.dir_names = ["/usr/lib"]

    attrs = (
        "libexample.so",
        "invalid",  # dir_index (should be int)
        "abcd1234",
        1,
        644,
        1024,
        "root",
        "root",
    )

    record = create_rpm_file_record(resolver, entry, attrs)  # type: ignore[arg-type]
    assert record is None


def test_create_rpm_file_record_missing_file_location() -> None:
    resolver = MagicMock()
    resolver.files_by_path.return_value = None

    entry = MagicMock()
    entry.dir_names = ["/usr/lib"]

    attrs = (
        "libexample.so",
        0,
        "abcd1234",
        1,
        644,
        1024,
        "root",
        "root",
    )

    record = create_rpm_file_record(resolver, entry, attrs)
    assert record is None


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.cataloger.redhat.parse_rpm_db,
            target="open_db",
            target_type="sync",
            expected=MagicMock(
                list_packages=lambda: [
                    PackageInfo(
                        name="test-package",
                        version="1.0.0",
                        epoch=None,
                        arch="x86_64",
                        release="1",
                        source_rpm="test-package-1.0.0-1.src.rpm",
                        vendor="Test Vendor",
                        size=1000,
                        modularity_label="",
                        license="MIT",
                    ),
                ],
            ),
        ),
    ],
)
async def test_parse_rpm_db_success() -> None:
    resolver = Directory(root="./", exclude=())
    env = Environment(linux_release=Release(id_="redhat", version_id="8.6", build_id=None))
    reader = LocationReadCloser(
        location=Location(
            coordinates=Coordinates(real_path="/test/path", line=None),
        ),
        read_closer=TextIOWrapper(BytesIO(b"test data")),
    )

    packages, relationships = parse_rpm_db(resolver, env, reader)

    assert len(packages) == 1
    assert len(relationships) == 0
    assert packages[0].name == "test-package"
    assert packages[0].version == "1.0.0"


async def test_parse_rpm_db_no_coordinates() -> None:
    resolver = Directory(root="./", exclude=())
    env = Environment(linux_release=None)
    reader = LocationReadCloser(
        location=Location(coordinates=None),
        read_closer=TextIOWrapper(BytesIO(b"test data")),
    )

    packages, relationships = parse_rpm_db(resolver, env, reader)

    assert len(packages) == 0
    assert len(relationships) == 0


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.cataloger.redhat.parse_rpm_db,
            target="open_db",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_parse_rpm_db_no_database() -> None:
    resolver = Directory(root="./", exclude=())
    env = Environment(linux_release=None)
    reader = LocationReadCloser(
        location=Location(
            coordinates=Coordinates(real_path="/test/path", line=None),
        ),
        read_closer=TextIOWrapper(BytesIO(b"test data")),
    )

    packages, relationships = parse_rpm_db(resolver, env, reader)

    assert len(packages) == 0
    assert len(relationships) == 0


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.cataloger.redhat.parse_rpm_db,
            target="open_db",
            target_type="sync",
            expected=MagicMock(list_packages=list),
        ),
    ],
)
async def test_parse_rpm_db_empty_package_list() -> None:
    resolver = Directory(root="./", exclude=())
    env = Environment(linux_release=None)
    reader = LocationReadCloser(
        location=Location(
            coordinates=Coordinates(real_path="/test/path", line=None),
        ),
        read_closer=TextIOWrapper(BytesIO(b"test data")),
    )

    packages, relationships = parse_rpm_db(resolver, env, reader)

    assert len(packages) == 0
    assert len(relationships) == 0


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.cataloger.redhat.parse_rpm_db,
            target="open_db",
            target_type="sync",
            expected=MagicMock(
                list_packages=lambda: [
                    PackageInfo(
                        name="",
                        version="",
                        epoch=None,
                        arch="x86_64",
                        release="1",
                        source_rpm="test-package-1.0.0-1.src.rpm",
                        vendor="Test Vendor",
                        size=1000,
                        modularity_label="",
                        license="MIT",
                    ),
                ],
            ),
        ),
    ],
)
async def test_parse_rpm_db_package_none() -> None:
    resolver = Directory(root="./", exclude=())
    env = Environment(linux_release=None)
    reader = LocationReadCloser(
        location=Location(
            coordinates=Coordinates(real_path="/test/path", line=None),
        ),
        read_closer=TextIOWrapper(BytesIO(b"test data")),
    )

    packages, relationships = parse_rpm_db(resolver, env, reader)

    assert len(packages) == 0
    assert len(relationships) == 0
