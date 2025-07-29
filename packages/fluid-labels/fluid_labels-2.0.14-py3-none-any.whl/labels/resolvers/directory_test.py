import contextlib
import os
import shutil
import tempfile
from pathlib import Path

import pytest

from labels.model.file import Coordinates, Location, Type
from labels.resolvers.directory import (
    Directory,
    DirectoryContentResolver,
    DirectoryMetadataResolver,
    DirectoryPathResolver,
    _normalize_rules,
)


def create_test_directory() -> str:
    temp_dir = tempfile.mkdtemp()
    Path(temp_dir, "subdir1").mkdir(parents=True)
    Path(temp_dir, "subdir2", "nested").mkdir(parents=True)
    Path(temp_dir, "node_modules", "package").mkdir(parents=True)
    Path(temp_dir, "__pycache__").mkdir(parents=True)

    with Path(temp_dir, "file1.txt").open("w") as f:
        f.write("test content 1")
    with Path(temp_dir, "subdir1", "file2.txt").open("w") as f:
        f.write("test content 2")
    with Path(temp_dir, "subdir2", "file3.py").open("w") as f:
        f.write("print('Hello World')")

    with contextlib.suppress(OSError, AttributeError):
        os.symlink(
            os.path.join(temp_dir, "file1.txt"),
            os.path.join(temp_dir, "link_to_file1.txt"),
        )

    return temp_dir


def test_has_path() -> None:
    test_directory = create_test_directory()
    try:
        directory_resolver = DirectoryPathResolver(root=test_directory)
        assert directory_resolver.has_path("file1.txt")
        assert directory_resolver.has_path("/file1.txt")
        assert directory_resolver.has_path("subdir1/file2.txt")
        assert not directory_resolver.has_path("nonexistent.txt")
    finally:
        shutil.rmtree(test_directory)


def test_files_by_path() -> None:
    test_directory = create_test_directory()
    try:
        directory_resolver = DirectoryPathResolver(root=test_directory)
        locations = directory_resolver.files_by_path(
            "file1.txt",
            "subdir1/file2.txt",
            "nonexistent.txt",
        )
        assert len(locations) == 2
        assert locations[0].access_path == "file1.txt"
        assert locations[0].coordinates
        assert locations[0].coordinates.real_path == str(
            Path(test_directory).resolve() / "file1.txt",
        )

    finally:
        shutil.rmtree(test_directory)


def test_files_by_glob() -> None:
    test_directory = create_test_directory()
    try:
        directory_resolver = DirectoryPathResolver(root=test_directory)
        locations = directory_resolver.files_by_glob("**/*.txt")
        assert len(locations) == 3

        py_locations = directory_resolver.files_by_glob("**/*.py")
        assert len(py_locations) == 1
        assert py_locations[0].access_path == "subdir2/file3.py"
    finally:
        shutil.rmtree(test_directory)


def test_file_contents_by_location() -> None:
    test_directory = create_test_directory()
    try:
        directory_resolver = DirectoryContentResolver(root=test_directory)
        location = Location(
            coordinates=Coordinates(
                real_path=os.path.join(test_directory, "file1.txt"),
                file_system_id="",
            ),
            access_path="file1.txt",
        )
        file_contents = directory_resolver.file_contents_by_location(location)
        assert file_contents
        with file_contents as f:
            content = f.read()
            assert content == "test content 1"

        nonexistent_location = Location(
            coordinates=Coordinates(
                real_path=os.path.join(test_directory, "nonexistent.txt"),
                file_system_id="",
            ),
            access_path="nonexistent.txt",
        )
        assert directory_resolver.file_contents_by_location(nonexistent_location) is None
    finally:
        shutil.rmtree(test_directory)


async def test_file_metadata_by_location() -> None:
    test_directory = create_test_directory()
    try:
        directory_resolver = DirectoryMetadataResolver(root=test_directory)
        file_location = Location(
            coordinates=Coordinates(
                real_path=os.path.join(test_directory, "file1.txt"),
                file_system_id="",
            ),
            access_path=os.path.join(test_directory, "file1.txt"),
        )

        metadata = directory_resolver.file_metadata_by_location(file_location)

        assert metadata is not None
        assert metadata.path == os.path.join(test_directory, "file1.txt")
        assert metadata.type == Type.TYPE_REGULAR
        assert metadata.mime_type == "text/plain"
    finally:
        shutil.rmtree(test_directory)


async def test_symlink_metadata() -> None:
    test_directory = create_test_directory()
    try:
        directory_resolver = DirectoryMetadataResolver(root=test_directory)
        link_path = os.path.join(test_directory, "link_to_file1.txt")
        if not Path(link_path).exists():
            pytest.skip("Symlinks not supported on this platform/configuration")

        location = Location(
            coordinates=Coordinates(real_path=link_path, file_system_id=""),
            access_path=link_path,
        )

        metadata = directory_resolver.file_metadata_by_location(location)
        assert metadata is not None
        assert metadata.type == Type.TYPE_SYM_LINK
        assert "file1.txt" in metadata.link_destination
    finally:
        shutil.rmtree(test_directory)


async def test_file_metadata_by_location_directory() -> None:
    test_directory = create_test_directory()
    try:
        directory_resolver = DirectoryMetadataResolver(root=test_directory)

        dir_location = Location(
            coordinates=Coordinates(
                real_path=os.path.join(test_directory, "subdir1"),
                file_system_id="",
            ),
            access_path=os.path.join(test_directory, "subdir1"),
        )

        metadata = directory_resolver.file_metadata_by_location(dir_location)

        assert metadata is not None
        assert metadata.type == Type.TYPE_DIRECTORY
        assert metadata.path == os.path.join(test_directory, "subdir1")
        assert metadata.link_destination == ""
    finally:
        shutil.rmtree(test_directory)


async def test_file_metadata_by_location_regular_file() -> None:
    test_directory = create_test_directory()
    try:
        directory_resolver = DirectoryMetadataResolver(root=test_directory)
        file_location = Location(
            coordinates=Coordinates(
                real_path=os.path.join(test_directory, "file1.txt"),
                file_system_id="",
            ),
            access_path=os.path.join(test_directory, "file1.txt"),
        )

        metadata = directory_resolver.file_metadata_by_location(file_location)

        assert metadata is not None
        assert metadata.type == Type.TYPE_REGULAR
        assert metadata.path == os.path.join(test_directory, "file1.txt")
        assert metadata.mime_type == "text/plain"
    finally:
        shutil.rmtree(test_directory)


async def test_file_metadata_by_location_no_access_path() -> None:
    test_directory = create_test_directory()
    try:
        directory_resolver = DirectoryMetadataResolver(root=test_directory)
        location_none = Location(
            coordinates=Coordinates(
                real_path=os.path.join(test_directory, "file1.txt"),
                file_system_id="",
            ),
            access_path=None,
        )
        metadata_none = directory_resolver.file_metadata_by_location(location_none)
        assert metadata_none is None

        location_empty = Location(
            coordinates=Coordinates(
                real_path=os.path.join(test_directory, "file1.txt"),
                file_system_id="",
            ),
            access_path="",
        )
        metadata_empty = directory_resolver.file_metadata_by_location(location_empty)
        assert metadata_empty is None
    finally:
        shutil.rmtree(test_directory)


def test_relative_file_path() -> None:
    test_directory = create_test_directory()
    try:
        directory_resolver = DirectoryPathResolver(
            root=test_directory,
        )
        dummy_location = Location(
            coordinates=Coordinates(real_path="", file_system_id=""),
            access_path="",
        )

        full_path = os.path.realpath(os.path.join(test_directory, "subdir1", "file2.txt"))
        result = directory_resolver.relative_file_path(dummy_location, full_path)

        assert result.access_path == "subdir1/file2.txt"
        assert result.coordinates
        assert result.coordinates.real_path == full_path
    finally:
        shutil.rmtree(test_directory)


def test_walk_file() -> None:
    test_directory = create_test_directory()
    try:
        directory_resolver = DirectoryPathResolver(
            root=test_directory,
        )
        file_paths = list(directory_resolver.walk_file())

        assert "file1.txt" in file_paths
        assert "subdir1/file2.txt" in file_paths
        assert "subdir2/file3.py" in file_paths

        node_modules_files = [path for path in file_paths if "node_modules" in path]
        assert len(node_modules_files) == 0

        pycache_files = [path for path in file_paths if "__pycache__" in path]
        assert len(pycache_files) == 0
    finally:
        shutil.rmtree(test_directory)


def test_walk_file_with_exclusion_rules() -> None:
    test_directory = create_test_directory()
    try:
        with Path(test_directory, "exclude_me.txt").open("w") as f:
            f.write("This file should be excluded")
        with Path(test_directory, "subdir1", "also_exclude.txt").open("w") as f:
            f.write("This file should also be excluded")

        directory_resolver = DirectoryPathResolver(
            root=test_directory,
            exclude=("*exclude*.txt", "node_modules", "__pycache__"),
        )
        file_paths = list(directory_resolver.walk_file())

        assert "file1.txt" in file_paths
        assert "subdir1/file2.txt" in file_paths
        assert "subdir2/file3.py" in file_paths

        assert "exclude_me.txt" not in file_paths
        assert "subdir1/also_exclude.txt" not in file_paths

        node_modules_files = [path for path in file_paths if "node_modules" in path]
        assert len(node_modules_files) == 0
        pycache_files = [path for path in file_paths if "__pycache__" in path]
        assert len(pycache_files) == 0

        wildcard_resolver = DirectoryPathResolver(
            root=test_directory,
            exclude=("*.txt", "node_modules", "__pycache__"),
        )
        wildcard_paths = list(wildcard_resolver.walk_file())

        assert "subdir2/file3.py" in wildcard_paths
        assert "file1.txt" not in wildcard_paths
        assert "subdir1/file2.txt" not in wildcard_paths
    finally:
        shutil.rmtree(test_directory)


def test_normalize_rules_general() -> None:
    rules = ("glob(*.py)", ".", "**/node_modules/", "dist/")
    normalized = _normalize_rules(rules)

    assert "*.py" in normalized
    assert "**" in normalized
    assert "node_modules/**" in normalized
    assert "dist/**" in normalized


def test_normalize_rules_glob_wrapper() -> None:
    rules_glob = ("glob(pattern)", "glob(another)")
    normalized_glob = _normalize_rules(rules_glob)
    assert normalized_glob == ("pattern", "another")


def test_normalize_rules_dot_to_asterisks() -> None:
    rules_dot = (".", "other")
    normalized_dot = _normalize_rules(rules_dot)
    assert normalized_dot == ("**", "other")


def test_normalize_rules_trailing_slash() -> None:
    rules_slash = ("dir/", "file")
    normalized_slash = _normalize_rules(rules_slash)
    assert normalized_slash == ("dir/**", "file")


def test_normalize_rules_combined_transformations() -> None:
    rules_combined = ("**/dir/", "**/node_modules")
    normalized_combined = _normalize_rules(rules_combined)
    assert "dir/**" in normalized_combined
    assert "node_modules" in normalized_combined


def test_normalize_rules_empty() -> None:
    rules_empty: tuple[str, ...] = ()
    normalized_empty = _normalize_rules(rules_empty)
    assert normalized_empty == ()


async def test_directory_minimal_integration() -> None:
    test_directory = create_test_directory()
    try:
        directory = Directory(
            root=test_directory,
        )

        assert directory.has_path("file1.txt")
        assert not directory.has_path("nonexistent.txt")

        locations = directory.files_by_path("file1.txt", "subdir1/file2.txt")
        assert len(locations) == 2
        file1_location = locations[0]

        txt_files = directory.files_by_glob("**/*.txt")
        assert len(txt_files) >= 1

        contents = directory.file_contents_by_location(file1_location)
        assert contents is not None
        with contents as f:
            content = f.read()
            assert content == "test content 1"

        full_file_path = os.path.join(test_directory, "file1.txt")
        metadata_location = Location(
            coordinates=Coordinates(
                real_path=full_file_path,
                file_system_id="",
            ),
            access_path=full_file_path,
        )
        metadata = directory.file_metadata_by_location(metadata_location)
        assert metadata is not None
        assert metadata.type == Type.TYPE_REGULAR
        assert metadata.mime_type == "text/plain"

        full_path = os.path.realpath(os.path.join(test_directory, "subdir1", "file2.txt"))
        relative_location = directory.relative_file_path(file1_location, full_path)
        assert relative_location.access_path == "subdir1/file2.txt"

        all_files = list(directory.walk_file())
        assert "file1.txt" in all_files
        assert "subdir1/file2.txt" in all_files

    finally:
        shutil.rmtree(test_directory)
