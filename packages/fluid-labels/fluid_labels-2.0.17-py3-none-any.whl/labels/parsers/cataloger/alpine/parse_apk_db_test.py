from pathlib import Path
from typing import cast

from labels.model.file import LocationReadCloser
from labels.model.package import Digest, Language, Package, PackageType
from labels.model.release import Release
from labels.parsers.cataloger.alpine.package import ApkDBEntry, ApkFileRecord
from labels.parsers.cataloger.alpine.parse_apk_db import (
    ApkFileParsingContext,
    FileInfo,
    _build_lookup_table,
    _process_file_info,
    parse_apk_db,
    parse_package,
    process_checksum,
    process_line,
    strip_version_specifier,
    update_context_with_line,
)
from labels.parsers.cataloger.generic.parser import Environment
from labels.resolvers.directory import Directory
from labels.testing.utils.helpers import get_test_data_path
from labels.testing.utils.pytest_marks import parametrize_sync
from labels.utils.file import new_location


def test_extra_file_attributes() -> None:
    apk_file_records = [
        ApkFileRecord(path="/usr"),
        ApkFileRecord(path="/usr/lib"),
        ApkFileRecord(path="/usr/lib/jvm"),
        ApkFileRecord(path="/usr/lib/jvm/java-1.8-openjdk"),
        ApkFileRecord(path="/usr/lib/jvm/java-1.8-openjdk/bin"),
        ApkFileRecord(
            path="/usr/lib/jvm/java-1.8-openjdk/bin/policytool",
            owner_uid="0",
            owner_gid="0",
            permissions="755",
            digest=Digest(
                algorithm="'Q1'+base64(sha1)",
                value="Q1M0C9qfC/+kdRiOodeihG2GMRtkE=",
            ),
        ),
    ]
    test_data = get_test_data_path("dependencies/alpine/extra-file-attributes")
    test_data_location = new_location(test_data)
    if not test_data_location.access_path:
        return

    with Path(test_data_location.access_path).open(encoding="utf-8") as f:
        items = parse_apk_db(
            Directory(root=test_data, exclude=()),
            None,
            LocationReadCloser(
                location=test_data_location,
                read_closer=f,
            ),
        )
    if items:
        pkgs, _ = items
        assert cast(ApkDBEntry, pkgs[0].metadata).files == apk_file_records


@parametrize_sync(
    args=["test_data", "expected_package"],
    cases=[
        [
            "dependencies/alpine/single",
            Package(
                name="musl-utils",
                version="1.1.24-r2",
                licenses=["GPL-2.0-or-later", "MIT"],
                type=PackageType.ApkPkg,
                language=Language.UNKNOWN_LANGUAGE,
                locations=[],
                p_url="pkg:apk/musl-utils@1.1.24-r2?arch=x86_64&upstream=musl",
                metadata=ApkDBEntry(
                    package="musl-utils",
                    origin_package="musl",
                    version="1.1.24-r2",
                    description="the musl c library (libc) implementation",
                    maintainer="Timo Teräs <timo.teras@iki.fi>",
                    architecture="x86_64",
                    url="https://musl.libc.org/",
                    size="37944",
                    installed_size="151552",
                    dependencies=["scanelf", "so:libc.musl-x86_64.so.1"],
                    provides=[
                        "cmd:getconf",
                        "cmd:getent",
                        "cmd:iconv",
                        "cmd:ldconfig",
                        "cmd:ldd",
                    ],
                    checksum="Q1bTtF5526tETKfL+lnigzIDvm+2o=",
                    git_commit="4024cc3b29ad4c65544ad068b8f59172b5494306",
                    files=[
                        ApkFileRecord(path="/sbin"),
                        ApkFileRecord(
                            path="/sbin/ldconfig",
                            owner_uid="0",
                            owner_gid="0",
                            permissions="755",
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1Kja2+POZKxEkUOZqwSjC6kmaED4=",
                            ),
                        ),
                        ApkFileRecord(path="/usr"),
                        ApkFileRecord(path="/usr/bin"),
                        ApkFileRecord(
                            path="/usr/bin/iconv",
                            owner_uid="0",
                            owner_gid="0",
                            permissions="755",
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1CVmFbdY+Hv6/jAHl1gec2Kbx1EY=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/usr/bin/ldd",
                            owner_uid="0",
                            owner_gid="0",
                            permissions="755",
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1yFAhGggmL7ERgbIA7KQxyTzf3ks=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/usr/bin/getconf",
                            owner_uid="0",
                            owner_gid="0",
                            permissions="755",
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1dAdYK8M/INibRQF5B3Rw7cmNDDA=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/usr/bin/getent",
                            owner_uid="0",
                            owner_gid="0",
                            permissions="755",
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1eR2Dz/WylabgbWMTkd2+hGmEya4=",
                            ),
                        ),
                    ],
                ),
            ),
        ],
        [
            "dependencies/alpine/empty-deps-and-provides",
            Package(
                name="alpine-baselayout-data",
                version="3.4.0-r0",
                licenses=["GPL-2.0-only"],
                type=PackageType.ApkPkg,
                locations=[],
                language=Language.UNKNOWN_LANGUAGE,
                p_url="pkg:apk/alpine-baselayout-data@3.4.0-r0?arch=x86_64&"
                "upstream=alpine-baselayout",
                metadata=ApkDBEntry(
                    package="alpine-baselayout-data",
                    origin_package="alpine-baselayout",
                    maintainer="Natanael Copa <ncopa@alpinelinux.org>",
                    version="3.4.0-r0",
                    description="Alpine base dir structure and init scripts",
                    architecture="x86_64",
                    url=("https://git.alpinelinux.org/cgit/aports/tree/main/alpine-baselayout"),
                    size="11664",
                    installed_size="77824",
                    dependencies=[],
                    provides=[],
                    checksum="Q15ffjKT28lB7iSXjzpI/eDdYRCwM=",
                    git_commit="bd965a7ebf7fd8f07d7a0cc0d7375bf3e4eb9b24",
                    files=[
                        ApkFileRecord(path="/etc"),
                        ApkFileRecord(path="/etc/fstab"),
                        ApkFileRecord(path="/etc/group"),
                        ApkFileRecord(path="/etc/hostname"),
                        ApkFileRecord(path="/etc/hosts"),
                        ApkFileRecord(path="/etc/inittab"),
                        ApkFileRecord(path="/etc/modules"),
                        ApkFileRecord(
                            path="/etc/mtab",
                            owner_uid="0",
                            owner_gid="0",
                            permissions="0777",
                        ),
                        ApkFileRecord(path="/etc/nsswitch.conf"),
                        ApkFileRecord(path="/etc/passwd"),
                        ApkFileRecord(path="/etc/profile"),
                        ApkFileRecord(path="/etc/protocols"),
                        ApkFileRecord(path="/etc/services"),
                        ApkFileRecord(
                            path="/etc/shadow",
                            owner_uid="0",
                            owner_gid="148",
                            permissions="0640",
                        ),
                        ApkFileRecord(path="/etc/shells"),
                        ApkFileRecord(path="/etc/sysctl.conf"),
                    ],
                ),
            ),
        ],
        [
            "dependencies/alpine/base",
            Package(
                locations=[],
                language=Language.UNKNOWN_LANGUAGE,
                name="alpine-baselayout",
                version="3.2.0-r6",
                licenses=["GPL-2.0-only"],
                type=PackageType.ApkPkg,
                p_url="pkg:apk/alpine-baselayout@3.2.0-r6?arch=x86_64",
                metadata=ApkDBEntry(
                    package="alpine-baselayout",
                    origin_package="alpine-baselayout",
                    version="3.2.0-r6",
                    description="Alpine base dir structure and init scripts",
                    maintainer="Natanael Copa <ncopa@alpinelinux.org>",
                    architecture="x86_64",
                    url=("https://git.alpinelinux.org/cgit/aports/tree/main/alpine-baselayout"),
                    size="19917",
                    installed_size="409600",
                    dependencies=["/bin/sh", "so:libc.musl-x86_64.so.1"],
                    provides=["cmd:mkmntdirs"],
                    checksum="Q1myMNfd7u5v5UTgNHeq1e31qTjZU=",
                    git_commit="e1c51734fa96fa4bac92e9f14a474324c67916fc",
                    files=[
                        ApkFileRecord(path="/dev"),
                        ApkFileRecord(path="/dev/pts"),
                        ApkFileRecord(path="/dev/shm"),  # noqa: S108
                        ApkFileRecord(
                            path="/etc",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/fstab",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q11Q7hNe8QpDS531guqCdrXBzoA/o=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/group",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1oJ16xWudgKOrXIEquEDzlF2Lsm4=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/hostname",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q16nVwYVXP/tChvUPdukVD2ifXOmc=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/hosts",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1BD6zJKZTRWyqGnPi4tSfd3krsMU=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/inittab",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1TsthbhW7QzWRe1E/NKwTOuD4pHc=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/modules",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1toogjUipHGcMgECgPJX64SwUT1M=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/motd",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1XmduVVNURHQ27TvYp1Lr5TMtFcA=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/mtab",
                            owner_uid="0",
                            owner_gid="0",
                            permissions="777",
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1kiljhXXH1LlQroHsEJIkPZg2eiw=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/passwd",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1TchuuLUfur0izvfZQZxgN/LJhB8=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/profile",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1KpFb8kl5LvwXWlY3e58FNsjrI34=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/protocols",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q13FqXUnvuOpMDrH/6rehxuYAEE34=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/services",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1C6HJNgQvLWqt5VY+n7MZJ1rsDuY=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/shadow",
                            owner_uid="0",
                            owner_gid="42",
                            permissions="640",
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1ltrPIAW2zHeDiajsex2Bdmq3uqA=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/shells",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1ojm2YdpCJ6B/apGDaZ/Sdb2xJkA=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/sysctl.conf",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q14upz3tfnNxZkIEsUhWn7Xoiw96g=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/apk",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/conf.d",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/crontabs",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/crontabs/root",
                            owner_uid="0",
                            owner_gid="0",
                            permissions="600",
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1vfk1apUWI4yLJGhhNRd0kJixfvY=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/init.d",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/modprobe.d",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/modprobe.d/aliases.conf",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1WUbh6TBYNVK7e4Y+uUvLs/7viqk=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/modprobe.d/blacklist.conf",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1xxYGU6S6TLQvb7ervPrWWwAWqMg=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/modprobe.d/i386.conf",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1pnay/njn6ol9cCssL7KiZZ8etlc=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/modprobe.d/kms.conf",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1ynbLn3GYDpvajba/ldp1niayeog=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/modules-load.d",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/network",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/network/if-down.d",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/network/if-post-down.d",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/network/if-pre-up.d",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/network/if-up.d",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/opt",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/periodic",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/periodic/15min",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/periodic/daily",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/periodic/hourly",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/periodic/monthly",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/periodic/weekly",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/profile.d",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/etc/profile.d/color_prompt",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q10wL23GuSCVfumMRgakabUI6EsSk=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/profile.d/locale",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1R4bIEpnKxxOSrlnZy9AoawqZ5DU=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/etc/sysctl.d",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/home",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/lib",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/lib/firmware",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/lib/mdev",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/lib/modules-load.d",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/lib/sysctl.d",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/lib/sysctl.d/00-alpine.conf",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1HpElzW1xEgmKfERtTy7oommnq6c=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/media",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/media/cdrom",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/media/floppy",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/media/usb",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/mnt",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/opt",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/proc",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/root",
                            owner_uid="0",
                            owner_gid="0",
                            permissions="700",
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/run",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/sbin",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/sbin/mkmntdirs",
                            owner_uid="0",
                            owner_gid="0",
                            permissions="755",
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1YeuSmC7iDbEWrusPzA/zUQF6YSg=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/srv",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/sys",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/tmp",  # noqa: S108
                            owner_uid="0",
                            owner_gid="0",
                            permissions="1777",
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/usr",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/usr/lib",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/usr/lib/modules-load.d",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/usr/local",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/usr/local/bin",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/usr/local/lib",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/usr/local/share",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/usr/sbin",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/usr/share",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/usr/share/man",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/usr/share/misc",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/var",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/var/run",
                            owner_uid="0",
                            owner_gid="0",
                            permissions="777",
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q11/SNZz/8cK2dSKK+cJpVrZIuF4Q=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/var/cache",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/var/cache/misc",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/var/empty",
                            owner_uid="0",
                            owner_gid="0",
                            permissions="555",
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/var/lib",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/var/lib/misc",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/var/local",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/var/lock",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/var/lock/subsys",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/var/log",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/var/mail",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/var/opt",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/var/spool",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/var/spool/mail",
                            owner_uid="0",
                            owner_gid="0",
                            permissions="777",
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1dzbdazYZA2nTzSIG3YyNw7d4Juc=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/var/spool/cron",
                            owner_uid=None,
                            owner_gid=None,
                            permissions=None,
                            digest=None,
                        ),
                        ApkFileRecord(
                            path="/var/spool/cron/crontabs",
                            owner_uid="0",
                            owner_gid="0",
                            permissions="777",
                            digest=Digest(
                                algorithm="'Q1'+base64(sha1)",
                                value="Q1OFZt+ZMp7j0Gny0rqSKuWJyqYmA=",
                            ),
                        ),
                        ApkFileRecord(
                            path="/var/tmp",  # noqa: S108
                            owner_uid="0",
                            owner_gid="0",
                            permissions="1777",
                            digest=None,
                        ),
                    ],
                ),
            ),
        ],
    ],
)
def test_single_package_details(
    test_data: str,
    expected_package: Package,
) -> None:
    test_data_path = get_test_data_path(test_data)
    test_data_location = new_location(test_data_path)
    if not test_data_location.access_path:
        return

    expected_package.locations.append(test_data_location)

    with Path(test_data_location.access_path).open(encoding="utf-8") as f:
        items = parse_apk_db(
            Directory(root=test_data, exclude=()),
            None,
            LocationReadCloser(
                location=test_data_location,
                read_closer=f,
            ),
        )
    if items:
        pkgs, _ = items
        pkgs[0].health_metadata = None
        assert pkgs[0] == expected_package


def test_multiple_packages() -> None:
    test_data = get_test_data_path("dependencies/alpine/multiple")
    test_data_location = new_location(test_data)
    if not test_data_location.access_path:
        return
    packages = [
        Package(
            name="libc-utils",
            version="0.7.2-r0",
            licenses=["MIT", "MPL-2.0"],
            type=PackageType.ApkPkg,
            language=Language.UNKNOWN_LANGUAGE,
            p_url=(
                "pkg:apk/alpine/libc-utils@0.7.2-r0?arch=x86_64"
                "&distro=alpine-3.12&distro_id=alpine"
                "&distro_version_id=3.12&upstream=libc-dev"
            ),
            locations=[test_data_location],
            metadata=ApkDBEntry(
                package="libc-utils",
                origin_package="libc-dev",
                maintainer="Natanael Copa <ncopa@alpinelinux.org>",
                version="0.7.2-r0",
                architecture="x86_64",
                url="http://alpinelinux.org",
                description="Meta package to pull in correct libc",
                size="1175",
                installed_size="4096",
                dependencies=["musl-utils"],
                provides=[],
                files=[],
                checksum="Q1p78yvTLG094tHE1+dToJGbmYzQE=",
                git_commit="97b1c2842faa3bfa30f5811ffbf16d5ff9f1a479",
            ),
        ),
        Package(
            name="musl-utils",
            version="1.1.24-r2",
            licenses=["GPL-2.0-or-later", "MIT"],
            type=PackageType.ApkPkg,
            language=Language.UNKNOWN_LANGUAGE,
            p_url=(
                "pkg:apk/alpine/musl-utils@1.1.24-r2?arch=x86_64"
                "&distro=alpine-3.12&distro_id=alpine&distro_version_id=3.12"
                "&upstream=musl"
            ),
            locations=[test_data_location],
            metadata=ApkDBEntry(
                package="musl-utils",
                origin_package="musl",
                version="1.1.24-r2",
                description="the musl c library (libc) implementation",
                maintainer="Timo Teräs <timo.teras@iki.fi>",
                architecture="x86_64",
                url="https://musl.libc.org/",
                size="37944",
                installed_size="151552",
                dependencies=["scanelf", "so:libc.musl-x86_64.so.1"],
                provides=[
                    "cmd:getconf",
                    "cmd:getent",
                    "cmd:iconv",
                    "cmd:ldconfig",
                    "cmd:ldd",
                ],
                checksum="Q1bTtF5526tETKfL+lnigzIDvm+2o=",
                git_commit="4024cc3b29ad4c65544ad068b8f59172b5494306",
                files=[
                    ApkFileRecord(path="/sbin"),
                    ApkFileRecord(
                        path="/sbin/ldconfig",
                        owner_uid="0",
                        owner_gid="0",
                        permissions="755",
                        digest=Digest(
                            algorithm="'Q1'+base64(sha1)",
                            value="Q1Kja2+POZKxEkUOZqwSjC6kmaED4=",
                        ),
                    ),
                    ApkFileRecord(path="/usr"),
                    ApkFileRecord(path="/usr/bin"),
                    ApkFileRecord(
                        path="/usr/bin/iconv",
                        owner_uid="0",
                        owner_gid="0",
                        permissions="755",
                        digest=Digest(
                            algorithm="'Q1'+base64(sha1)",
                            value="Q1CVmFbdY+Hv6/jAHl1gec2Kbx1EY=",
                        ),
                    ),
                    ApkFileRecord(
                        path="/usr/bin/ldd",
                        owner_uid="0",
                        owner_gid="0",
                        permissions="755",
                        digest=Digest(
                            algorithm="'Q1'+base64(sha1)",
                            value="Q1yFAhGggmL7ERgbIA7KQxyTzf3ks=",
                        ),
                    ),
                    ApkFileRecord(
                        path="/usr/bin/getconf",
                        owner_uid="0",
                        owner_gid="0",
                        permissions="755",
                        digest=Digest(
                            algorithm="'Q1'+base64(sha1)",
                            value="Q1dAdYK8M/INibRQF5B3Rw7cmNDDA=",
                        ),
                    ),
                    ApkFileRecord(
                        path="/usr/bin/getent",
                        owner_uid="0",
                        owner_gid="0",
                        permissions="755",
                        digest=Digest(
                            algorithm="'Q1'+base64(sha1)",
                            value="Q1eR2Dz/WylabgbWMTkd2+hGmEya4=",
                        ),
                    ),
                ],
            ),
        ),
    ]
    with Path(test_data_location.access_path).open(encoding="utf-8") as f:
        items = parse_apk_db(
            Directory(root=test_data, exclude=()),
            Environment(linux_release=Release(id_="alpine", version_id="3.12")),
            LocationReadCloser(
                location=test_data_location,
                read_closer=f,
            ),
        )
    if items:
        pkgs, _ = items
        for pkg in pkgs:
            pkg.health_metadata = None
        assert pkgs == packages


@parametrize_sync(
    args=["value", "expected"],
    cases=[
        [
            "38870ede8700535d7382ff66a46fcc2f",
            Digest(algorithm="md5", value="38870ede8700535d7382ff66a46fcc2f"),
        ],
        [
            "Q1Kja2+POZKxEkUOZqwSjC6kmaED4=",
            Digest(
                algorithm="'Q1'+base64(sha1)",
                value="Q1Kja2+POZKxEkUOZqwSjC6kmaED4=",
            ),
        ],
    ],
)
def test_process_checksum(value: str, expected: Digest) -> None:
    assert process_checksum(value) == expected


def test_parse_apk_db_exted_pkg_names() -> None:
    test_data = get_test_data_path("dependencies/alpine/very-large-entries")
    test_data_location = new_location(test_data)
    if not test_data_location.access_path:
        return
    expected_pkgs = [
        "ca-certificates-bundle",
        "glibc-locale-posix",
        "wolfi-baselayout",
        "glibc",
        "libcrypto3",
        "libssl3",
        "zlib",
        "apk-tools",
        "ncurses-terminfo-base",
        "ncurses",
        "bash",
        "libcap",
        "bubblewrap",
        "busybox",
        "libbrotlicommon1",
        "libbrotlidec1",
        "libnghttp2-14",
        "libcurl4",
        "curl",
        "expat",
        "libpcre2-8-0",
        "git",
        "binutils",
        "libstdc++-dev",
        "libgcc",
        "libstdc++",
        "gmp",
        "isl",
        "mpfr",
        "mpc",
        "gcc",
        "linux-headers",
        "glibc-dev",
        "make",
        "pkgconf",
        "build-base",
        "go",
        "tree",
        "sdk",
    ]

    with Path(test_data_location.access_path).open(encoding="utf-8") as f:
        items = parse_apk_db(
            Directory(root=test_data, exclude=()),
            None,
            LocationReadCloser(
                location=test_data_location,
                read_closer=f,
            ),
        )
    if items:
        pkgs, _ = items
        pkg_result_names = [pkg.name for pkg in pkgs]
        assert pkg_result_names == expected_pkgs


@parametrize_sync(
    args=["version", "expected"],
    cases=[
        ["", ""],
        ["cmd:foo", "cmd:foo"],
        ["cmd:scanelf=1.3.4-r0", "cmd:scanelf"],
        ["cmd:scanelf>=1.3.4-r0", "cmd:scanelf"],
        ["cmd:scanelf<1.3.4-r0", "cmd:scanelf"],
    ],
)
def test_strip_version_specifier(version: str, expected: str) -> None:
    assert strip_version_specifier(version) == expected


@parametrize_sync(
    args=["info", "expected"],
    cases=[
        ["0:0:755", {"uid": "0", "gid": "0", "perms": "755"}],
        ["1000:1000:644", {"uid": "1000", "gid": "1000", "perms": "644"}],
        ["root:wheel:777", {"uid": "root", "gid": "wheel", "perms": "777"}],
        ["invalid", None],
        ["1:1", None],
        ["1:1:644:extra", {"uid": "1", "gid": "1", "perms": "644"}],
        ["", None],
    ],
)
def test_process_file_info(info: str, expected: FileInfo | None) -> None:
    result = _process_file_info(info)
    assert result == expected


def test_parse_package_valid() -> None:
    package_data = """P:musl-utils
V:1.1.24-r2
A:x86_64
L:MIT GPL-2.0-or-later
T:the musl c library (libc) implementation
D:scanelf so:libc.musl-x86_64.so.1
p:cmd:getconf cmd:getent cmd:iconv cmd:ldconfig cmd:ldd
m:Timo Teräs <timo.teras@iki.fi>
U:https://musl.libc.org/
I:151552
S:37944
C:Q1bTtF5526tETKfL+lnigzIDvm+2o=
o:musl
c:4024cc3b29ad4c65544ad068b8f59172b5494306"""

    result = parse_package(package_data)
    assert result is not None
    assert result.apk_db_entry.package == "musl-utils"
    assert result.apk_db_entry.version == "1.1.24-r2"
    assert result.apk_db_entry.architecture == "x86_64"
    assert result.apk_db_entry.maintainer == "Timo Teräs <timo.teras@iki.fi>"
    assert result.apk_db_entry.url == "https://musl.libc.org/"
    assert result.apk_db_entry.description == "the musl c library (libc) implementation"
    assert result.apk_db_entry.size == "37944"
    assert result.apk_db_entry.installed_size == "151552"
    assert result.apk_db_entry.origin_package == "musl"
    assert result.apk_db_entry.dependencies == ["scanelf", "so:libc.musl-x86_64.so.1"]
    assert result.apk_db_entry.provides == [
        "cmd:getconf",
        "cmd:getent",
        "cmd:iconv",
        "cmd:ldconfig",
        "cmd:ldd",
    ]
    assert result.license == "MIT GPL-2.0-or-later"


def test_parse_package_missing_required() -> None:
    package_data = """A:x86_64
L:MIT
T:test package
D:foo
m:Test User <test@example.com>
U:https://example.com/
I:1234
S:5678
C:Q1234567890="""

    result = parse_package(package_data)
    assert result is None


def test_parse_package_empty_string() -> None:
    result = parse_package("")
    assert result is None


def test_parse_package_file_metadata() -> None:
    package_data = """P:test-pkg
V:1.0
F:/usr
M:0:0:755
R:file.txt
a:0:0:644
Z:Q1abc123="""

    result = parse_package(package_data)
    assert result is not None
    assert len(result.apk_db_entry.files) == 2

    assert result.apk_db_entry.files[0].path == "/usr"
    assert result.apk_db_entry.files[0].owner_uid == "0"
    assert result.apk_db_entry.files[0].owner_gid == "0"
    assert result.apk_db_entry.files[0].permissions == "755"

    assert result.apk_db_entry.files[1].path == "/usr/file.txt"
    assert result.apk_db_entry.files[1].owner_uid == "0"
    assert result.apk_db_entry.files[1].owner_gid == "0"
    assert result.apk_db_entry.files[1].permissions == "644"
    assert result.apk_db_entry.files[1].digest is not None
    assert result.apk_db_entry.files[1].digest.value == "Q1abc123="


def test_parse_package_with_spaces() -> None:
    package_data = """P:test-pkg
V:1.0.0
T:This is a description with spaces
m:Test User <test@example.com>
L:Apache 2.0"""

    result = parse_package(package_data)
    assert result is not None
    assert result.apk_db_entry.description == "This is a description with spaces"
    assert result.license == "Apache 2.0"


@parametrize_sync(
    args=["key", "initial_data", "line", "expected_data"],
    cases=[
        [
            "T",
            {"T": "Primera línea"},
            "  Segunda línea",
            {"T": "Primera línea\nSegunda línea"},
        ],
        [
            "L",
            {"L": "Apache"},
            "  2.0",
            {"L": "Apache\n2.0"},
        ],
        [
            "D",
            {"D": "dep1"},
            "  dep2",
            {"D": "dep1\ndep2"},
        ],
    ],
)
def test_process_line_continuation(
    key: str,
    initial_data: dict[str, str],
    line: str,
    expected_data: dict[str, str],
) -> None:
    ctx = ApkFileParsingContext(
        files=[],
        index_of_latest_directory=-1,
        index_of_latest_regular_file=-1,
    )

    result_key = process_line(line, key, initial_data, ctx)

    assert result_key == key
    assert initial_data == expected_data


def test_invalid_file_info() -> None:
    ctx = ApkFileParsingContext(
        files=[
            ApkFileRecord(path="/usr/bin"),
        ],
        index_of_latest_directory=0,
        index_of_latest_regular_file=-1,
    )

    test_cases = [
        ("M", "invalid"),
        ("M", "1"),
        ("M", ""),
        ("M", "1:2"),
        ("a", "invalid"),
        ("a", "1"),
        ("a", ""),
        ("a", "1:2"),
    ]

    for key, invalid_value in test_cases:
        if key == "a":
            ctx.index_of_latest_regular_file = 0
        else:
            ctx.index_of_latest_directory = 0

        initial_file = ApkFileRecord(path="/usr/bin")
        ctx.files = [initial_file]

        update_context_with_line(key, invalid_value, ctx)

        assert ctx.files[0].owner_uid is None
        assert ctx.files[0].owner_gid is None
        assert ctx.files[0].permissions is None


def test_regular_file_without_directory() -> None:
    ctx = ApkFileParsingContext(
        files=[],
        index_of_latest_directory=-1,
        index_of_latest_regular_file=-1,
    )

    test_cases = [
        ("bin/ls", "/bin/ls"),
        ("etc/config", "/etc/config"),
        ("file.txt", "/file.txt"),
        ("usr/local/bin/app", "/usr/local/bin/app"),
    ]

    for value, expected_path in test_cases:
        update_context_with_line("R", value, ctx)

        assert len(ctx.files) == 1
        assert ctx.files[0].path == expected_path
        assert ctx.index_of_latest_regular_file == 0

        ctx.files = []
        ctx.index_of_latest_regular_file = -1


def test_build_lookup_table_with_duplicates() -> None:
    pkg1 = Package(
        name="python",
        version="3.9.0",
        type=PackageType.ApkPkg,
        language=Language.UNKNOWN_LANGUAGE,
        licenses=["MIT"],
        locations=[],
        p_url="pkg:apk/python@3.9.0",
        metadata=ApkDBEntry(
            package="python",
            version="3.9.0",
            provides=["python3"],
            files=[],
            origin_package="python",
            maintainer="Python Maintainer <maintainer@python.org>",
            architecture="x86_64",
            url="https://python.org",
            description="Python programming language",
            size="1000",
            installed_size="5000",
            dependencies=[],
            checksum="Q1abc123",
            git_commit="1234567890abcdef",
        ),
    )

    pkg2 = Package(
        name="python",
        version="3.10.0",
        type=PackageType.ApkPkg,
        language=Language.UNKNOWN_LANGUAGE,
        licenses=["MIT"],
        locations=[],
        p_url="pkg:apk/python@3.10.0",
        metadata=ApkDBEntry(
            package="python",
            version="3.10.0",
            provides=["python3", "python310"],
            files=[],
            origin_package="python",
            maintainer="Python Maintainer <maintainer@python.org>",
            architecture="x86_64",
            url="https://python.org",
            description="Python programming language",
            size="1200",
            installed_size="6000",
            dependencies=[],
            checksum="Q1def456",
            git_commit="0987654321fedcba",
        ),
    )

    pkg3 = Package(
        name="other-pkg",
        version="1.0.0",
        type=PackageType.ApkPkg,
        language=Language.UNKNOWN_LANGUAGE,
        licenses=["Apache-2.0"],
        locations=[],
        p_url="pkg:apk/other-pkg@1.0.0",
        metadata=ApkDBEntry(
            package="other-pkg",
            version="1.0.0",
            provides=["python3"],
            files=[],
            origin_package="other-pkg",
            maintainer="Other Maintainer <other@example.com>",
            architecture="x86_64",
            url="https://example.com",
            description="Other package",
            size="500",
            installed_size="2000",
            dependencies=[],
            checksum="Q1ghi789",
            git_commit="abcdef1234567890",
        ),
    )

    packages = [pkg1, pkg2, pkg3]

    lookup = _build_lookup_table(packages)

    assert len(lookup["python"]) == 2
    assert pkg1 in lookup["python"]
    assert pkg2 in lookup["python"]

    assert len(lookup["python3"]) == 3
    assert pkg1 in lookup["python3"]
    assert pkg2 in lookup["python3"]
    assert pkg3 in lookup["python3"]

    assert len(lookup["python310"]) == 1
    assert pkg2 in lookup["python310"]

    assert len(lookup["other-pkg"]) == 1
    assert pkg3 in lookup["other-pkg"]


def test_build_lookup_table_provides_with_versions() -> None:
    pkg1 = Package(
        name="python3",
        version="3.9.0",
        type=PackageType.ApkPkg,
        language=Language.UNKNOWN_LANGUAGE,
        licenses=["MIT"],
        locations=[],
        p_url="pkg:apk/python3@3.9.0",
        metadata=ApkDBEntry(
            package="python3",
            version="3.9.0",
            provides=[
                "python-base=3.9.0",
                "python3-base",
                "python-utils>=3.9.0",
            ],
            files=[],
            origin_package="python3",
            maintainer="Python Maintainer <maintainer@python.org>",
            architecture="x86_64",
            url="https://python.org",
            description="Python programming language",
            size="1000",
            installed_size="5000",
            dependencies=[],
            checksum="Q1abc123",
            git_commit="1234567890abcdef",
        ),
    )

    pkg2 = Package(
        name="python-dev",
        version="3.9.0",
        type=PackageType.ApkPkg,
        language=Language.UNKNOWN_LANGUAGE,
        licenses=["MIT"],
        locations=[],
        p_url="pkg:apk/python-dev@3.9.0",
        metadata=ApkDBEntry(
            package="python-dev",
            version="3.9.0",
            provides=[
                "cmd:python3-config",
                "so:libpython3.9.so.1.0",
            ],
            files=[],
            origin_package="python3",
            maintainer="Python Maintainer <maintainer@python.org>",
            architecture="x86_64",
            url="https://python.org",
            description="Python development files",
            size="500",
            installed_size="2000",
            dependencies=[],
            checksum="Q1def456",
            git_commit="0987654321fedcba",
        ),
    )

    packages = [pkg1, pkg2]
    lookup = _build_lookup_table(packages)

    assert len(lookup["python-base"]) == 1
    assert pkg1 in lookup["python-base"]

    assert len(lookup["python-utils"]) == 1
    assert pkg1 in lookup["python-utils"]

    assert len(lookup["python3-base"]) == 1
    assert pkg1 in lookup["python3-base"]

    assert len(lookup["cmd:python3-config"]) == 1
    assert pkg2 in lookup["cmd:python3-config"]

    assert len(lookup["so:libpython3.9.so.1.0"]) == 1
    assert pkg2 in lookup["so:libpython3.9.so.1.0"]

    assert len(lookup["python3"]) == 1
    assert pkg1 in lookup["python3"]

    assert len(lookup["python-dev"]) == 1
    assert pkg2 in lookup["python-dev"]
