from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.graph_parser import Graph, NId
from labels.parsers.cataloger.swift import parse_package_swift as parse_package_swift_module
from labels.parsers.cataloger.swift.parse_package_swift import (
    create_package,
    extract_package_details,
    get_dependencies,
    parse_package_swift,
)
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_package_swift() -> None:
    test_data_path = get_test_data_path("dependencies/swift/Package.swift")
    expected_packages = [
        Package(
            name="vapor",
            version="4.50.0",
            language=Language.SWIFT,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=10,
                    ),
                    dependency_type=DependencyType.UNKNOWN,
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
            metadata=None,
            p_url="pkg:swift/%22github.com/vapor/vapor.git%22/vapor@4.50.0",
        ),
        Package(
            name="swift-argument-parser",
            version="1.3.0",
            language=Language.SWIFT,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=14,
                    ),
                    dependency_type=DependencyType.UNKNOWN,
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
            metadata=None,
            p_url="pkg:swift/%22github.com/apple/swift-argument-parser.git%22/swift-argument-parser@1.3.0",
        ),
        Package(
            name="swift-collections",
            version="1.1.0",
            language=Language.SWIFT,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=16,
                    ),
                    dependency_type=DependencyType.UNKNOWN,
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
            metadata=None,
            p_url="pkg:swift/%22github.com/apple/swift-collections.git%22/swift-collections@1.1.0",
        ),
        Package(
            name="swift-nio",
            version="2.41.0",
            language=Language.SWIFT,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=18,
                    ),
                    dependency_type=DependencyType.UNKNOWN,
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
            metadata=None,
            p_url="pkg:swift/%22github.com/apple/swift-nio%22/swift-nio@2.41.0",
        ),
        Package(
            name="Nimble",
            version="13.2.1",
            language=Language.SWIFT,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=19,
                    ),
                    dependency_type=DependencyType.UNKNOWN,
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
            metadata=None,
            p_url="pkg:swift/%22github.com/Quick/Nimble.git%22/Nimble@13.2.1",
        ),
    ]

    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, relationships = parse_package_swift(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        assert pkgs == expected_packages
        assert len(relationships) == 0


def test_extract_package_details_no_matching_conditions() -> None:
    graph = Graph()
    package_node = NId("1")
    argument_node = NId("2")
    name_node = NId("3")

    graph.add_node(package_node)
    graph.add_node(argument_node, label_type="value_argument", label_field_name=name_node)
    graph.add_node(name_node, label_text="other_field")

    with patch(
        "labels.parsers.cataloger.swift.parse_package_swift.adj",
        return_value=(argument_node,),
    ):
        package_name, package_version, source_url = extract_package_details(graph, package_node)

        assert package_name is None
        assert package_version is None
        assert source_url is None


@mocks(
    mocks=[
        Mock(
            module=parse_package_swift_module,
            target="adj",
            target_type="sync",
            expected=(NId("2"),),
        ),
        Mock(
            module=parse_package_swift_module,
            target="is_valid_package_node",
            target_type="sync",
            expected=True,
        ),
        Mock(
            module=parse_package_swift_module,
            target="extract_package_details",
            target_type="sync",
            expected=("test_package", "1.0.0", "https://github.com/test/package.git"),
        ),
        Mock(
            module=parse_package_swift_module,
            target="create_package",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_dependencies_no_matching_conditions() -> None:
    graph = Graph()
    dep_node = NId("1")
    package_node = NId("2")

    graph.add_node(dep_node)
    graph.add_node(package_node)

    location = Location(
        coordinates=Coordinates(
            real_path="./test.swift",
            file_system_id=None,
            line=1,
        ),
        dependency_type=DependencyType.UNKNOWN,
        access_path="./test.swift",
        annotations={},
    )

    reader = LocationReadCloser(
        location=location,
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    packages, relationships = get_dependencies(dep_node, graph, reader)

    assert packages == []
    assert relationships == []


def test_create_package_no_coordinates() -> None:
    graph = Graph()
    package_node = NId("1")
    graph.add_node(package_node, label_l=10)

    location = Location(
        coordinates=None,
        dependency_type=DependencyType.UNKNOWN,
        access_path="./test.swift",
        annotations={},
    )

    reader = LocationReadCloser(
        location=location,
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    package = create_package(
        graph=graph,
        package_node=package_node,
        package_name="test_package",
        package_version="1.0.0",
        source_url="https://github.com/test/package.git",
        reader=reader,
    )

    assert package is not None
    assert package.name == "test_package"
    assert package.version == "1.0.0"
    assert package.locations[0].coordinates is None


def test_parse_package_swift_empty_content() -> None:
    with patch(
        "labels.parsers.cataloger.swift.parse_package_swift.parse_ast_graph",
        return_value=None,
    ):
        reader = LocationReadCloser(
            location=Location(
                coordinates=Coordinates(
                    real_path="./test.swift",
                    file_system_id=None,
                    line=1,
                ),
                dependency_type=DependencyType.UNKNOWN,
                access_path="./test.swift",
                annotations={},
            ),
            read_closer=TextIOWrapper(BytesIO(b"")),
        )

        packages, relationships = parse_package_swift(None, None, reader)

        assert packages == []
        assert relationships == []


async def test_parse_package_swift_no_adj_children() -> None:
    def mock_adj(*args: object, **_kwargs: object) -> tuple[NId, ...] | None:
        if len(args) > 2 and args[2] == 2:
            return None
        return (NId("1"), NId("3"))

    graph = Graph()
    graph.add_node(NId("1"), label_type="call_expression", label_text="Package")
    graph.add_node(NId("2"), label_type="value_argument", label_field_name=NId("3"))
    graph.add_node(NId("3"), label_text="dependencies")

    with (
        patch(
            "labels.parsers.cataloger.swift.parse_package_swift.adj",
            side_effect=mock_adj,
        ),
        patch(
            "labels.parsers.cataloger.swift.parse_package_swift.parse_ast_graph",
            return_value=graph,
        ),
    ):
        reader = LocationReadCloser(
            location=Location(
                coordinates=Coordinates(
                    real_path="./test.swift",
                    file_system_id=None,
                    line=1,
                ),
                dependency_type=DependencyType.UNKNOWN,
                access_path="./test.swift",
                annotations={},
            ),
            read_closer=TextIOWrapper(
                BytesIO(b'let package = Package(name: "test", dependencies: [])'),
            ),
        )

        packages, relationships = parse_package_swift(None, None, reader)

        assert packages == []
        assert relationships == []
