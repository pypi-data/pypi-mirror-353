from io import StringIO
from pathlib import Path

from labels.model.package import Digest
from labels.parsers.cataloger.debian.model import DpkgFileRecord
from labels.parsers.cataloger.debian.parse_dpkg_info_files import (
    _process_line,
    parse_dpkg_conffile_info,
    parse_dpkg_md5_info,
)
from labels.testing.utils.helpers import get_test_data_path
from labels.testing.utils.pytest_marks import parametrize_sync


@parametrize_sync(
    args=["test_data", "expected"],
    cases=[
        [
            "dependencies/debian/info/zlib1g.md5sums",
            [
                DpkgFileRecord(
                    path="/lib/x86_64-linux-gnu/libz.so.1.2.11",
                    digest=Digest(
                        algorithm="md5",
                        value="55f905631797551d4d936a34c7e73474",
                    ),
                ),
                DpkgFileRecord(
                    path="/usr/share/doc/zlib1g/changelog.Debian.gz",
                    digest=Digest(
                        algorithm="md5",
                        value="cede84bda30d2380217f97753c8ccf3a",
                    ),
                ),
                DpkgFileRecord(
                    path="/usr/share/doc/zlib1g/changelog.gz",
                    digest=Digest(
                        algorithm="md5",
                        value="f3c9dafa6da7992c47328b4464f6d122",
                    ),
                ),
                DpkgFileRecord(
                    path="/usr/share/doc/zlib1g/copyright",
                    digest=Digest(
                        algorithm="md5",
                        value="a4fae96070439a5209a62ae5b8017ab2",
                    ),
                ),
            ],
        ],
    ],
)
def test_md5_sum_info_parsing(
    test_data: str,
    expected: list[DpkgFileRecord],
) -> None:
    test_data_path = get_test_data_path(test_data)
    with Path(test_data_path).open(encoding="utf-8") as handler:
        actual = parse_dpkg_md5_info(handler)
        assert expected == actual


@parametrize_sync(
    args=["test_data", "expected"],
    cases=[
        [
            "dependencies/debian/info/util-linux.conffiles",
            [
                DpkgFileRecord(path="/etc/default/hwclock", is_config_file=True),
                DpkgFileRecord(path="/etc/init.d/hwclock.sh", is_config_file=True),
                DpkgFileRecord(path="/etc/pam.d/runuser", is_config_file=True),
                DpkgFileRecord(path="/etc/pam.d/runuser-l", is_config_file=True),
                DpkgFileRecord(path="/etc/pam.d/su", is_config_file=True),
                DpkgFileRecord(path="/etc/pam.d/su-l", is_config_file=True),
            ],
        ],
    ],
)
def test_conffile_info_parsing(
    test_data: str,
    expected: list[DpkgFileRecord],
) -> None:
    test_data_path = get_test_data_path(test_data)
    with Path(test_data_path).open(encoding="utf-8") as handler:
        actual = parse_dpkg_conffile_info(handler)
        assert expected == actual


@parametrize_sync(
    args=["input_content", "expected"],
    cases=[
        [
            "abc123  /usr/bin/file\n",
            [
                DpkgFileRecord(
                    path="/usr/bin/file",
                    digest=Digest(algorithm="md5", value="abc123"),
                ),
            ],
        ],
        [
            "def456  usr/lib/file\n",
            [
                DpkgFileRecord(
                    path="/usr/lib/file",
                    digest=Digest(algorithm="md5", value="def456"),
                ),
            ],
        ],
        [
            "abc123  /path1\ndef456  path2\n",
            [
                DpkgFileRecord(
                    path="/path1",
                    digest=Digest(algorithm="md5", value="abc123"),
                ),
                DpkgFileRecord(
                    path="/path2",
                    digest=Digest(algorithm="md5", value="def456"),
                ),
            ],
        ],
        [
            "invalid_line\n",
            [],
        ],
    ],
)
def test_parse_dpkg_md5_info_record_creation(
    input_content: str,
    expected: list[DpkgFileRecord],
) -> None:
    reader = StringIO(input_content)
    actual = parse_dpkg_md5_info(reader)
    assert actual == expected


@parametrize_sync(
    args=["input_line", "expected_path", "expected_digest"],
    cases=[
        [
            "etc/config abc123",
            "/etc/config",
            Digest(algorithm="md5", value="abc123"),
        ],
        [
            "/usr/bin/file def456",
            "/usr/bin/file",
            Digest(algorithm="md5", value="def456"),
        ],
        [
            "  relative/path 123abc  ",
            "/relative/path",
            Digest(algorithm="md5", value="123abc"),
        ],
        [
            "",
            "",
            None,
        ],
        [
            "invalid_line",
            "/invalid_line",
            None,
        ],
    ],
)
def test_process_line_path_normalization(
    input_line: str,
    expected_path: str,
    expected_digest: Digest | None,
) -> None:
    actual_path, actual_digest = _process_line(input_line)
    assert actual_path == expected_path
    assert actual_digest == expected_digest
