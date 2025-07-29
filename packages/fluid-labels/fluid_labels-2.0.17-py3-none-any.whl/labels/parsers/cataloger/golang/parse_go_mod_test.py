from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.golang.parse_go_mod import (
    GolangModuleEntry,
    package_url,
    parse_go_mod,
    parse_go_sum_file,
    resolve_go_deps,
)
from labels.resolvers.directory import Directory
from labels.testing.utils.helpers import get_test_data_path
from labels.testing.utils.pytest_marks import parametrize_sync
from labels.utils.file import new_location


def test_parse_go_mod() -> None:
    test_data_path = get_test_data_path("dependencies/go/go-sum-hashes/go.mod")
    expected_packages = [
        Package(
            name="github.com/CycloneDX/cyclonedx-go",
            version="0.6.0",
            language=Language.GO,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=12,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.GoModulePkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:golang/github.com/CycloneDX/cyclonedx-go@0.6.0",
        ),
        Package(
            name="github.com/docker/docker",
            version="1.0.0",
            language=Language.GO,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=7,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.GoModulePkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:golang/github.com/docker/docker@1.0.0",
        ),
        Package(
            name="github.com/acarl005/stripansi",
            version="0.0.0-20180116102854-5a71ef0e047d",
            language=Language.GO,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=8,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.GoModulePkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=GolangModuleEntry(h1_digest="h1:licZJFw2RwpHMqeKTCYkitsPqHNxTmd4SNR5r94FGM8="),
            p_url=("pkg:golang/github.com/acarl005/stripansi@0.0.0-20180116102854-5a71ef0e047d"),
        ),
        Package(
            name="github.com/mgutz/ansi",
            version="0.0.0-20200706080929-d51e80ef957d",
            language=Language.GO,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=9,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.GoModulePkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=GolangModuleEntry(h1_digest="h1:5PJl274Y63IEHC+7izoQE9x6ikvDFZS2mDVS3drnohI="),
            p_url=("pkg:golang/github.com/mgutz/ansi@0.0.0-20200706080929-d51e80ef957d"),
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_go_mod(
            Directory(root="test/data/dependencies/go/go-sum-hashes", exclude=()),
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        assert pkgs == expected_packages


def test_parse_go_sum_file_with_invalid_inputs() -> None:
    reader = LocationReadCloser(
        location=Location(
            coordinates=Coordinates(
                real_path="test/path/go.mod",
                file_system_id=None,
                line=1,
            ),
            dependency_type=DependencyType.DIRECT,
            access_path="test/path/go.mod",
            annotations={},
        ),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )
    assert parse_go_sum_file(None, reader) is None

    reader = LocationReadCloser(
        location=Location(
            coordinates=None,
            dependency_type=DependencyType.DIRECT,
            access_path="test/path/go.mod",
            annotations={},
        ),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )
    assert parse_go_sum_file(Directory(root="test", exclude=()), reader) is None


def test_parse_go_sum_file_with_missing_sum_file() -> None:
    test_data_path = "./go.mod"
    reader = LocationReadCloser(
        location=Location(
            coordinates=Coordinates(
                real_path=test_data_path,
                file_system_id=None,
                line=1,
            ),
            dependency_type=DependencyType.DIRECT,
            access_path=test_data_path,
            annotations={},
        ),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )
    resolver = Directory(root="test/data/dependencies/go", exclude=())
    assert parse_go_sum_file(resolver, reader) is None


def test_parse_go_sum_file_with_os_error() -> None:
    test_data_path = "./go.mod"
    reader = LocationReadCloser(
        location=Location(
            coordinates=Coordinates(
                real_path=test_data_path,
                file_system_id=None,
                line=1,
            ),
            dependency_type=DependencyType.DIRECT,
            access_path=test_data_path,
            annotations={},
        ),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    resolver = Directory(root="test/data/dependencies/go/go-sum-hashes", exclude=())

    with patch.object(resolver, "file_contents_by_location", side_effect=OSError):
        assert parse_go_sum_file(resolver, reader) is None


def test_parse_go_sum_file_with_no_contents() -> None:
    test_data_path = "./go.mod"
    reader = LocationReadCloser(
        location=Location(
            coordinates=Coordinates(
                real_path=test_data_path,
                file_system_id=None,
                line=1,
            ),
            dependency_type=DependencyType.DIRECT,
            access_path=test_data_path,
            annotations={},
        ),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    resolver = Directory(root="test/data/dependencies/go/go-sum-hashes", exclude=())

    with patch.object(resolver, "file_contents_by_location", return_value=None):
        assert parse_go_sum_file(resolver, reader) is None


def test_parse_go_sum_file_with_no_sum_location() -> None:
    test_data_path = "./go.mod"
    reader = LocationReadCloser(
        location=Location(
            coordinates=Coordinates(
                real_path=test_data_path,
                file_system_id=None,
                line=1,
            ),
            dependency_type=DependencyType.DIRECT,
            access_path=test_data_path,
            annotations={},
        ),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    resolver = Directory(root="test/data/dependencies/go/go-sum-hashes", exclude=())

    with patch.object(resolver, "relative_file_path", return_value=None):
        assert parse_go_sum_file(resolver, reader) is None


def test_parse_go_sum_file_with_invalid_line() -> None:
    test_data_path = "./go.mod"
    reader = LocationReadCloser(
        location=Location(
            coordinates=Coordinates(
                real_path=test_data_path,
                file_system_id=None,
                line=1,
            ),
            dependency_type=DependencyType.DIRECT,
            access_path=test_data_path,
            annotations={},
        ),
        read_closer=TextIOWrapper(BytesIO(b"")),
    )

    resolver = Directory(root="test/data/dependencies/go/go-sum-hashes", exclude=())

    mock_contents = TextIOWrapper(BytesIO(b"invalid_line\nvalid_package v1.0.0 h1:hash123"))

    with patch.object(resolver, "file_contents_by_location", return_value=mock_contents):
        result = parse_go_sum_file(resolver, reader)
        assert result is not None
        assert "valid_package v1.0.0" in result
        assert result["valid_package v1.0.0"] == "h1:hash123"
        assert len(result) == 1


@parametrize_sync(
    args=["module_name", "module_version", "expected"],
    cases=[
        ["", "1.0.0", ""],
        ["package", "1.0.0", "pkg:golang/package@1.0.0"],
        ["github.com/user", "1.0.0", "pkg:golang/github.com/user@1.0.0"],
        ["github.com/user/package", "1.0.0", "pkg:golang/github.com/user/package@1.0.0"],
        [
            "github.com/user/package/sub/dir",
            "1.0.0",
            "pkg:golang/github.com/user/package@1.0.0#sub/dir",
        ],
    ],
)
def test_package_url(module_name: str, module_version: str, expected: str) -> None:
    assert package_url(module_name, module_version) == expected


def test_add_require_without_coordinates() -> None:
    test_data_path = "./go.mod"
    reader = LocationReadCloser(
        location=Location(
            coordinates=None,
            dependency_type=DependencyType.DIRECT,
            access_path=test_data_path,
            annotations={},
        ),
        read_closer=TextIOWrapper(
            BytesIO(b"module test\n\ngo 1.18\n\nrequire github.com/test/package v1.0.0"),
        ),
    )

    resolver = Directory(root="test/data/dependencies/go/go-sum-hashes", exclude=())

    packages, _ = parse_go_mod(resolver, None, reader)
    assert len(packages) == 1
    package = packages[0]
    assert package.name == "github.com/test/package"
    assert package.version == "1.0.0"
    assert package.locations[0].coordinates is None


def test_replace_nonexistent_package() -> None:
    test_data_path = "./go.mod"
    reader = LocationReadCloser(
        location=Location(
            coordinates=Coordinates(
                real_path=test_data_path,
                file_system_id=None,
                line=1,
            ),
            dependency_type=DependencyType.DIRECT,
            access_path=test_data_path,
            annotations={},
        ),
        read_closer=TextIOWrapper(
            BytesIO(
                b"module test\n\ngo 1.18\n\n"
                b"require github.com/existing/package v1.0.0\n"
                b"replace github.com/nonexistent/package => github.com/new/package v2.0.0",
            ),
        ),
    )

    resolver = Directory(root="test/data/dependencies/go/go-sum-hashes", exclude=())

    packages, _ = parse_go_mod(resolver, None, reader)
    assert len(packages) == 1
    package = packages[0]
    assert package.name == "github.com/existing/package"
    assert package.version == "1.0.0"


def test_replace_without_new_version() -> None:
    test_data_path = "./go.mod"
    reader = LocationReadCloser(
        location=Location(
            coordinates=Coordinates(
                real_path=test_data_path,
                file_system_id=None,
                line=1,
            ),
            dependency_type=DependencyType.DIRECT,
            access_path=test_data_path,
            annotations={},
        ),
        read_closer=TextIOWrapper(
            BytesIO(
                b"module test\n\ngo 1.18\n\n"
                b"require github.com/old/package v1.0.0\n"
                b"replace github.com/old/package v1.0.0 => github.com/new/package",
            ),
        ),
    )

    resolver = Directory(root="test/data/dependencies/go/go-sum-hashes", exclude=())

    packages, _ = parse_go_mod(resolver, None, reader)
    assert len(packages) == 1
    package = packages[0]
    assert package.name == "github.com/new/package"
    assert package.version == "1.0.0"


def test_replace_with_version_mismatch() -> None:
    test_data_path = "./go.mod"
    reader = LocationReadCloser(
        location=Location(
            coordinates=Coordinates(
                real_path=test_data_path,
                file_system_id=None,
                line=1,
            ),
            dependency_type=DependencyType.DIRECT,
            access_path=test_data_path,
            annotations={},
        ),
        read_closer=TextIOWrapper(
            BytesIO(
                b"module test\n\ngo 1.18\n\n"
                b"require github.com/old/package v1.0.0\n"
                b"replace github.com/old/package v2.0.0 => github.com/new/package v3.0.0",
            ),
        ),
    )

    resolver = Directory(root="test/data/dependencies/go/go-sum-hashes", exclude=())

    packages, _ = parse_go_mod(resolver, None, reader)
    assert len(packages) == 1
    package = packages[0]
    assert package.name == "github.com/old/package"
    assert package.version == "1.0.0"


def test_replace_without_coordinates() -> None:
    test_data_path = "./go.mod"
    reader = LocationReadCloser(
        location=Location(
            coordinates=None,
            dependency_type=DependencyType.DIRECT,
            access_path=test_data_path,
            annotations={},
        ),
        read_closer=TextIOWrapper(
            BytesIO(
                b"module test\n\ngo 1.18\n\n"
                b"require github.com/old/package v1.0.0\n"
                b"replace github.com/old/package v1.0.0 => github.com/new/package v2.0.0",
            ),
        ),
    )

    resolver = Directory(root="test/data/dependencies/go/go-sum-hashes", exclude=())

    packages, _ = parse_go_mod(resolver, None, reader)
    assert len(packages) == 1
    package = packages[0]
    assert package.name == "github.com/new/package"
    assert package.version == "2.0.0"
    assert package.locations[0].coordinates is None


def test_replace_directive_reset() -> None:
    test_data_path = "./go.mod"
    location = Location(
        coordinates=Coordinates(
            real_path=test_data_path,
            file_system_id=None,
            line=1,
        ),
        dependency_type=DependencyType.DIRECT,
        access_path=test_data_path,
        annotations={},
    )

    content = (
        "module test\n\n"
        "go 1.18\n\n"
        "require (\n"
        "    github.com/old/package v1.0.0\n"
        ")\n"
        "replace (\n"
        "    github.com/old/package => github.com/new/package v2.0.0\n"
        ")\n"
        "require github.com/another/package v1.0.0\n"
    )

    packages = list(resolve_go_deps(content, location, None))
    assert len(packages) == 2
    package_names = {pkg.name for pkg in packages}
    assert "github.com/new/package" in package_names
    assert "github.com/another/package" in package_names


def test_parse_go_mod_without_version() -> None:
    test_data_path = "./go.mod"
    reader = LocationReadCloser(
        location=Location(
            coordinates=Coordinates(
                real_path=test_data_path,
                file_system_id=None,
                line=1,
            ),
            dependency_type=DependencyType.DIRECT,
            access_path=test_data_path,
            annotations={},
        ),
        read_closer=TextIOWrapper(
            BytesIO(
                b"module test\n\n" b"require github.com/test/package v1.0.0\n",
            ),
        ),
    )

    resolver = Directory(root="test/data/dependencies/go/go-sum-hashes", exclude=())

    packages, relationships = parse_go_mod(resolver, None, reader)
    assert len(packages) == 0
    assert len(relationships) == 0


def test_parse_go_mod_old_version() -> None:
    test_data_path = "./go.mod"
    reader = LocationReadCloser(
        location=Location(
            coordinates=Coordinates(
                real_path=test_data_path,
                file_system_id=None,
                line=1,
            ),
            dependency_type=DependencyType.DIRECT,
            access_path=test_data_path,
            annotations={},
        ),
        read_closer=TextIOWrapper(
            BytesIO(
                b"module test\n\n" b"go 1.16\n\n" b"require github.com/test/package v1.0.0\n",
            ),
        ),
    )

    resolver = Directory(root="test/data/dependencies/go/go-sum-hashes", exclude=())

    packages, relationships = parse_go_mod(resolver, None, reader)
    assert len(packages) == 0
    assert len(relationships) == 0
