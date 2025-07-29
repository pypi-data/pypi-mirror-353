import json
import os
import tempfile
from pathlib import Path

from defusedxml import ElementTree as DefusedET

from labels.model.core import OutputFormat, SbomConfig, SourceType
from labels.model.file import Coordinates, DependencyType, Location, Scope
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship, RelationshipType
from labels.output.dispatcher import dispatch_sbom_output, merge_packages
from labels.resolvers.directory import Directory
from labels.testing.utils.pytest_marks import parametrize_sync


def test_merge_packages() -> None:
    packages = [
        Package(
            name="pkg1",
            version="1.0",
            type=PackageType.NpmPkg,
            language=Language.JAVASCRIPT,
            locations=[
                Location(
                    coordinates=Coordinates(real_path="/path1"),
                    scope=Scope.PROD,
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            licenses=[],
            p_url="pkg:npm/pkg1@1.0",
            metadata={"id": "pkg1"},
        ),
        Package(
            name="pkg1",
            version="1.0",
            type=PackageType.NpmPkg,
            language=Language.JAVASCRIPT,
            locations=[
                Location(
                    coordinates=Coordinates(real_path="/path2"),
                    scope=Scope.PROD,
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            licenses=[],
            p_url="pkg:npm/pkg1@1.0",
            metadata={"id": "pkg1"},
        ),
        Package(
            name="pkg3",
            version="3.0",
            type=PackageType.NpmPkg,
            language=Language.JAVASCRIPT,
            locations=[
                Location(
                    coordinates=Coordinates(real_path="/path3"),
                    scope=Scope.PROD,
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            licenses=[],
            p_url="pkg:npm/pkg3@3.0",
            metadata={"id": "pkg3"},
        ),
        Package(
            name="pkg4",
            version="4.0",
            type=PackageType.NpmPkg,
            language=Language.JAVASCRIPT,
            locations=[
                Location(
                    coordinates=Coordinates(real_path="/path4"),
                    scope=Scope.PROD,
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            licenses=[],
            p_url="pkg:npm/pkg4@4.0",
        ),
    ]

    result = merge_packages(packages)

    assert len(result) == 3

    merged_pkg1 = next(
        p for p in result if isinstance(p.metadata, dict) and p.metadata.get("id") == "pkg1"
    )
    merged_paths = {loc.coordinates.real_path for loc in merged_pkg1.locations if loc.coordinates}
    assert merged_paths == {"/path1", "/path2"}

    pkg3_result = next(
        p for p in result if isinstance(p.metadata, dict) and p.metadata.get("id") == "pkg3"
    )
    assert [loc.coordinates.real_path for loc in pkg3_result.locations if loc.coordinates] == [
        "/path3",
    ]

    no_id_pkg = next(p for p in result if not p.metadata)
    assert [loc.coordinates.real_path for loc in no_id_pkg.locations if loc.coordinates] == [
        "/path4",
    ]


@parametrize_sync(
    args=["output_format"],
    cases=[
        [OutputFormat.FLUID_JSON],
        [OutputFormat.CYCLONEDX_JSON],
        [OutputFormat.CYCLONEDX_XML],
        [OutputFormat.SPDX_JSON],
        [OutputFormat.SPDX_XML],
    ],
)
def test_dispatch_sbom_output(
    output_format: OutputFormat,
) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        test_directory = "/test/dummy/path"
        output_path = os.path.join(temp_dir, "my_sbom")

        loc = Location(
            coordinates=Coordinates(
                real_path=str(Path(test_directory, "test", "file1.txt")),
                file_system_id="",
            ),
            access_path="test/file1.txt",
        )

        test_pkg = Package(
            name="test1",
            version="1.0.0",
            type=PackageType.NpmPkg,
            language=Language.JAVASCRIPT,
            locations=[loc],
            licenses=[],
            p_url="pkg:npm/test1@1.0.0",
            metadata={"id": "test1"},
            found_by="javascript-parse-package-json",
        )

        dep_pkg = Package(
            name="test2",
            version="2.0.0",
            type=PackageType.NpmPkg,
            language=Language.JAVASCRIPT,
            locations=[loc],
            licenses=[],
            p_url="pkg:npm/test2@2.0.0",
            metadata={"id": "test2"},
            found_by="javascript-parse-package-json",
        )

        relationships = [
            Relationship(
                from_=test_pkg,
                to_=dep_pkg,
                type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
            ),
        ]

        config = SbomConfig(
            source=test_directory,
            source_type=SourceType.DIRECTORY,
            execution_id="test-id",
            output_format=output_format,
            output=output_path,
            exclude=(),
            debug=False,
        )

        resolver = Directory(
            root=test_directory,
        )

        dispatch_sbom_output(
            packages=[test_pkg, dep_pkg],
            relationships=relationships,
            config=config,
            resolver=resolver,
        )

        extension = (
            ".json"
            if output_format
            in [
                OutputFormat.FLUID_JSON,
                OutputFormat.CYCLONEDX_JSON,
                OutputFormat.SPDX_JSON,
            ]
            else ".xml"
        )
        actual_output_path = f"{output_path}{extension}"

        assert Path(actual_output_path).exists()
        assert Path(actual_output_path).stat().st_size > 0

        if extension == ".json":
            with Path(actual_output_path).open() as f:
                json_content = json.loads(f.read())
                assert isinstance(json_content, dict)
        else:
            tree = DefusedET.parse(actual_output_path)
            root = tree.getroot()
            assert root is not None


def test_merge_packages_range_prefer_fixed_version() -> None:
    pkg_range = Package(
        name="pkgR",
        version=">=1.0.0,<2.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[
            Location(
                coordinates=Coordinates(real_path="/dir/package.json"),
                access_path="dir/package.json",
            ),
        ],
        licenses=[],
        p_url="pkg:npm/pkgR@1.0.0",
        metadata={"id": "pkgR_range"},
    )
    pkg_fixed = Package(
        name="pkgR",
        version="1.5.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[
            Location(
                coordinates=Coordinates(real_path="/dir/package-lock.json"),
                access_path="dir/package-lock.json",
            ),
        ],
        licenses=[],
        p_url="pkg:npm/pkgR@1.5.0",
        metadata={"id": "pkgR_fixed"},
    )

    result = merge_packages([pkg_range, pkg_fixed])

    assert len(result) == 1
    merged_pkg = result[0]
    assert merged_pkg.version == "1.5.0"
    merged_paths = {loc.coordinates.real_path for loc in merged_pkg.locations if loc.coordinates}
    assert merged_paths == {"/dir/package.json", "/dir/package-lock.json"}
    assert isinstance(merged_pkg.metadata, dict)
    assert merged_pkg.metadata.get("id") == "pkgR_fixed"


def test_merge_packages_with_shared_directories() -> None:
    pkg1 = Package(
        name="pkgShared",
        version="1.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[
            Location(
                coordinates=Coordinates(real_path="/shared/dir/package.json"),
                access_path="shared/dir/package.json",
            ),
        ],
        licenses=[],
        p_url="pkg:npm/pkgShared@1.0.0",
        metadata={"id": "pkgShared1"},
    )
    pkg2 = Package(
        name="pkgShared",
        version="1.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[
            Location(
                coordinates=Coordinates(real_path="/shared/dir/package-lock.json"),
                access_path="shared/dir/package-lock.json",
            ),
        ],
        licenses=[],
        p_url="pkg:npm/pkgShared@1.0.0",
        metadata={"id": "pkgShared2"},
    )

    result = merge_packages([pkg1, pkg2])

    assert len(result) == 1
    merged_pkg = result[0]
    merged_paths = {loc.coordinates.real_path for loc in merged_pkg.locations if loc.coordinates}
    assert merged_paths == {"/shared/dir/package.json", "/shared/dir/package-lock.json"}


def test_merge_packages_with_different_partent_directories() -> None:
    pkg1 = Package(
        name="pkgShared",
        version="1.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[
            Location(
                coordinates=Coordinates(real_path="/dir1/package.json"),
                access_path="dir1/package.json",
            ),
        ],
        licenses=[],
        p_url="pkg:npm/pkgShared@1.0.0",
        metadata={"id": "pkgShared1"},
    )
    pkg2 = Package(
        name="pkgShared",
        version=">=1.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[
            Location(
                coordinates=Coordinates(real_path="/dir2/package-lock.json"),
                access_path="dir2/package-lock.json",
            ),
        ],
        licenses=[],
        p_url="pkg:npm/pkgShared@1.0.0",
        metadata={"id": "pkgShared2"},
    )

    result = merge_packages([pkg1, pkg2])

    assert len(result) == 2


def test_merge_packages_with_non_lock_and_lock_files() -> None:
    pkg_same_dir = Package(
        name="pkgWithLock",
        version="1.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[
            Location(
                coordinates=Coordinates(real_path="/dir/package.json"),
                access_path="/dir/package.json",
                dependency_type=DependencyType.DIRECT,
                scope=Scope.PROD,
            ),
            Location(
                coordinates=Coordinates(real_path="/dir/package-lock.json"),
                access_path="/dir/package-lock.json",
                dependency_type=DependencyType.UNKNOWN,
            ),
        ],
        licenses=[],
        p_url="pkg:npm/pkgWithLock@1.0.0",
        metadata={"id": "pkgWithLock"},
    )

    pkg_different_dir = Package(
        name="pkgWithLock",
        version="1.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[
            Location(
                coordinates=Coordinates(real_path="/dir1/package.json"),
                access_path="/dir1/package.json",
                dependency_type=DependencyType.DIRECT,
                scope=Scope.PROD,
            ),
            Location(
                coordinates=Coordinates(real_path="/dir2/package-lock.json"),
                access_path="/dir2/package-lock.json",
                dependency_type=DependencyType.UNKNOWN,
            ),
        ],
        licenses=[],
        p_url="pkg:npm/pkgWithLock@1.0.0",
        metadata={"id": "pkgWithLockDifferentDir"},
    )

    result_same_dir = merge_packages([pkg_same_dir])
    assert len(result_same_dir) == 1
    updated_pkg_same_dir = result_same_dir[0]
    for loc in updated_pkg_same_dir.locations:
        assert loc.dependency_type == DependencyType.DIRECT
        assert loc.scope == Scope.PROD

    result_different_dir = merge_packages([pkg_different_dir])
    assert len(result_different_dir) == 1
    updated_pkg_different_dir = result_different_dir[0]
    assert len(updated_pkg_different_dir.locations) == 2
    for loc in updated_pkg_different_dir.locations:
        if loc.access_path == "package.json":
            assert loc.dependency_type == DependencyType.DIRECT
            assert loc.scope == Scope.PROD
        elif loc.access_path == "package-lock.json":
            assert loc.dependency_type == DependencyType.UNKNOWN


def test_merge_packages_with_version_range_and_fixed_version() -> None:
    pkg_range = Package(
        name="pkgVersionRange",
        version=">=1.0.0,<2.0.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[
            Location(
                coordinates=Coordinates(real_path="/dir/package.json"),
                access_path="dir/package.json",
            ),
        ],
        licenses=[],
        p_url="pkg:npm/pkgVersionRange@1.0.0",
        metadata={"id": "pkgRange"},
    )
    pkg_fixed = Package(
        name="pkgVersionRange",
        version="1.5.0",
        type=PackageType.NpmPkg,
        language=Language.JAVASCRIPT,
        locations=[
            Location(
                coordinates=Coordinates(real_path="/dir/package-lock.json"),
                access_path="dir/package-lock.json",
            ),
        ],
        licenses=[],
        p_url="pkg:npm/pkgVersionRange@1.5.0",
        metadata={"id": "pkgFixed"},
    )

    result = merge_packages([pkg_range, pkg_fixed])

    assert len(result) == 1
    merged_pkg = result[0]
    assert merged_pkg.version == "1.5.0"
    merged_paths = {loc.coordinates.real_path for loc in merged_pkg.locations if loc.coordinates}
    assert merged_paths == {"/dir/package.json", "/dir/package-lock.json"}
    assert isinstance(merged_pkg.metadata, dict)
    assert merged_pkg.metadata.get("id") == "pkgFixed"
