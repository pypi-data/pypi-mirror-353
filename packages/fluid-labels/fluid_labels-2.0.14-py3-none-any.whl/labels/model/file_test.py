import pytest

from labels.model.file import (
    Coordinates,
    Location,
    LocationData,
    LocationMetadata,
)


def test_coordinates() -> None:
    coords = Coordinates(real_path="/test/path", file_system_id="layer1", line=10)
    assert str(coords) == "Location<RealPath=/test/path Layer=layer1>"

    coords_no_layer = Coordinates(real_path="/test/path")
    assert str(coords_no_layer) == "Location<RealPath=/test/path>"


def test_location_metadata() -> None:
    metadata1 = LocationMetadata(annotations={"key1": "value1"})
    metadata2 = LocationMetadata(annotations={"key2": "value2"})

    merged = metadata1.merge(metadata2)
    assert merged.annotations == {"key1": "value1", "key2": "value2"}


def test_location_data() -> None:
    coords = Coordinates(real_path="/test/path", file_system_id="layer1")
    loc_data = LocationData(coordinates=coords, access_path="/access/path")

    expected_hash = hash((loc_data.access_path, loc_data.coordinates.file_system_id))
    assert hash(loc_data) == expected_hash


def test_location_path_error() -> None:
    location = Location()
    with pytest.raises(ValueError, match="Both access_path and coordinates.real_path are empty"):
        location.path()


def test_location_path_spaces() -> None:
    location = Location(access_path="/test path/with spaces")
    assert location.path() == "/test_path/with_spaces"
