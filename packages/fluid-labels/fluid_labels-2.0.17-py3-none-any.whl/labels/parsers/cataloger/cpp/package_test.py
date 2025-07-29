from labels.model.file import Coordinates, DependencyType, Location, Scope
from labels.parsers.cataloger.cpp.package import (
    build_conan_file_location,
    build_conan_file_py_location,
    new_conan_file_py_dep,
)
from labels.parsers.cataloger.graph_parser import Graph


def test_new_conan_file_location() -> None:
    location = Location(
        coordinates=Coordinates(real_path="./", line=None),
    )

    new_location = build_conan_file_location(location=location, line_number=13, is_dev=False)
    assert new_location.scope == Scope.PROD
    assert new_location.coordinates
    assert new_location.coordinates.real_path == "./"
    assert new_location.coordinates.line == 13
    assert new_location.dependency_type == DependencyType.DIRECT


def test_new_conan_file_location_no_coordinates() -> None:
    location = Location(coordinates=None)

    new_location = build_conan_file_location(location=location, line_number=13, is_dev=False)
    assert new_location == location


def test_new_conan_file_py_location() -> None:
    location = Location(
        coordinates=Coordinates(real_path="./", line=None),
    )

    new_location = build_conan_file_py_location(location=location, sourceline=13, is_dev=False)
    assert new_location.coordinates
    assert new_location.scope == Scope.PROD
    assert new_location.coordinates.line == 13
    assert new_location.coordinates.real_path == "./"


def test_new_conan_file_py_location_no_coordinates() -> None:
    location = Location(coordinates=None)

    new_location = build_conan_file_py_location(location=location, sourceline=13, is_dev=False)
    assert new_location == location


def test_new_conan_file_py_dep_with_explicit_dep_info() -> None:
    graph = Graph()
    node_id = "1"
    graph.add_node(node_id, label_text="example/1.0", label_l=42)

    location = Location(coordinates=Coordinates(real_path="./", line=None))

    explicit_dep_info = "explicit_example/2.0"

    package = new_conan_file_py_dep(
        graph=graph,
        node_id=node_id,
        dep_info=explicit_dep_info,
        is_dev=False,
        location=location,
    )

    assert package.name == "explicit_example"
    assert package.version == "2.0"
    assert package.locations[0].coordinates is not None
    assert package.locations[0].coordinates.line == 42
    assert package.locations[0].scope == Scope.PROD
