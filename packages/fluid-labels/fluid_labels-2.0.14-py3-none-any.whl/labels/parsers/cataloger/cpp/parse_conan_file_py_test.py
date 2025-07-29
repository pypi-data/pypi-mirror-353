from io import BytesIO, TextIOWrapper
from pathlib import Path

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.cpp.parse_conan_file_py import parse_conan_file_py
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_conan_file() -> None:
    test_data_path = get_test_data_path("dependencies/cpp/conanfile.py")
    expected_packages = [
        Package(
            name="libde265",
            version="1.0.8",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=10,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:conan/libde265@1.0.8",
        ),
        Package(
            name="opencv",
            version="2.4.13.7",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=11,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:conan/opencv@2.4.13.7",
        ),
        Package(
            name="poco",
            version="1.10.1",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=12,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:conan/poco@1.10.1",
        ),
        Package(
            name="opencv",
            version="2.2",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=25,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:conan/opencv@2.2",
        ),
        Package(
            name="assimp",
            version="~5.1.0",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=26,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:conan/assimp@~5.1.0",
        ),
        Package(
            name="closecv",
            version="4.2",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=29,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:conan/closecv@4.2",
        ),
        Package(
            name="pkg_a",
            version="4.5.1",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.DEV,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=15,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
            metadata=None,
            p_url="pkg:conan/pkg_a@4.5.1",
        ),
        Package(
            name="libtiff",
            version="3.9.0",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.DEV,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=16,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
            metadata=None,
            p_url="pkg:conan/libtiff@3.9.0",
        ),
        Package(
            name="glew",
            version="2.1.0",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.DEV,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=17,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
            metadata=None,
            p_url="pkg:conan/glew@2.1.0",
        ),
        Package(
            name="tool_win",
            version="0.1",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.DEV,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=20,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
            metadata=None,
            p_url="pkg:conan/tool_win@0.1",
        ),
        Package(
            name="cairo",
            version="~0.17.0",
            language=Language.CPP,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.DEV,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=21,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.ConanPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=True,
            metadata=None,
            p_url="pkg:conan/cairo@~0.17.0",
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_conan_file_py(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        assert pkgs == expected_packages


def test_get_method_requirements_skips_non_requires_method() -> None:
    conan_content = """from conan import ConanFile

class MyConanFile(ConanFile):
    def requirements(self):
        self.requires("libde265/1.0.8")
        self.other_method("some/package@1.0.0")
"""

    reader = LocationReadCloser(
        location=new_location("conanfile.py"),
        read_closer=TextIOWrapper(BytesIO(conan_content.encode("utf-8"))),
    )

    pkgs, _ = parse_conan_file_py(None, None, reader)
    assert len(pkgs) == 1
    assert pkgs[0].name == "libde265"


def test_get_attr_requirements_handles_missing_value() -> None:
    conan_content = """from conan import ConanFile

class MyConanFile(ConanFile):
    requires = None
"""

    reader = LocationReadCloser(
        location=new_location("conanfile.py"),
        read_closer=TextIOWrapper(BytesIO(conan_content.encode("utf-8"))),
    )

    pkgs, _ = parse_conan_file_py(None, None, reader)
    assert len(pkgs) == 0


def test_get_attr_requirements_list() -> None:
    conan_content = """from conan import ConanFile

class MyConanFile(ConanFile):
    requires = ["libde265/1.0.8", "opencv/2.4.13.7"]
"""

    reader = LocationReadCloser(
        location=new_location("conanfile.py"),
        read_closer=TextIOWrapper(BytesIO(conan_content.encode("utf-8"))),
    )

    pkgs, _ = parse_conan_file_py(None, None, reader)
    assert len(pkgs) == 2
    assert pkgs[0].name == "libde265"
    assert pkgs[0].version == "1.0.8"
    assert pkgs[1].name == "opencv"
    assert pkgs[1].version == "2.4.13.7"


def test_get_attr_requirements_invalid() -> None:
    conan_content = """from conan import ConanFile

class MyConanFile(ConanFile):
    requires = None
"""

    reader = LocationReadCloser(
        location=new_location("conanfile.py"),
        read_closer=TextIOWrapper(BytesIO(conan_content.encode("utf-8"))),
    )

    pkgs, _ = parse_conan_file_py(None, None, reader)
    assert len(pkgs) == 0


def test_parse_conan_file_empty_content() -> None:
    reader = LocationReadCloser(
        location=new_location("conanfile.py"),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    pkgs, rels = parse_conan_file_py(None, None, reader)
    assert len(pkgs) == 0
    assert len(rels) == 0


def test_parse_conan_file_invalid_content() -> None:
    invalid_content = """from conan import ConanFile

class MyConanFile(ConanFile):
    requires = [
"""

    reader = LocationReadCloser(
        location=new_location("conanfile.py"),
        read_closer=TextIOWrapper(BytesIO(invalid_content.encode("utf-8"))),
    )

    pkgs, rels = parse_conan_file_py(None, None, reader)
    assert len(pkgs) == 0
    assert len(rels) == 0


def test_parse_conan_file_no_conan_class() -> None:
    invalid_content = """from conan import ConanFile

class MyClass:
    def __init__(self):
        self.requires = ["some/package@1.0.0"]
"""

    reader = LocationReadCloser(
        location=new_location("conanfile.py"),
        read_closer=TextIOWrapper(BytesIO(invalid_content.encode("utf-8"))),
    )

    pkgs, rels = parse_conan_file_py(None, None, reader)
    assert len(pkgs) == 0
    assert len(rels) == 0


def test_parse_conan_file_simple_requires() -> None:
    conan_content = """from conan import ConanFile

class HelloConan(ConanFile):
    requires = "fmt/9.1.0"
"""

    reader = LocationReadCloser(
        location=new_location("conanfile.py"),
        read_closer=TextIOWrapper(BytesIO(conan_content.encode("utf-8"))),
    )

    pkgs, _ = parse_conan_file_py(None, None, reader)
    assert len(pkgs) == 1
    assert pkgs[0].name == "fmt"
    assert pkgs[0].version == "9.1.0"
    assert not pkgs[0].is_dev


def test_get_attr_requirements_expression_list() -> None:
    conan_content = """from conan import ConanFile

class HelloConan(ConanFile):
    requires = "fmt/9.1.0", "libde265/1.0.8"
"""

    reader = LocationReadCloser(
        location=new_location("conanfile.py"),
        read_closer=TextIOWrapper(BytesIO(conan_content.encode("utf-8"))),
    )

    pkgs, _ = parse_conan_file_py(None, None, reader)
    assert len(pkgs) == 2
    assert pkgs[0].name == "fmt"
    assert pkgs[0].version == "9.1.0"
    assert not pkgs[0].is_dev
    assert pkgs[1].name == "libde265"
    assert pkgs[1].version == "1.0.8"
    assert not pkgs[1].is_dev
