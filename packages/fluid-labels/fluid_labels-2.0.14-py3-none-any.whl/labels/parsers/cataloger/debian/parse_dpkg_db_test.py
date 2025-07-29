from io import StringIO
from pathlib import Path

import pytest

from labels.model.file import LocationReadCloser
from labels.model.package import Digest, Package
from labels.model.relationship import Relationship
from labels.parsers.cataloger.debian import parse_dpkg_db
from labels.parsers.cataloger.debian.model import DpkgDBEntry, DpkgFileRecord
from labels.testing.utils import raises
from labels.testing.utils.helpers import get_test_data_path
from labels.testing.utils.pytest_marks import parametrize_sync
from labels.utils.file import new_location


@parametrize_sync(
    args=["test_data", "expected"],
    cases=[
        [
            "dependencies/debian/status/single",
            [
                DpkgDBEntry(
                    package="apt",
                    source="apt-dev",
                    version="1.8.2",
                    architecture="amd64",
                    maintainer="APT Development Team <deity@lists.debian.org>",
                    installed_size=4064,
                    description="""commandline package manager
 This package provides commandline tools for searching and
 managing as well as querying information about packages
 as a low-level access to all features of the libapt-pkg library.
 .
 These include:
  * apt-get for retrieval of packages and information about them
    from authenticated sources and for installation, upgrade and
    removal of packages together with their dependencies
  * apt-cache for querying available information about installed
    as well as installable packages
  * apt-cdrom to use removable media as a source for packages
  * apt-config as an interface to the configuration settings
  * apt-key as an interface to manage authentication keys""",
                    provides=["apt-transport-https (= 1.8.2)"],
                    dependencies=[
                        "adduser",
                        "gpgv | gpgv2 | gpgv1",
                        "debian-archive-keyring",
                        "libapt-pkg5.0 (>= 1.7.0~alpha3~)",
                        "libc6 (>= 2.15)",
                        "libgcc1 (>= 1:3.0)",
                        "libgnutls30 (>= 3.6.6)",
                        "libseccomp2 (>= 1.0.1)",
                        "libstdc++6 (>= 5.2)",
                    ],
                    files=[
                        DpkgFileRecord(
                            path="/etc/apt/apt.conf.d/01autoremove",
                            digest=Digest(
                                algorithm="md5",
                                value="76120d358bc9037bb6358e737b3050b5",
                            ),
                            is_config_file=True,
                        ),
                        DpkgFileRecord(
                            path="/etc/cron.daily/apt-compat",
                            digest=Digest(
                                algorithm="md5",
                                value="49e9b2cfa17849700d4db735d04244f3",
                            ),
                            is_config_file=True,
                        ),
                        DpkgFileRecord(
                            path="/etc/kernel/postinst.d/apt-auto-removal",
                            digest=Digest(
                                algorithm="md5",
                                value="4ad976a68f045517cf4696cec7b8aa3a",
                            ),
                            is_config_file=True,
                        ),
                        DpkgFileRecord(
                            path="/etc/logrotate.d/apt",
                            digest=Digest(
                                algorithm="md5",
                                value="179f2ed4f85cbaca12fa3d69c2a4a1c3",
                            ),
                            is_config_file=True,
                        ),
                    ],
                    source_version="",
                    pre_dependencies=[],
                ),
            ],
        ],
        [
            "dependencies/debian/status/installed-size-4KB",
            [
                DpkgDBEntry(
                    package="apt",
                    source="apt-dev",
                    version="1.8.2",
                    architecture="amd64",
                    installed_size=4000,
                    maintainer="APT Development Team <deity@lists.debian.org>",
                    description="""commandline package manager
 This package provides commandline tools for searching and
 managing as well as querying information about packages
 as a low-level access to all features of the libapt-pkg library.
 .
 These include:
  * apt-get for retrieval of packages and information about them
    from authenticated sources and for installation, upgrade and
    removal of packages together with their dependencies
  * apt-cache for querying available information about installed
    as well as installable packages
  * apt-cdrom to use removable media as a source for packages
  * apt-config as an interface to the configuration settings
  * apt-key as an interface to manage authentication keys""",
                    provides=["apt-transport-https (= 1.8.2)"],
                    dependencies=[
                        "adduser",
                        "gpgv | gpgv2 | gpgv1",
                        "debian-archive-keyring",
                        "libapt-pkg5.0 (>= 1.7.0~alpha3~)",
                        "libc6 (>= 2.15)",
                        "libgcc1 (>= 1:3.0)",
                        "libgnutls30 (>= 3.6.6)",
                        "libseccomp2 (>= 1.0.1)",
                        "libstdc++6 (>= 5.2)",
                    ],
                    files=[],
                    source_version="",
                    pre_dependencies=[],
                ),
            ],
        ],
        [
            "dependencies/debian/status/multiple",
            [
                DpkgDBEntry(
                    package="no-version",
                    files=[],
                    source_version="",
                    pre_dependencies=[],
                    source="",
                    version="",
                    architecture="",
                    maintainer="",
                    installed_size=0,
                    description="",
                    provides=[],
                    dependencies=[],
                ),
                DpkgDBEntry(
                    package="tzdata",
                    version="2020a-0+deb10u1",
                    source="tzdata-dev",
                    architecture="all",
                    installed_size=3036,
                    maintainer=("GNU Libc Maintainers <debian-glibc@lists.debian.org>"),
                    description="""time zone and daylight-saving time data
 This package contains data required for the implementation of
 standard local time for many representative locations around the
 globe. It is updated periodically to reflect changes made by
 political bodies to time zone boundaries, UTC offsets, and
 daylight-saving rules.""",
                    provides=["tzdata-buster"],
                    dependencies=["debconf (>= 0.5) | debconf-2.0"],
                    files=[],
                    source_version="",
                    pre_dependencies=[],
                ),
                DpkgDBEntry(
                    package="util-linux",
                    version="2.33.1-0.1",
                    architecture="amd64",
                    installed_size=4327,
                    maintainer="LaMont Jones <lamont@debian.org>",
                    description="""miscellaneous system utilities
 This package contains a number of important utilities, most of which
 are oriented towards maintenance of your system. Some of the more
 important utilities included in this package allow you to view kernel
 messages, create new filesystems, view block device information,
 interface with real time clock, etc.""",
                    dependencies=["fdisk", "login (>= 1:4.5-1.1~)"],
                    pre_dependencies=[
                        "libaudit1 (>= 1:2.2.1)",
                        "libblkid1 (>= 2.31.1)",
                        "libc6 (>= 2.25)",
                        "libcap-ng0 (>= 0.7.9)",
                        "libmount1 (>= 2.25)",
                        "libpam0g (>= 0.99.7.1)",
                        "libselinux1 (>= 2.6-3~)",
                        "libsmartcols1 (>= 2.33)",
                        "libsystemd0",
                        "libtinfo6 (>= 6)",
                        "libudev1 (>= 183)",
                        "libuuid1 (>= 2.16)",
                        "zlib1g (>= 1:1.1.4)",
                    ],
                    files=[
                        DpkgFileRecord(
                            path="/etc/default/hwclock",
                            digest=Digest(
                                algorithm="md5",
                                value="3916544450533eca69131f894db0ca12",
                            ),
                            is_config_file=True,
                        ),
                        DpkgFileRecord(
                            path="/etc/init.d/hwclock.sh",
                            digest=Digest(
                                algorithm="md5",
                                value="1ca5c0743fa797ffa364db95bb8d8d8e",
                            ),
                            is_config_file=True,
                        ),
                        DpkgFileRecord(
                            path="/etc/pam.d/runuser",
                            digest=Digest(
                                algorithm="md5",
                                value="b8b44b045259525e0fae9e38fdb2aeeb",
                            ),
                            is_config_file=True,
                        ),
                        DpkgFileRecord(
                            path="/etc/pam.d/runuser-l",
                            digest=Digest(
                                algorithm="md5",
                                value="2106ea05877e8913f34b2c77fa02be45",
                            ),
                            is_config_file=True,
                        ),
                        DpkgFileRecord(
                            path="/etc/pam.d/su",
                            digest=Digest(
                                algorithm="md5",
                                value="ce6dcfda3b190a27a455bb38a45ff34a",
                            ),
                            is_config_file=True,
                        ),
                        DpkgFileRecord(
                            path="/etc/pam.d/su-l",
                            digest=Digest(
                                algorithm="md5",
                                value="756fef5687fecc0d986e5951427b0c4f",
                            ),
                            is_config_file=True,
                        ),
                    ],
                    source_version="",
                    source="",
                    provides=[],
                ),
            ],
        ],
    ],
)
def test_parse_dpkg_status(
    test_data: str,
    expected: list[DpkgDBEntry],
) -> None:
    test_data_path = get_test_data_path(test_data)
    with Path(test_data_path).open(encoding="utf-8") as reader:
        assert parse_dpkg_db.parse_dpkg_status(reader) == expected


def test_parse_dpkg_status_with_value_error(caplog: pytest.LogCaptureFixture) -> None:
    content = """Package: test-package
Version: 1.0
Installed-Size: invalid_size
Description: A test package
"""

    result = parse_dpkg_db.parse_dpkg_status(StringIO(content))

    assert len(result) == 1
    assert result[0].package == "test-package"
    assert result[0].version == "1.0"
    assert "Value error occurred" in caplog.text


def test_parse_dpkg_status_continuation_but_no_prev_key() -> None:
    content = """ continuation line without previous key"""

    result = parse_dpkg_db.parse_dpkg_status(StringIO(content))

    assert result == []


@parametrize_sync(
    args=["line", "expected"],
    cases=[
        ["test (1.2.3)", ("test", "1.2.3")],
        ["test", ("test", "")],
        ["", ("", "")],
    ],
)
def test_source_version_extract(line: str, expected: tuple[str, str | None]) -> None:
    assert parse_dpkg_db.extract_source_version(line) == expected


@parametrize_sync(
    args=["line", "expected", "raise_exception"],
    cases=[
        ["blabla", (None, "blabla"), False],
        ["key: val", ("key", "val"), False],
        ["Installed-Size: 128", ("Installed-Size", "128"), False],
        ["Installed-Size: 1kb", ("Installed-Size", "1000"), False],
        ["Installed-Size: 1 mb", ("Installed-Size", "1000000"), False],
        ["Installed-Size: 1 blblbl", ("Installed-Size", ""), True],
    ],
)
def test_handle_new_key_value(
    line: str,
    expected: tuple[str | None, str],
    raise_exception: bool,  # noqa: FBT001
) -> None:
    if raise_exception:
        with raises(ValueError, match="Unhandled size name:"):
            parse_dpkg_db.handle_new_key_value(line)
    else:
        assert parse_dpkg_db.handle_new_key_value(line) == expected


@parametrize_sync(
    args=["input_string", "expected_output"],
    cases=[
        ["libgmp10 (>= 2:6.2.1+dfsg1)", "libgmp10"],
        ["libgmp10", "libgmp10"],
        ["foo [i386]", "foo"],
        [
            "default-mta | mail-transport-agent",
            "default-mta | mail-transport-agent",
        ],
        ["kernel-headers-2.2.10 [!hurd-i386]", "kernel-headers-2.2.10"],
        ["  libgmp10   ", "libgmp10"],
        ["package-name<2.0> [!arch]", "package-name"],
    ],
)
def test_strip_version_specifier(input_string: str, expected_output: str) -> None:
    assert parse_dpkg_db.strip_version_specifier(input_string) == expected_output


@parametrize_sync(
    args=["test_data", "expected"],
    cases=[
        [
            "dependencies/debian/status/coreutils-relationships",
            {
                "coreutils": [
                    "libacl1",
                    "libattr1",
                    "libc6",
                    "libgmp10",
                    "libselinux1",
                ],
                "libacl1": ["libc6"],
                "acl": ["libc6"],
                "libc6": ["libgcc-s1"],
                "glibc": ["libgcc-s1"],
                "libgcc-s1": ["gcc-12-base", "libc6"],
                "gcc-12": ["gcc-12-base", "libc6"],
                "libattr1": ["libc6"],
                "attr": ["libc6"],
                "libgmp10": ["libc6"],
                "gmp": ["libc6"],
                "libselinux1": ["libc6", "libpcre2-8-0"],
                "libselinux": ["libc6", "libpcre2-8-0"],
                "libpcre2-8-0": ["libc6"],
                "pcre2": ["libc6"],
            },
        ],
        [
            "dependencies/debian/status/doc-examples",
            {
                "mutt": ["libc6", "default-mta", "mail-transport-agent"],
                "made-up-package-1": [
                    "kernel-headers-2.2.10",
                    "hurd-dev",
                    "gnumach-dev",
                ],
                "glibc": ["kernel-headers-2.2.10", "hurd-dev", "gnumach-dev"],
                "made-up-package-2": ["libluajit5.1-dev", "liblua5.1-dev"],
                "made-up-package-3": ["foo", "bar"],
                "made-up-package-4": ["made-up-package-5"],
            },
        ],
        [
            "dependencies/debian/status/libpam-runtime",
            {
                "libpam-runtime": [
                    "debconf1",
                    "debconf-2.0",
                    "debconf2",
                    "cdebconf",
                    "libpam-modules",
                ],
                "pam": [
                    "debconf1",
                    "debconf-2.0",
                    "debconf2",
                    "cdebconf",
                    "libpam-modules",
                ],
            },
        ],
    ],
)
def test_associate_relationships(
    test_data: str,
    expected: dict[str, list[str]],
) -> None:
    test_data_path = get_test_data_path(test_data)
    with Path(test_data_path).open(encoding="utf-8") as reader:
        _, relationships = parse_dpkg_db.parse_dpkg_db(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        reesult = convert_relationships(relationships)
        assert reesult == expected


def convert_relationships(
    relationships: list[Relationship],
) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for relationship in relationships:
        from_pkg: Package = relationship.from_
        to_pkg: Package = relationship.to_
        result.setdefault(to_pkg.name, []).append(from_pkg.name)
    return result
