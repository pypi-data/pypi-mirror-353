import os
import shutil
import tempfile
from pathlib import Path


def get_test_data_path(relative_path: str) -> str:
    project_root = Path(__file__).parents[3]
    base_path = project_root / "test" / "data"
    return str(base_path / relative_path)


def create_zip_archive(source_dir: str, destination_archive_path: str) -> str:
    if destination_archive_path.endswith(".zip"):
        destination_archive_path = destination_archive_path[:-4]
    return shutil.make_archive(destination_archive_path, "zip", source_dir)


def ensure_nested_zip_exists(source_dir: str) -> None:
    nested_archive_file_path = os.path.join(source_dir, "nested.zip")
    create_zip_archive(source_dir, nested_archive_file_path)


def setup_zip_file_test(source_dir_path: str) -> str:
    archive_prefix = os.path.join(tempfile.gettempdir(), "archive-TEST-")
    destination_archive_path = f"{archive_prefix}.zip"
    create_zip_archive(source_dir_path, destination_archive_path)

    return destination_archive_path
