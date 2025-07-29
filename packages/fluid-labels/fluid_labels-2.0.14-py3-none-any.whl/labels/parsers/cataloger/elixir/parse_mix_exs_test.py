from io import BytesIO, TextIOWrapper
from pathlib import Path

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.elixir.parse_mix_exs import _get_location, parse_mix_exs
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_mix_lock() -> None:
    test_data_path = get_test_data_path("dependencies/elixir/mix.exs")
    expected_packages = [
        Package(
            name="poison",
            version="3.1.0",
            language=Language.ELIXIR,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=21,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.HexPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:hex/poison@3.1.0",
        ),
        Package(
            name="plug",
            version="1.3.0",
            language=Language.ELIXIR,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=22,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.HexPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:hex/plug@1.3.0",
        ),
        Package(
            name="coherence",
            version="0.5",
            language=Language.ELIXIR,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=23,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.HexPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:hex/coherence@0.5",
        ),
        Package(
            name="ecto",
            version="2.2.0",
            language=Language.ELIXIR,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=24,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.DEV,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.HexPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
            metadata=None,
            p_url="pkg:hex/ecto@2.2.0",
        ),
        Package(
            name="inch_ex",
            version="1.0",
            language=Language.ELIXIR,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=25,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.HexPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:hex/inch_ex@1.0",
        ),
    ]

    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_mix_exs(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        assert pkgs == expected_packages


def test_get_location() -> None:
    test_content = b"test content"
    reader = TextIOWrapper(BytesIO(test_content))
    location = new_location("test/mix.exs")
    location.coordinates = None

    location_reader = LocationReadCloser(
        location=location,
        read_closer=reader,
    )

    result = _get_location(location_reader, 10, is_dev=True)

    assert result.scope == Scope.DEV
    assert result.dependency_type == DependencyType.UNKNOWN


def test_parse_mix_exs_with_mixed_deps() -> None:
    content = b""
    reader = TextIOWrapper(BytesIO(content))
    location = new_location("test/mix.exs")

    packages, relationships = parse_mix_exs(
        None,
        None,
        LocationReadCloser(location=location, read_closer=reader),
    )

    assert len(packages) == 0
    assert len(relationships) == 0
