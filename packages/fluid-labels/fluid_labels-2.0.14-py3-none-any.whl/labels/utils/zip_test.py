import tempfile
import zipfile
from pathlib import Path

from labels.testing.utils.helpers import (
    ensure_nested_zip_exists,
    get_test_data_path,
    setup_zip_file_test,
)
from labels.testing.utils.pytest_marks import parametrize_sync
from labels.utils.zip import (
    contents_from_zip,
    new_zip_file_manifest,
    normalize_zip_entry_name,
    traverse_files_in_zip,
    zip_glob_match,
)


def test_new_zip_file_manifest() -> None:
    source_dir = get_test_data_path("zip/zip_source")
    ensure_nested_zip_exists(source_dir)

    archive_file_path = setup_zip_file_test(source_dir)
    actual_manifest = new_zip_file_manifest(archive_file_path)

    expected_zip_entries = [
        "b-file.txt",
        "nested.zip",
        "some_dir/",
        str(Path("some_dir") / "a-file.txt"),
    ]
    assert sorted([x.filename for x in actual_manifest]) == expected_zip_entries


def test_new_zip_file_manifest_with_bad_zip() -> None:
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
        tmp_file.write(b"This is not a valid zip file")
        tmp_file.flush()

        result = new_zip_file_manifest(tmp_file.name)
        assert result == []

    Path(tmp_file.name).unlink()


@parametrize_sync(
    args=["glob", "expected"],
    cases=[
        [
            "/b*",
            "b-file.txt",
        ],
        [
            "*/a-file.txt",
            "some_dir/a-file.txt",
        ],
        [
            "*/A-file.txt",
            "some_dir/a-file.txt",
        ],
        [
            "**/*.zip",
            "nested.zip",
        ],
    ],
)
def test_zip_file_manifest_glob_match(
    glob: str,
    expected: str,
) -> None:
    source_dir = get_test_data_path("zip/zip_source")
    ensure_nested_zip_exists(source_dir)

    archive_file_path = setup_zip_file_test(source_dir)
    manifest = new_zip_file_manifest(archive_file_path)
    result = zip_glob_match(manifest, case_sensitive=True, patterns=(glob,))
    assert len(result) == 1
    assert result[0] == expected


def test_contents_from_zip() -> None:
    expected = {
        str(Path("some_dir") / "a-file.txt"): "A file! nice!",
        str(Path("b-file.txt")): "B file...",
    }
    source_dir = get_test_data_path("zip/zip_source")
    ensure_nested_zip_exists(source_dir)

    archive_file_path = setup_zip_file_test(source_dir)
    result = contents_from_zip(archive_file_path, *expected.keys())
    assert result == expected


@parametrize_sync(
    args=["entry", "case_insensitive", "expected"],
    cases=[
        ["MiArchivo.TXT", True, "/miarchivo.txt"],
        ["path/TO/File.ZIP", True, "/path/to/file.zip"],
        ["UPPERCASE.doc", True, "/uppercase.doc"],
        ["MixedCase.PDF", False, "/MixedCase.PDF"],
        ["already/has/slash/", True, "/already/has/slash/"],
        ["no/leading/slash", False, "/no/leading/slash"],
        ["/with/leading/slash", True, "/with/leading/slash"],
        ["single.file", False, "/single.file"],
    ],
)
def test_normalize_zip_entry_name(
    entry: str,
    *,
    case_insensitive: bool,
    expected: str,
) -> None:
    result = normalize_zip_entry_name(entry, case_insensitive=case_insensitive)
    assert result == expected


def test_zip_glob_match_endswith() -> None:
    test_entries = [
        zipfile.ZipInfo(filename="test.txt"),
        zipfile.ZipInfo(filename="file.txt"),
        zipfile.ZipInfo(filename="other.doc"),
    ]
    result = zip_glob_match(test_entries, case_sensitive=True, patterns=(".txt",))
    assert len(result) == 2
    assert all(name.endswith(".txt") for name in result)


def test_traverse_files_in_zip_not_found() -> None:
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
        with zipfile.ZipFile(tmp_file.name, "w") as zip_writer:
            zip_writer.writestr("test.txt", "content")

        def visitor(info: zipfile.ZipInfo) -> None:
            pass

        traverse_files_in_zip(tmp_file.name, visitor, "nonexistent.txt")

    Path(tmp_file.name).unlink()


def test_contents_from_zip_empty_paths() -> None:
    result = contents_from_zip("dummy.zip")
    assert result == {}


def test_contents_from_zip_with_directory() -> None:
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
        with zipfile.ZipFile(tmp_file.name, "w") as zip_writer:
            dir_info = zipfile.ZipInfo("test_dir/")
            dir_info.external_attr = 0o40775 << 16
            zip_writer.writestr(dir_info, "")
            zip_writer.writestr("test.txt", "content")

        result = contents_from_zip(tmp_file.name, "test_dir/", "test.txt")
        assert len(result) == 1
        assert "test.txt" in result

    Path(tmp_file.name).unlink()
