from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import MagicMock, patch

from tree_sitter import Node

import labels.parsers.cataloger.swift.parse_podfile_lock as parse_lock
from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser
from labels.model.indexables import IndexedDict, IndexedList, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.swift.package import CocoaPodfileLockEntry
from labels.parsers.cataloger.swift.parse_podfile_lock import parse_podfile_lock
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_podsfile_lock() -> None:
    test_data_path = get_test_data_path("dependencies/swift/Podfile.lock")
    expected = [
        Package(
            name="GlossButtonNode",
            version="3.1.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=2,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="4ea1197a744f2fb5fb875fe31caf17ded4762e8f"),
            p_url="pkg:cocoapods/GlossButtonNode@3.1.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="PINCache",
            version="3.0.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=5,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="7a8fc1a691173d21dbddbf86cd515de6efa55086"),
            p_url="pkg:cocoapods/PINCache@3.0.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="PINCache/Arc-exception-safe",
            version="3.0.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=8,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="7a8fc1a691173d21dbddbf86cd515de6efa55086"),
            p_url="pkg:cocoapods/PINCache/Arc-exception-safe@3.0.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="PINCache/Core",
            version="3.0.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=10,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="7a8fc1a691173d21dbddbf86cd515de6efa55086"),
            p_url="pkg:cocoapods/PINCache/Core@3.0.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="PINOperation",
            version="1.2.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=12,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="00c935935f1e8cf0d1e2d6b542e75b88fc3e5e20"),
            p_url="pkg:cocoapods/PINOperation@1.2.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="PINRemoteImage/Core",
            version="3.0.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=13,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="f1295b29f8c5e640e25335a1b2bd9d805171bd01"),
            p_url="pkg:cocoapods/PINRemoteImage/Core@3.0.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="PINRemoteImage/iOS",
            version="3.0.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=15,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="f1295b29f8c5e640e25335a1b2bd9d805171bd01"),
            p_url="pkg:cocoapods/PINRemoteImage/iOS@3.0.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="PINRemoteImage/PINCache",
            version="3.0.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=17,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="f1295b29f8c5e640e25335a1b2bd9d805171bd01"),
            p_url="pkg:cocoapods/PINRemoteImage/PINCache@3.0.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="Reveal-SDK",
            version="33",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=20,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="effba1c940b8337195563c425a6b5862ec875caa"),
            p_url="pkg:cocoapods/Reveal-SDK@33",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="SwiftGen",
            version="6.5.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=21,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="a6d22010845f08fe18fbdf3a07a8e380fd22e0ea"),
            p_url="pkg:cocoapods/SwiftGen@6.5.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="Texture",
            version="3.1.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=22,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="2e8ab2519452515f7f5a520f5a8f7e0a413abfa3"),
            p_url="pkg:cocoapods/Texture@3.1.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="Texture/AssetsLibrary",
            version="3.1.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=29,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="2e8ab2519452515f7f5a520f5a8f7e0a413abfa3"),
            p_url="pkg:cocoapods/Texture/AssetsLibrary@3.1.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="Texture/Core",
            version="3.1.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=31,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="2e8ab2519452515f7f5a520f5a8f7e0a413abfa3"),
            p_url="pkg:cocoapods/Texture/Core@3.1.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="Texture/MapKit",
            version="3.1.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=32,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="2e8ab2519452515f7f5a520f5a8f7e0a413abfa3"),
            p_url="pkg:cocoapods/Texture/MapKit@3.1.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="Texture/Photos",
            version="3.1.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=34,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="2e8ab2519452515f7f5a520f5a8f7e0a413abfa3"),
            p_url="pkg:cocoapods/Texture/Photos@3.1.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="Texture/PINRemoteImage",
            version="3.1.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=36,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="2e8ab2519452515f7f5a520f5a8f7e0a413abfa3"),
            p_url="pkg:cocoapods/Texture/PINRemoteImage@3.1.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="Texture/Video",
            version="3.1.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=40,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="2e8ab2519452515f7f5a520f5a8f7e0a413abfa3"),
            p_url="pkg:cocoapods/Texture/Video@3.1.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="TextureSwiftSupport",
            version="3.13.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=42,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="c515c7927fab92d0d9485f49b885b8c5de34fbfb"),
            p_url="pkg:cocoapods/TextureSwiftSupport@3.13.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="TextureSwiftSupport/Components",
            version="3.13.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=48,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="c515c7927fab92d0d9485f49b885b8c5de34fbfb"),
            p_url="pkg:cocoapods/TextureSwiftSupport/Components@3.13.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="TextureSwiftSupport/Experiments",
            version="3.13.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=51,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="c515c7927fab92d0d9485f49b885b8c5de34fbfb"),
            p_url="pkg:cocoapods/TextureSwiftSupport/Experiments@3.13.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="TextureSwiftSupport/Extensions",
            version="3.13.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=53,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="c515c7927fab92d0d9485f49b885b8c5de34fbfb"),
            p_url="pkg:cocoapods/TextureSwiftSupport/Extensions@3.13.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="TextureSwiftSupport/LayoutSpecBuilders",
            version="3.13.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=55,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.TRANSITIVE,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="c515c7927fab92d0d9485f49b885b8c5de34fbfb"),
            p_url=("pkg:cocoapods/TextureSwiftSupport/LayoutSpecBuilders@3.13.0"),
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
        Package(
            name="TinyConstraints",
            version="4.0.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=57,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            language=Language.SWIFT,
            licenses=[],
            type=PackageType.CocoapodsPkg,
            metadata=CocoaPodfileLockEntry(checksum="7b7ccc0c485bb3bb47082138ff28bc33cd49897f"),
            p_url="pkg:cocoapods/TinyConstraints@4.0.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_podfile_lock(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
    assert pkgs == expected


def test_parse_podsfile_lock_invalid_yaml() -> None:
    invalid_yaml = "invalid: yaml: content: with: invalid: syntax: {"
    reader = LocationReadCloser(
        location=new_location("invalid_podfile.lock"),
        read_closer=TextIOWrapper(BytesIO(invalid_yaml.encode())),
    )
    with patch(
        "labels.parsers.cataloger.swift.parse_podfile_lock.parse_yaml_with_tree_sitter",
        side_effect=ValueError("Invalid YAML"),
    ):
        pkgs, rels = parse_podfile_lock(None, None, reader)
        assert pkgs == []
        assert rels == []


@mocks(
    mocks=[
        Mock(
            module=parse_lock,
            target="process_pods",
            target_type="sync",
            expected=([], {}),
        ),
    ],
)
async def test_parse_podsfile_lock_no_packages() -> None:
    invalid_structure = """
PODS:
  - "Package1 (1.0.0)"
DEPENDENCIES:
  - "Package1"
SPEC CHECKSUMS:
  Package1: abc123
"""
    reader = LocationReadCloser(
        location=new_location("empty_podfile.lock"),
        read_closer=TextIOWrapper(BytesIO(invalid_structure.encode())),
    )
    pkgs, rels = parse_podfile_lock(None, None, reader)
    assert pkgs == []
    assert rels == []


@mocks(
    mocks=[
        Mock(
            module=parse_lock,
            target="parse_yaml_with_tree_sitter",
            target_type="sync",
            expected={},
        ),
    ],
)
async def test_parse_podsfile_lock_empty_podfile() -> None:
    empty_yaml = "{}"
    reader = LocationReadCloser(
        location=new_location("empty_podfile.lock"),
        read_closer=TextIOWrapper(BytesIO(empty_yaml.encode())),
    )
    pkgs, rels = parse_podfile_lock(None, None, reader)
    assert pkgs == []
    assert rels == []


@mocks(
    mocks=[
        Mock(
            module=parse_lock,
            target="parse_yaml_with_tree_sitter",
            target_type="sync",
            expected={"DEPENDENCIES": [], "SPEC CHECKSUMS": {}},
        ),
    ],
)
async def test_parse_podsfile_lock_no_pods_key() -> None:
    yaml_without_pods = """
DEPENDENCIES:
  - "Package1"
SPEC CHECKSUMS:
  Package1: abc123
"""
    reader = LocationReadCloser(
        location=new_location("no_pods_podfile.lock"),
        read_closer=TextIOWrapper(BytesIO(yaml_without_pods.encode())),
    )
    pkgs, rels = parse_podfile_lock(None, None, reader)
    assert pkgs == []
    assert rels == []


def test_parse_podsfile_lock_invalid_dependencies_type() -> None:
    yaml_with_invalid_types = """
PODS:
  - "Package1 (1.0.0)"
DEPENDENCIES: "not a list"
SPEC CHECKSUMS:
  Package1: abc123
"""
    reader = LocationReadCloser(
        location=new_location("invalid_types_podfile.lock"),
        read_closer=TextIOWrapper(BytesIO(yaml_with_invalid_types.encode())),
    )
    mock_node = MagicMock(spec=Node)
    mock_dict = IndexedDict[str, ParsedValue](mock_node)
    mock_pods = IndexedList[ParsedValue](mock_node)
    mock_pods.append(("Package1 (1.0.0)", mock_node))
    mock_dict[("PODS", mock_node)] = (mock_pods, mock_node)
    mock_dict[("DEPENDENCIES", mock_node)] = ("not a list", mock_node)
    mock_checksums = IndexedDict[str, ParsedValue](mock_node)
    mock_checksums[("Package1", mock_node)] = ("abc123", mock_node)
    mock_dict[("SPEC CHECKSUMS", mock_node)] = (mock_checksums, mock_node)
    with patch(
        "labels.parsers.cataloger.swift.parse_podfile_lock.parse_yaml_with_tree_sitter",
        return_value=mock_dict,
    ):
        pkgs, rels = parse_podfile_lock(None, None, reader)
        assert pkgs == []
        assert rels == []


@mocks(
    mocks=[
        Mock(
            module=parse_lock,
            target="extract_pod_info",
            target_type="sync",
            expected=("", ""),
        ),
    ],
)
async def test_parse_podsfile_lock_empty_pod_info() -> None:
    yaml_content = """
PODS:
  - "Package1 (1.0.0)"
DEPENDENCIES:
  - "Package1"
SPEC CHECKSUMS:
  Package1: abc123
"""
    reader = LocationReadCloser(
        location=new_location("empty_pod_info_podfile.lock"),
        read_closer=TextIOWrapper(BytesIO(yaml_content.encode())),
    )
    pkgs, rels = parse_podfile_lock(None, None, reader)
    assert pkgs == []
    assert rels == []


def test_parse_podsfile_lock_invalid_checksums_type() -> None:
    yaml_content = """
PODS:
  - "Package1 (1.0.0)"
DEPENDENCIES:
  - "Package1"
SPEC CHECKSUMS: not a dict
"""
    reader = LocationReadCloser(
        location=new_location("invalid_checksums_podfile.lock"),
        read_closer=TextIOWrapper(BytesIO(yaml_content.encode())),
    )
    mock_node = MagicMock(spec=Node)
    mock_dict = IndexedDict[str, ParsedValue](mock_node)
    mock_pods = IndexedList[ParsedValue](mock_node)
    mock_pods.append(("Package1 (1.0.0)", mock_node))
    mock_dict[("PODS", mock_node)] = (mock_pods, mock_node)
    mock_deps = IndexedList[ParsedValue](mock_node)
    mock_deps.append(("Package1", mock_node))
    mock_dict[("DEPENDENCIES", mock_node)] = (mock_deps, mock_node)
    mock_dict[("SPEC CHECKSUMS", mock_node)] = ("not a dict", mock_node)
    with patch(
        "labels.parsers.cataloger.swift.parse_podfile_lock.parse_yaml_with_tree_sitter",
        return_value=mock_dict,
    ):
        pkgs, rels = parse_podfile_lock(None, None, reader)
        assert pkgs == []
        assert rels == []


def test_parse_podsfile_lock_no_coordinates() -> None:
    yaml_content = """
PODS:
  - "Package1 (1.0.0)"
DEPENDENCIES:
  - "Package1"
SPEC CHECKSUMS:
  Package1: abc123
"""
    location = new_location("no_coordinates_podfile.lock")
    location.coordinates = None
    reader = LocationReadCloser(
        location=location,
        read_closer=TextIOWrapper(BytesIO(yaml_content.encode())),
    )
    mock_node = MagicMock(spec=Node)
    mock_dict = IndexedDict[str, ParsedValue](mock_node)
    mock_pods = IndexedList[ParsedValue](mock_node)
    mock_pods.append(("Package1 (1.0.0)", mock_node))
    mock_dict[("PODS", mock_node)] = (mock_pods, mock_node)
    mock_deps = IndexedList[ParsedValue](mock_node)
    mock_deps.append(("Package1", mock_node))
    mock_dict[("DEPENDENCIES", mock_node)] = (mock_deps, mock_node)
    mock_checksums = IndexedDict[str, ParsedValue](mock_node)
    mock_checksums[("Package1", mock_node)] = ("abc123", mock_node)
    mock_dict[("SPEC CHECKSUMS", mock_node)] = (mock_checksums, mock_node)
    with patch(
        "labels.parsers.cataloger.swift.parse_podfile_lock.parse_yaml_with_tree_sitter",
        return_value=mock_dict,
    ):
        pkgs, _ = parse_podfile_lock(None, None, reader)
        assert len(pkgs) == 1
        assert pkgs[0].locations[0] == location


def test_parse_podsfile_lock_no_package_created() -> None:
    yaml_content = """
PODS:
  - "Package1 (1.0.0)"
DEPENDENCIES:
  - "Package1"
SPEC CHECKSUMS:
  Package1: abc123
"""
    location = new_location("no_package_podfile.lock")
    reader = LocationReadCloser(
        location=location,
        read_closer=TextIOWrapper(BytesIO(yaml_content.encode())),
    )
    mock_node = MagicMock(spec=Node)
    mock_dict = IndexedDict[str, ParsedValue](mock_node)
    mock_pods = IndexedList[ParsedValue](mock_node)
    mock_pods.append(("Package1 (1.0.0)", mock_node))
    mock_dict[("PODS", mock_node)] = (mock_pods, mock_node)
    mock_deps = IndexedList[ParsedValue](mock_node)
    mock_deps.append(("Package1", mock_node))
    mock_dict[("DEPENDENCIES", mock_node)] = (mock_deps, mock_node)
    mock_checksums = IndexedDict[str, ParsedValue](mock_node)
    mock_checksums[("Package1", mock_node)] = ("abc123", mock_node)
    mock_dict[("SPEC CHECKSUMS", mock_node)] = (mock_checksums, mock_node)
    with (
        patch(
            "labels.parsers.cataloger.swift.parse_podfile_lock.parse_yaml_with_tree_sitter",
            return_value=mock_dict,
        ),
        patch(
            "labels.parsers.cataloger.swift.parse_podfile_lock.new_cocoa_pods_package",
            return_value=None,
        ),
    ):
        pkgs, rels = parse_podfile_lock(None, None, reader)
        assert pkgs == []
        assert rels == []


def test_parse_podsfile_lock_invalid_pod_type() -> None:
    yaml_content = """
PODS:
  - 123  # número inválido en lugar de string
DEPENDENCIES:
  - "Package1"
SPEC CHECKSUMS:
  Package1: abc123
"""
    location = new_location("invalid_pod_type_podfile.lock")
    reader = LocationReadCloser(
        location=location,
        read_closer=TextIOWrapper(BytesIO(yaml_content.encode())),
    )
    mock_node = MagicMock(spec=Node)
    mock_dict = IndexedDict[str, ParsedValue](mock_node)
    mock_pods = IndexedList[ParsedValue](mock_node)
    mock_pods.append((123, mock_node))

    mock_dict[("PODS", mock_node)] = (mock_pods, mock_node)
    mock_deps = IndexedList[ParsedValue](mock_node)
    mock_deps.append(("Package1", mock_node))
    mock_dict[("DEPENDENCIES", mock_node)] = (mock_deps, mock_node)
    mock_checksums = IndexedDict[str, ParsedValue](mock_node)
    mock_checksums[("Package1", mock_node)] = ("abc123", mock_node)
    mock_dict[("SPEC CHECKSUMS", mock_node)] = (mock_checksums, mock_node)
    with patch(
        "labels.parsers.cataloger.swift.parse_podfile_lock.parse_yaml_with_tree_sitter",
        return_value=mock_dict,
    ):
        pkgs, rels = parse_podfile_lock(None, None, reader)
        assert pkgs == []
        assert rels == []


def test_extract_pod_info_invalid_type() -> None:
    result = parse_lock.extract_pod_info(123)
    assert result == ("", "")


def test_extract_pod_info_string() -> None:
    result = parse_lock.extract_pod_info("Package1 (1.0.0)")
    assert result == ("Package1", "1.0.0")


def test_extract_pod_info_indexed_dict() -> None:
    mock_node = MagicMock(spec=Node)
    mock_dict = IndexedDict[str, ParsedValue](mock_node)
    mock_dict[("Package1 (1.0.0)", mock_node)] = ("value", mock_node)
    result = parse_lock.extract_pod_info(mock_dict)
    assert result == ("Package1", "1.0.0")
