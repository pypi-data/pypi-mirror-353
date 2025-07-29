import shutil
import tempfile
from pathlib import Path
from types import ModuleType
from typing import cast

from labels.parsers.operations.utils import identify_release, parse_os_release
from labels.resolvers.directory import Directory
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.pytest_marks import parametrize_sync


def create_test_files(temp_dir: str, files: dict[str, str | None]) -> None:
    for path, content in files.items():
        file_path = Path(temp_dir, path.lstrip("/"))
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if content is None:
            file_path.touch(mode=0o000)
        else:
            with file_path.open("w") as f:
                f.write(content)


def test_identify_release_tries_all_files() -> None:
    temp_dir = tempfile.mkdtemp()
    try:
        files: dict[str, str | None] = {
            "/etc/os-release": "invalid=key=value\n",
            "/etc/system-release-cpe": "also invalid\n",
            "/etc/redhat-release": (
                "NAME=Ubuntu\nVERSION=20.04\n" "ID=ubuntu\nPRETTY_NAME=Ubuntu\n"
            ),
            "/bin/busybox": "NAME=BusyBox\nVERSION=1.0\n",
        }
        create_test_files(temp_dir, files)
        resolver = Directory(root=temp_dir, exclude=())

        result = identify_release(resolver)
        assert result is not None
        assert result.name == "Ubuntu"
        assert result.version == "20.04"
        assert result.id_ == "ubuntu"
    finally:
        shutil.rmtree(temp_dir)


def test_identify_release_no_valid_files() -> None:
    temp_dir = tempfile.mkdtemp()
    try:
        files: dict[str, str | None] = {
            "/etc/os-release": "invalid=key=value\n",
            "/etc/system-release-cpe": "",
            "/etc/redhat-release": "not a key value format\n",
        }
        create_test_files(temp_dir, files)
        resolver = Directory(root=temp_dir, exclude=())

        result = identify_release(resolver)
        assert result is None
    finally:
        shutil.rmtree(temp_dir)


@mocks(
    mocks=[
        Mock(
            module=cast(ModuleType, Directory),
            target="file_contents_by_location",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_identify_release_with_unreadable_file() -> None:
    temp_dir = tempfile.mkdtemp()
    try:
        files: dict[str, str | None] = {
            "/etc/os-release": "some content",
            "/etc/redhat-release": "not a key value format\n",
        }
        create_test_files(temp_dir, files)
        resolver = Directory(root=temp_dir, exclude=())

        result = identify_release(resolver)
        assert result is None
    finally:
        shutil.rmtree(temp_dir)


@parametrize_sync(
    args=["id_like_input", "expected_output"],
    cases=[
        ["debian ubuntu", ["debian", "ubuntu"]],
        ["fedora", ["fedora"]],
        ["rhel centos fedora", ["centos", "fedora", "rhel"]],
        ["", [""]],
    ],
)
def test_parse_os_release_id_like(id_like_input: str, expected_output: list[str]) -> None:
    content = f"NAME=Test\nID_LIKE={id_like_input}"
    result = parse_os_release(content)
    assert result is not None
    assert result.id_like == expected_output
