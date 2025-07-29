import tarfile
import tempfile
from pathlib import Path
from typing import cast

from labels.model.file import Coordinates, Location
from labels.testing.utils.pytest_marks import parametrize_sync
from labels.testing.utils.pytest_methods import raises
from labels.utils.file import (
    extract_tar_file,
    new_location,
    new_location_from_image,
    parse_bytes,
)


@parametrize_sync(
    args=["input_str", "expected"],
    cases=[
        ["1", 1],
        ["1k", 1000],
        ["1ki", 1024],
        ["1kb", 1000],
        ["1kib", 1024],
        ["2mb", 2 * 1000**2],
        ["2.5Mi", int(2.5 * 1024**2)],
        ["1gb", 1000**3],
        ["1Gi", 1024**3],
        ["3.2TB", int(3.2 * 1000**4)],
        ["0.5Pi", int(0.5 * 1024**5)],
        ["100", 100],
        ["1,000", 1000],
    ],
)
def test_parse_bytes(input_str: str, expected: int) -> None:
    assert parse_bytes(input_str) == expected


@parametrize_sync(
    args=["invalid_input"],
    cases=[
        ["abc"],
        ["10zb"],
        ["10yy"],
        ["12..3kb"],
    ],
)
def test_parse_bytes_invalid(invalid_input: str) -> None:
    with raises(ValueError):
        parse_bytes(invalid_input)


def test_extract_tar_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        tar_path = temp_path / "test.tar"
        content_path = temp_path / "content.txt"

        content_path.write_text("test content")

        with tarfile.open(tar_path, "w") as tar:
            tar.add(str(content_path), arcname="/test/content.txt")

        extract_dir = temp_path / "extract"
        extract_dir.mkdir(parents=True)
        extract_tar_file(str(tar_path), str(extract_dir))

        extracted_file = extract_dir / "test/content.txt"
        assert extracted_file.exists()
        assert extracted_file.read_text() == "test content"


def test_new_location_from_image() -> None:
    location = new_location_from_image(
        access_path="test/path",
        layer_id="layer123",
        real_path="/real/path",
    )
    assert isinstance(location, Location)
    assert location.access_path == "/test/path"
    coordinates = cast(Coordinates, location.coordinates)
    assert coordinates.file_system_id == "layer123"
    assert coordinates.real_path == "/real/path"

    location = new_location_from_image(
        access_path=None,
        layer_id="layer123",
    )
    assert location.access_path is None
    coordinates = cast(Coordinates, location.coordinates)
    assert coordinates.real_path == ""
    assert coordinates.file_system_id == "layer123"


def test_new_location() -> None:
    location = new_location("/test/path")
    assert isinstance(location, Location)
    assert location.access_path == "/test/path"
    coordinates = cast(Coordinates, location.coordinates)
    assert coordinates.real_path == "/test/path"
    assert location.annotations == {}
