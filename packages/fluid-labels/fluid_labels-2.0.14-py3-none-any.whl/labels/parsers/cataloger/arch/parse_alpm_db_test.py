import gzip
import os
from datetime import UTC, datetime
from io import BytesIO, StringIO, TextIOWrapper
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.package import Digest, Language, Package, PackageType
from labels.model.release import Release
from labels.model.resolver import FileReader
from labels.parsers.cataloger.arch.package import AlpmDBEntry, AlpmFileRecord
from labels.parsers.cataloger.arch.parse_alpm import (
    _parse_files,
    parse_alpm_db,
    parse_alpm_db_entry,
    parse_backup,
    parse_key_value_pair,
    parse_mtree,
)
from labels.parsers.cataloger.generic.parser import Environment
from labels.resolvers.directory import Directory
from labels.testing.utils.helpers import get_test_data_path
from labels.testing.utils.pytest_marks import parametrize_sync
from labels.utils.file import new_location


def _get_location_for_path(path: str, test_data_path: str) -> list[Location]:
    if "mtree" in path:
        return [
            Location(
                scope=Scope.PROD,
                coordinates=Coordinates(real_path=os.path.join(test_data_path, "mtree")),
                access_path=os.path.join(test_data_path, "mtree"),
                annotations={},
                dependency_type=DependencyType.UNKNOWN,
                reachable_cves=[],
            ),
        ]
    if "files" in path:
        return [
            Location(
                scope=Scope.PROD,
                coordinates=Coordinates(real_path=os.path.join(test_data_path, "files")),
                access_path=os.path.join(test_data_path, "files"),
                annotations={},
                dependency_type=DependencyType.UNKNOWN,
                reachable_cves=[],
            ),
        ]
    return []


@parametrize_sync(
    args=["test_data", "expected"],
    cases=[
        [
            "dependencies/arch/files",
            AlpmDBEntry(
                backup=[
                    AlpmFileRecord(
                        path="/etc/pacman.conf",
                        digests=[
                            Digest(
                                algorithm="md5",
                                value="de541390e52468165b96511c4665bff4",
                            ),
                        ],
                    ),
                    AlpmFileRecord(
                        path="/etc/makepkg.conf",
                        digests=[
                            Digest(
                                algorithm="md5",
                                value="79fce043df7dfc676ae5ecb903762d8b",
                            ),
                        ],
                    ),
                ],
                files=[
                    AlpmFileRecord(path="/etc/"),
                    AlpmFileRecord(path="/etc/makepkg.conf"),
                    AlpmFileRecord(path="/etc/pacman.conf"),
                    AlpmFileRecord(path="/usr/"),
                    AlpmFileRecord(path="/usr/bin/"),
                    AlpmFileRecord(path="/usr/bin/makepkg"),
                    AlpmFileRecord(path="/usr/bin/makepkg-template"),
                    AlpmFileRecord(path="/usr/bin/pacman"),
                    AlpmFileRecord(path="/usr/bin/pacman-conf"),
                    AlpmFileRecord(path="/var/"),
                    AlpmFileRecord(path="/var/cache/"),
                    AlpmFileRecord(path="/var/cache/pacman/"),
                    AlpmFileRecord(path="/var/cache/pacman/pkg/"),
                    AlpmFileRecord(path="/var/lib/"),
                    AlpmFileRecord(path="/var/lib/pacman/"),
                ],
            ),
        ],
    ],
)
def test_database_parser(
    test_data: str,
    expected: AlpmDBEntry,
) -> None:
    test_data_path = get_test_data_path(test_data)
    with Path(test_data_path).open(encoding="utf-8") as reader:
        entry = parse_alpm_db_entry(
            reader,
        )

    assert entry == expected


def test_mtree_parse() -> None:
    expected = [
        AlpmFileRecord(
            path="/etc",
            type="dir",
            time=datetime.fromisoformat("2022-04-10T12:59:52Z"),
            digests=[],
        ),
        AlpmFileRecord(
            path="/etc/pacman.d",
            type="dir",
            time=datetime.fromisoformat("2022-04-10T12:59:52Z"),
            digests=[],
        ),
        AlpmFileRecord(
            path="/etc/pacman.d/mirrorlist",
            size="44683",
            time=datetime.fromisoformat("2022-04-10T12:59:52Z"),
            digests=[
                Digest(
                    algorithm="md5",
                    value="81c39827e38c759d7e847f05db62c233",
                ),
                Digest(
                    algorithm="sha256",
                    value=("fc135ab26f2a227b9599b66a2f1ba325c445acb914d60e7ecf6e5997a87abe1e"),
                ),
            ],
        ),
    ]
    test_data_path = get_test_data_path("dependencies/arch")
    resolver = Directory(root=test_data_path, exclude=())
    mtree_location = resolver.files_by_path("mtree")[0]
    reader = resolver.file_contents_by_location(
        mtree_location,
        function_reader=cast(FileReader, gzip.open),
        mode="rt",
    )
    if reader:
        entries = parse_mtree(reader)
        assert entries == expected


def test_mtree_parse_without_equals() -> None:
    mtree_data = StringIO(
        ". /etc time=1234567890 type dir mode 755\n"
        ". /usr time=1234567890 type dir\n"
        ". /var time=1234567890\n",
    )
    result = parse_mtree(mtree_data)
    assert len(result) > 0
    for record in result:
        assert record.type is None
        assert record.size is None


def test_empty_entry_returns_none() -> None:
    empty_data = StringIO("")

    result = parse_alpm_db_entry(empty_data)
    assert result is None


def test_invalid_key_value_pair_returns_empty_dict() -> None:
    invalid_line = "invalid_line_without_newline"
    result = parse_key_value_pair(invalid_line)
    assert result == {}


def test_numeric_field_parsing() -> None:
    valid_reason = "%REASON\n123"
    result = parse_key_value_pair(valid_reason)
    assert result == {"reason": 123}

    valid_size = "%SIZE\n456"
    result = parse_key_value_pair(valid_size)
    assert result == {"size": 456}

    invalid_reason = "%REASON\nnot_a_number"
    result = parse_key_value_pair(invalid_reason)
    assert result == {}

    invalid_size = "%SIZE\nnot_a_number"
    result = parse_key_value_pair(invalid_size)
    assert result == {}

    normal_field = "%NAME\ntest_package"
    result = parse_key_value_pair(normal_field)
    assert result == {"name": "test_package"}


def test_parse_backup_ignores_files() -> None:
    input_value = "set\tmd5hash1\n.normalfile\tmd5hash2\n.PKGINFO\tmd5hash3"

    result = parse_backup(input_value)

    paths = [item["path"] for item in result]
    assert "/set" not in paths
    assert "/.PKGINFO" not in paths

    assert "/.normalfile" in paths


def test_parse_files_ignores_files() -> None:
    input_value = "set\n.normalfile\n.PKGINFO"

    result = _parse_files(input_value)

    paths = [item["path"] for item in result]
    assert "/set" not in paths
    assert "/.PKGINFO" not in paths

    assert "/.normalfile" in paths


def test_parse_alpm_db_with_real_files() -> None:
    test_data_path = get_test_data_path(
        "dependencies/arch/gmp-fixture/var/lib/pacman/local/gmp-6.2.1-2",
    )

    test_resolver = Directory(root=test_data_path, exclude=())
    test_env = Environment(linux_release=Release(id_="arch", version_id="rolling"))

    desc_path = os.path.join(test_data_path, "desc")
    with Path(desc_path).open("r", encoding="utf-8") as f:
        reader = LocationReadCloser(
            read_closer=f,
            location=new_location(desc_path),
        )

        expected_metadata = AlpmDBEntry(
            licenses="LGPL3\nGPL",
            base_package="gmp",
            package="gmp",
            version="6.2.1-2",
            description="A free library for arbitrary precision arithmetic",
            architecture="x86_64",
            size=1044438,
            packager="Antonio Rojas <arojas@archlinux.org>",
            url="https://gmplib.org/",
            validation="pgp",
            reason=1,
            files=[
                AlpmFileRecord(
                    path="/usr",
                    type="dir",
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size=None,
                    link=None,
                    digests=[],
                ),
                AlpmFileRecord(
                    path="/usr/include",
                    type="dir",
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size=None,
                    link=None,
                    digests=[],
                ),
                AlpmFileRecord(
                    path="/usr/include/gmp.h",
                    type=None,
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size="84140",
                    link=None,
                    digests=[
                        Digest(algorithm="md5", value="76595f70565c72550eb520809bf86856"),
                        Digest(
                            algorithm="sha256",
                            value="91a614b9202453153fe3b7512d15e89659108b93ce8841c8e13789eb85da9e3a",
                        ),
                    ],
                ),
                AlpmFileRecord(
                    path="/usr/include/gmpxx.h",
                    type=None,
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size="129113",
                    link=None,
                    digests=[
                        Digest(algorithm="md5", value="ea3d21de4bcf7c696799c5c55dd3655b"),
                        Digest(
                            algorithm="sha256",
                            value="0011ae411a0bc1030e07d968b32fdc1343f5ac2a17b7d28f493e7976dde2ac82",
                        ),
                    ],
                ),
                AlpmFileRecord(
                    path="/usr/lib",
                    type="dir",
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size=None,
                    link=None,
                    digests=[],
                ),
                AlpmFileRecord(
                    path="/usr/lib/libgmp.so",
                    type="link",
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size=None,
                    link="libgmp.so.10.4.1",
                    digests=[],
                ),
                AlpmFileRecord(
                    path="/usr/lib/libgmp.so.10",
                    type="link",
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size=None,
                    link="libgmp.so.10.4.1",
                    digests=[],
                ),
                AlpmFileRecord(
                    path="/usr/lib/libgmp.so.10.4.1",
                    type=None,
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size="663224",
                    link=None,
                    digests=[
                        Digest(algorithm="md5", value="d6d03eadacdd9048d5b2adf577e9d722"),
                        Digest(
                            algorithm="sha256",
                            value="39898bd3d8d6785222432fa8b8aef7ce3b7e5bbfc66a52b7c0da09bed4adbe6a",
                        ),
                    ],
                ),
                AlpmFileRecord(
                    path="/usr/lib/libgmpxx.so",
                    type="link",
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size=None,
                    link="libgmpxx.so.4.6.1",
                    digests=[],
                ),
                AlpmFileRecord(
                    path="/usr/lib/libgmpxx.so.4",
                    type="link",
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size=None,
                    link="libgmpxx.so.4.6.1",
                    digests=[],
                ),
                AlpmFileRecord(
                    path="/usr/lib/libgmpxx.so.4.6.1",
                    type=None,
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size="30680",
                    link=None,
                    digests=[
                        Digest(algorithm="md5", value="dd5f0c4d635fa599fa7f4339c0e8814d"),
                        Digest(
                            algorithm="sha256",
                            value="0ef67cbde4841f58d2e4b41f59425eb87c9eeaf4e649c060b326342c53bedbec",
                        ),
                    ],
                ),
                AlpmFileRecord(
                    path="/usr/lib/pkgconfig",
                    type="dir",
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size=None,
                    link=None,
                    digests=[],
                ),
                AlpmFileRecord(
                    path="/usr/lib/pkgconfig/gmp.pc",
                    type=None,
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size="245",
                    link=None,
                    digests=[
                        Digest(algorithm="md5", value="a91a9f1b66218cb77b9cd2cdf341756d"),
                        Digest(
                            algorithm="sha256",
                            value="4e9de547a48c4e443781e9fa702a1ec5a23ee28b4bc520306cff2541a855be37",
                        ),
                    ],
                ),
                AlpmFileRecord(
                    path="/usr/lib/pkgconfig/gmpxx.pc",
                    type=None,
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size="280",
                    link=None,
                    digests=[
                        Digest(algorithm="md5", value="8c0f54e987934352177a6a30a811b001"),
                        Digest(
                            algorithm="sha256",
                            value="fc5dbfbe75977057ba50953d94b9daecf696c9fdfe5b94692b832b44ecca871b",
                        ),
                    ],
                ),
                AlpmFileRecord(
                    path="/usr/share",
                    type="dir",
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size=None,
                    link=None,
                    digests=[],
                ),
                AlpmFileRecord(
                    path="/usr/share/info",
                    type="dir",
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size=None,
                    link=None,
                    digests=[],
                ),
                AlpmFileRecord(
                    path="/usr/share/info/gmp.info-1.gz",
                    type=None,
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size="85892",
                    link=None,
                    digests=[
                        Digest(algorithm="md5", value="63304d4d2f0247fb8a999fae66a81c19"),
                        Digest(
                            algorithm="sha256",
                            value="86288c1531a2789db5da8b9838b5cde4db07bda230ae11eba23a1f33698bd14e",
                        ),
                    ],
                ),
                AlpmFileRecord(
                    path="/usr/share/info/gmp.info-2.gz",
                    type=None,
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size="48484",
                    link=None,
                    digests=[
                        Digest(algorithm="md5", value="4bb0dadec416d305232cac6eae712ff7"),
                        Digest(
                            algorithm="sha256",
                            value="b7443c1b529588d98a074266087f79b595657ac7274191c34b10a9ceedfa950e",
                        ),
                    ],
                ),
                AlpmFileRecord(
                    path="/usr/share/info/gmp.info.gz",
                    type=None,
                    uid=None,
                    gid=None,
                    time=datetime(2022, 5, 21, 8, 20, 58, tzinfo=UTC),
                    size="2380",
                    link=None,
                    digests=[
                        Digest(algorithm="md5", value="cf6880fb0d862ee1da0d13c3831b5720"),
                        Digest(
                            algorithm="sha256",
                            value="a13c8eecda3f3e5ad1e09773e47a9686f07d9d494eaddf326f3696bbef1548fd",
                        ),
                    ],
                ),
            ],
            backup=[],
        )

        expected_package = Package(
            name="gmp",
            version="6.2.1-2",
            locations=[reader.location],
            licenses=["LGPL-3.0-only"],
            type=PackageType.AlpmPkg,
            metadata=expected_metadata,
            p_url="pkg:alpm/gmp@6.2.1-2?arch=x86_64&distro=arch-rolling&upstream=gmp",
            language=Language.UNKNOWN_LANGUAGE,
        )

        packages, relationships = parse_alpm_db(test_resolver, test_env, reader)

        assert len(packages) == 1
        assert packages[0] == expected_package
        assert len(relationships) == 0


def test_parse_alpm_db_without_data_or_coordinates() -> None:
    test_resolver = Directory(root="./", exclude=())
    test_env = Environment(linux_release=Release(id_="arch", version_id="rolling"))

    empty_reader = LocationReadCloser(
        read_closer=TextIOWrapper(BytesIO(b"")),
        location=new_location("./dummy/desc"),
    )
    packages, relationships = parse_alpm_db(test_resolver, test_env, empty_reader)
    assert len(packages) == 0
    assert len(relationships) == 0

    reader_without_coordinates = LocationReadCloser(
        read_closer=TextIOWrapper(BytesIO(b"test data")),
        location=Location(
            scope=Scope.PROD,
            coordinates=None,
            access_path="./dummy/desc",
            annotations={},
            dependency_type=DependencyType.UNKNOWN,
            reachable_cves=[],
        ),
    )
    packages, relationships = parse_alpm_db(test_resolver, test_env, reader_without_coordinates)
    assert len(packages) == 0
    assert len(relationships) == 0


def test_parse_alpm_db_without_mtree() -> None:
    test_data_path = get_test_data_path(
        "dependencies/arch/gmp-fixture/var/lib/pacman/local/gmp-6.2.1-2",
    )

    test_resolver = MagicMock()
    test_resolver.files_by_path.return_value = []
    test_resolver.file_contents_by_location.return_value = None
    test_env = Environment(linux_release=Release(id_="arch", version_id="rolling"))

    desc_path = os.path.join(test_data_path, "desc")
    with Path(desc_path).open("r", encoding="utf-8") as f:
        reader = LocationReadCloser(
            read_closer=f,
            location=new_location(desc_path),
        )

        expected_metadata = AlpmDBEntry(
            licenses="LGPL3\nGPL",
            base_package="gmp",
            package="gmp",
            version="6.2.1-2",
            description="A free library for arbitrary precision arithmetic",
            architecture="x86_64",
            size=1044438,
            packager="Antonio Rojas <arojas@archlinux.org>",
            url="https://gmplib.org/",
            validation="pgp",
            reason=1,
            files=[],
            backup=[],
        )

        expected_package = Package(
            name="gmp",
            version="6.2.1-2",
            locations=[reader.location],
            licenses=["LGPL-3.0-only"],
            type=PackageType.AlpmPkg,
            metadata=expected_metadata,
            p_url="pkg:alpm/gmp@6.2.1-2?arch=x86_64&distro=arch-rolling&upstream=gmp",
            language=Language.UNKNOWN_LANGUAGE,
        )

        packages, relationships = parse_alpm_db(test_resolver, test_env, reader)

        assert len(packages) == 1
        assert packages[0] == expected_package
        assert len(relationships) == 0


def test_parse_alpm_db_without_files_reader() -> None:
    test_data_path = get_test_data_path(
        "dependencies/arch/gmp-fixture/var/lib/pacman/local/gmp-6.2.1-2",
    )

    test_resolver = MagicMock()
    test_resolver.files_by_path.side_effect = lambda path: _get_location_for_path(
        path,
        test_data_path,
    )
    test_resolver.file_contents_by_location.return_value = None
    test_env = Environment(linux_release=Release(id_="arch", version_id="rolling"))

    desc_path = os.path.join(test_data_path, "desc")
    with Path(desc_path).open("r", encoding="utf-8") as f:
        reader = LocationReadCloser(
            read_closer=f,
            location=new_location(desc_path),
        )

        expected_metadata = AlpmDBEntry(
            licenses="LGPL3\nGPL",
            base_package="gmp",
            package="gmp",
            version="6.2.1-2",
            description="A free library for arbitrary precision arithmetic",
            architecture="x86_64",
            size=1044438,
            packager="Antonio Rojas <arojas@archlinux.org>",
            url="https://gmplib.org/",
            validation="pgp",
            reason=1,
            files=[],
            backup=[],
        )

        expected_package = Package(
            name="gmp",
            version="6.2.1-2",
            locations=[reader.location],
            licenses=["LGPL-3.0-only"],
            type=PackageType.AlpmPkg,
            metadata=expected_metadata,
            p_url="pkg:alpm/gmp@6.2.1-2?arch=x86_64&distro=arch-rolling&upstream=gmp",
            language=Language.UNKNOWN_LANGUAGE,
        )

        packages, relationships = parse_alpm_db(test_resolver, test_env, reader)

        assert len(packages) == 1
        assert packages[0] == expected_package
        assert len(relationships) == 0


def test_parse_alpm_db_with_invalid_files_metadata() -> None:
    test_data_path = get_test_data_path(
        "dependencies/arch/gmp-fixture/var/lib/pacman/local/gmp-6.2.1-2",
    )

    test_resolver = MagicMock()
    test_resolver.files_by_path.side_effect = lambda path: _get_location_for_path(
        path,
        test_data_path,
    )
    test_resolver.file_contents_by_location.return_value = TextIOWrapper(BytesIO(b""))
    test_env = Environment(linux_release=Release(id_="arch", version_id="rolling"))

    desc_path = os.path.join(test_data_path, "desc")
    with Path(desc_path).open("r", encoding="utf-8") as f:
        reader = LocationReadCloser(
            read_closer=f,
            location=new_location(desc_path),
        )

        expected_metadata = AlpmDBEntry(
            licenses="LGPL3\nGPL",
            base_package="gmp",
            package="gmp",
            version="6.2.1-2",
            description="A free library for arbitrary precision arithmetic",
            architecture="x86_64",
            size=1044438,
            packager="Antonio Rojas <arojas@archlinux.org>",
            url="https://gmplib.org/",
            validation="pgp",
            reason=1,
            files=[],
            backup=[],
        )

        expected_package = Package(
            name="gmp",
            version="6.2.1-2",
            locations=[reader.location],
            licenses=["LGPL-3.0-only"],
            type=PackageType.AlpmPkg,
            metadata=expected_metadata,
            p_url="pkg:alpm/gmp@6.2.1-2?arch=x86_64&distro=arch-rolling&upstream=gmp",
            language=Language.UNKNOWN_LANGUAGE,
        )

        packages, relationships = parse_alpm_db(test_resolver, test_env, reader)

        assert len(packages) == 1
        assert packages[0] == expected_package
        assert len(relationships) == 0
