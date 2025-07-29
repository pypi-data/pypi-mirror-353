from io import BytesIO, TextIOWrapper
from pathlib import Path

import labels.parsers.cataloger.swift.parse_package_resolved
from labels.model.file import Coordinates, Location, LocationReadCloser
from labels.model.indexables import FileCoordinate, IndexedDict, ParsedValue, Position
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.swift.package import SwiftPackageManagerResolvedEntry
from labels.parsers.cataloger.swift.parse_package_resolved import (
    _get_name_and_version,
    parse_package_resolved,
)
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_pacakge_resolved() -> None:
    test_data_path = get_test_data_path("dependencies/swift/Package.resolved")
    expected = [
        Package(
            name="swift-algorithms",
            version="1.0.0",
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
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.SwiftPkg,
            metadata=SwiftPackageManagerResolvedEntry(
                revision="b14b7f4c528c942f121c8b860b9410b2bf57825e",
            ),
            p_url=("pkg:swift/github.com/apple/swift-algorithms.git/swift-algorithms@1.0.0"),
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="swift-async-algorithms",
            version="0.1.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=13,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.SwiftPkg,
            metadata=SwiftPackageManagerResolvedEntry(
                revision="9cfed92b026c524674ed869a4ff2dcfdeedf8a2a",
            ),
            p_url=(
                "pkg:swift/github.com/apple/swift-async-algorithms.git"
                "/swift-async-algorithms@0.1.0"
            ),
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="vapor",
            version="1.0.0",
            language=Language.SWIFT,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=22,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.SwiftPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=SwiftPackageManagerResolvedEntry(
                revision="9cfed92b026c524674ed869a4ff2dcfdeedf8a2a",
            ),
            p_url="pkg:swift/github.com/apple/vapor.git/vapor@1.0.0",
        ),
        Package(
            name="swift-atomics",
            version="1.1.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=31,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.SwiftPkg,
            metadata=SwiftPackageManagerResolvedEntry(
                revision="6c89474e62719ddcc1e9614989fff2f68208fe10",
            ),
            p_url=("pkg:swift/github.com/apple/swift-atomics.git/swift-atomics@1.1.0"),
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="swift-collections",
            version="1.0.4",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=40,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.SwiftPkg,
            metadata=SwiftPackageManagerResolvedEntry(
                revision="937e904258d22af6e447a0b72c0bc67583ef64a2",
            ),
            p_url=("pkg:swift/github.com/apple/swift-collections.git/swift-collections@1.0.4"),
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="swift-numerics",
            version="1.0.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=49,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.SwiftPkg,
            metadata=SwiftPackageManagerResolvedEntry(
                revision="0a5bc04095a675662cf24757cc0640aa2204253b",
            ),
            p_url=("pkg:swift/github.com/apple/swift-numerics/swift-numerics@1.0.2"),
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_package_resolved(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
    assert pkgs == expected


def test_get_name_and_version_not_indexed_dict() -> None:
    invalid_pin = "not a dict"
    result = _get_name_and_version(invalid_pin)
    assert result is None


def test_get_name_and_version_state_not_indexed_dict() -> None:
    mock_position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=1),
    )
    pin = IndexedDict[str, ParsedValue]()
    pin[("state", mock_position)] = ("not a dict", mock_position)
    result = _get_name_and_version(pin)
    assert result is None


def test_get_name_and_version_invalid_name_or_version() -> None:
    mock_position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=1),
    )
    state = IndexedDict[str, ParsedValue]()

    pin = IndexedDict[str, ParsedValue]()
    pin[("state", mock_position)] = (state, mock_position)

    state[("version", mock_position)] = (123, mock_position)
    pin[("identity", mock_position)] = ("test-package", mock_position)
    result = _get_name_and_version(pin)
    assert result is None


def test_parse_package_resolved_pins_not_indexed_list() -> None:
    json_content = '{"pins": "not a list"}'
    json_bytes = BytesIO(json_content.encode("utf-8"))
    reader = LocationReadCloser(
        location=new_location("Package.resolved"),
        read_closer=TextIOWrapper(json_bytes, encoding="utf-8"),
    )
    packages, relationships = parse_package_resolved(None, None, reader)
    assert len(packages) == 0
    assert len(relationships) == 0


def test_parse_package_resolved_pin_not_indexed_dict() -> None:
    json_content = '{"pins": ["not a dict", {"identity": "test", "state": {"version": "1.0.0"}}]}'
    json_bytes = BytesIO(json_content.encode("utf-8"))
    reader = LocationReadCloser(
        location=new_location("Package.resolved"),
        read_closer=TextIOWrapper(json_bytes, encoding="utf-8"),
    )
    packages, relationships = parse_package_resolved(None, None, reader)
    assert len(packages) == 1
    assert len(relationships) == 0


def test_parse_package_resolved_invalid_pin_info() -> None:
    json_content = (
        '{"pins": ['
        '{"identity": "test", "state": {"version": 123}}, '
        '{"identity": "valid", "state": {"version": "1.0.0"}}'
        "]}"
    )
    json_bytes = BytesIO(json_content.encode("utf-8"))
    reader = LocationReadCloser(
        location=new_location("Package.resolved"),
        read_closer=TextIOWrapper(json_bytes, encoding="utf-8"),
    )
    packages, relationships = parse_package_resolved(None, None, reader)
    assert len(packages) == 1
    assert len(relationships) == 0


def test_parse_package_resolved_no_coordinates() -> None:
    json_content = '{"pins": [{"identity": "test", "state": {"version": "1.0.0"}}]}'
    json_bytes = BytesIO(json_content.encode("utf-8"))
    location = Location(
        coordinates=None,
        access_path="Package.resolved",
    )
    reader = LocationReadCloser(
        location=location,
        read_closer=TextIOWrapper(json_bytes, encoding="utf-8"),
    )
    packages, relationships = parse_package_resolved(None, None, reader)
    assert len(packages) == 1
    assert len(relationships) == 0
    assert packages[0].locations[0].coordinates is None


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.cataloger.swift.parse_package_resolved,
            target="new_swift_package_manager_package",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_parse_package_resolved_package_creation_fails() -> None:
    json_content = '{"pins": [{"identity": "test", "state": {"version": "1.0.0"}}]}'
    json_bytes = BytesIO(json_content.encode("utf-8"))
    reader = LocationReadCloser(
        location=new_location("Package.resolved"),
        read_closer=TextIOWrapper(json_bytes, encoding="utf-8"),
    )
    packages, relationships = parse_package_resolved(None, None, reader)
    assert len(packages) == 0
    assert len(relationships) == 0
