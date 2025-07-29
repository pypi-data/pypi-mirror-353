from io import BytesIO, TextIOWrapper
from pathlib import Path

from labels.model.file import Coordinates, Location, LocationReadCloser, Scope
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.cpp.parse_conan_lock import parse_conan_lock
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_conan_lock() -> None:
    test_data_path = get_test_data_path("dependencies/cpp/conan.lock")
    expected_packages = [
        Package(
            name="xbyak",
            version="6.73",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=4,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:conan/xbyak@6.73",
        ),
        Package(
            name="snappy",
            version="1.1.10",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=5,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:conan/snappy@1.1.10",
        ),
        Package(
            name="rapidjson",
            version="cci.20220822",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=6,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:conan/rapidjson@cci.20220822",
        ),
        Package(
            name="pybind11",
            version="2.12.0",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=7,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:conan/pybind11@2.12.0",
        ),
        Package(
            name="pugixml",
            version="1.13",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=8,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:conan/pugixml@1.13",
        ),
        Package(
            name="zlib",
            version="1.2.13",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=11,
                    ),
                    scope=Scope.DEV,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
            metadata=None,
            p_url="pkg:conan/zlib@1.2.13",
        ),
        Package(
            name="protobuf",
            version="3.21.12",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=12,
                    ),
                    scope=Scope.DEV,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
            metadata=None,
            p_url="pkg:conan/protobuf@3.21.12",
        ),
        Package(
            name="pkgconf",
            version="1.9.5",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=13,
                    ),
                    scope=Scope.DEV,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
            metadata=None,
            p_url="pkg:conan/pkgconf@1.9.5",
        ),
        Package(
            name="patchelf",
            version="0.13",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=14,
                    ),
                    scope=Scope.DEV,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
            metadata=None,
            p_url="pkg:conan/patchelf@0.13",
        ),
        Package(
            name="ninja",
            version="1.11.1",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=15,
                    ),
                    scope=Scope.DEV,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
            metadata=None,
            p_url="pkg:conan/ninja@1.11.1",
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_conan_lock(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        assert pkgs == expected_packages


def test_parse_conan_lock_without_coordinates() -> None:
    test_data_path = "/mock/path/conan.lock"
    expected_packages = [
        Package(
            name="xbyak",
            version="6.73",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    coordinates=None,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:conan/xbyak@6.73",
        ),
        Package(
            name="zlib",
            version="1.2.13",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    coordinates=None,
                    access_path=test_data_path,
                    scope=Scope.DEV,
                    annotations={},
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
            metadata=None,
            p_url="pkg:conan/zlib@1.2.13",
        ),
    ]

    json_content = b"""{
        "requires": ["xbyak/6.73"],
        "build_requires": ["zlib/1.2.13"]
    }"""

    reader = TextIOWrapper(BytesIO(json_content), encoding="utf-8")
    location = new_location(test_data_path)
    location.coordinates = None
    pkgs, _ = parse_conan_lock(
        None,
        None,
        LocationReadCloser(location=location, read_closer=reader),
    )

    for i, expected_pkg in enumerate(expected_packages):
        pkg = pkgs[i]
        pkg.health_metadata = None
        pkg.licenses = []
        assert pkg == expected_pkg

    for pkg in pkgs:
        assert pkg.locations[0].coordinates is None
