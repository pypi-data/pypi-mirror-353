from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.java.model import JavaArchive, JavaPomProject
from labels.parsers.cataloger.java.parse_gradle import (
    LockFileDependency,
    avoid_cmt,
    build_regex_with_configs,
    create_packages,
    get_block_deps,
    is_comment,
    parse_gradle,
)
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_gradle() -> None:
    test_data_path = get_test_data_path("dependencies/java/gradle/build.gradle")
    expected_packages = [
        Package(
            name="org.yaml:snakeyaml",
            version="1.32",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=22,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="org.yaml",
                    artifact_id="org.yaml:snakeyaml",
                    version="1.32",
                    name="org.yaml:snakeyaml",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/org.yaml/org.yaml:snakeyaml@1.32",
        ),
        Package(
            name="io.springfox:springfox-swagger-ui",
            version="2.5.9",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=23,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="io.springfox",
                    artifact_id="io.springfox:springfox-swagger-ui",
                    version="2.5.9",
                    name="io.springfox:springfox-swagger-ui",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/io.springfox/io.springfox:springfox-swagger-ui@2.5.9",
        ),
        Package(
            name="io.springfox:springfox-swagger-ui",
            version="2.5.2",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=34,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="io.springfox",
                    artifact_id="io.springfox:springfox-swagger-ui",
                    version="2.5.2",
                    name="io.springfox:springfox-swagger-ui",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/io.springfox/io.springfox:springfox-swagger-ui@2.5.2",
        ),
        Package(
            name="io.springfox:springfox-swagger-ui",
            version="2.6.0",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=14,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="io.springfox",
                    artifact_id="io.springfox:springfox-swagger-ui",
                    version="2.6.0",
                    name="io.springfox:springfox-swagger-ui",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/io.springfox/io.springfox:springfox-swagger-ui@2.6.0",
        ),
        Package(
            name="io.springfox:springfox-swagger-ui",
            version="2.6.1",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=15,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="io.springfox",
                    artifact_id="io.springfox:springfox-swagger-ui",
                    version="2.6.1",
                    name="io.springfox:springfox-swagger-ui",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/io.springfox/io.springfox:springfox-swagger-ui@2.6.1",
        ),
        Package(
            name="org.apache.logging.log4j:log4j-core",
            version="2.13.2",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=18,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="org.apache.logging.log4j",
                    artifact_id="org.apache.logging.log4j:log4j-core",
                    version="2.13.2",
                    name="org.apache.logging.log4j:log4j-core",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/org.apache.logging.log4j/org.apache.logging.log4j:log4j-core@2.13.2",
        ),
        Package(
            name="org.json:json",
            version="20160810",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=19,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="org.json",
                    artifact_id="org.json:json",
                    version="20160810",
                    name="org.json:json",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/org.json/org.json:json@20160810",
        ),
        Package(
            name="javax.mail:mail",
            version="1.4",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=20,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="javax.mail",
                    artifact_id="javax.mail:mail",
                    version="1.4",
                    name="javax.mail:mail",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/javax.mail/javax.mail:mail@1.4",
        ),
        Package(
            name="io.springfox:springfox-swagger-ui",
            version="2.5.8",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=28,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="io.springfox",
                    artifact_id="io.springfox:springfox-swagger-ui",
                    version="2.5.8",
                    name="io.springfox:springfox-swagger-ui",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/io.springfox/io.springfox:springfox-swagger-ui@2.5.8",
        ),
        Package(
            name="io.springfox:springfox-swagger-ui",
            version="2.5.7",
            language=Language.JAVA,
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
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="io.springfox",
                    artifact_id="io.springfox:springfox-swagger-ui",
                    version="2.5.7",
                    name="io.springfox:springfox-swagger-ui",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/io.springfox/io.springfox:springfox-swagger-ui@2.5.7",
        ),
        Package(
            name="io.springfox:springfox-swagger-ui",
            version="2.5.6",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=30,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="io.springfox",
                    artifact_id="io.springfox:springfox-swagger-ui",
                    version="2.5.6",
                    name="io.springfox:springfox-swagger-ui",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/io.springfox/io.springfox:springfox-swagger-ui@2.5.6",
        ),
        Package(
            name="io.springfox:springfox-swagger-ui",
            version="2.5.5",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=31,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="io.springfox",
                    artifact_id="io.springfox:springfox-swagger-ui",
                    version="2.5.5",
                    name="io.springfox:springfox-swagger-ui",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/io.springfox/io.springfox:springfox-swagger-ui@2.5.5",
        ),
        Package(
            name="io.springfox:springfox-swagger-ui",
            version="2.5.4",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=32,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                ),
            ],
            type=PackageType.JavaPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="io.springfox",
                    artifact_id="io.springfox:springfox-swagger-ui",
                    version="2.5.4",
                    name="io.springfox:springfox-swagger-ui",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/io.springfox/io.springfox:springfox-swagger-ui@2.5.4",
        ),
    ]

    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, relations = parse_gradle(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        for rel in relations:
            rel.from_.health_metadata = None
            rel.from_.licenses = []
            rel.to_.health_metadata = None
            rel.to_.licenses = []
        assert pkgs == expected_packages


def test_is_comment() -> None:
    assert is_comment("// This is a comment")
    assert is_comment("  // This is a comment with spaces")
    assert is_comment("\t// This is a comment with tabulation")

    assert is_comment("/* This is a block comment */")
    assert is_comment("  /* This is a block comment with spaces */")
    assert is_comment("*/")

    assert not is_comment("This is not a comment")
    assert not is_comment("int x = 5; // This is a comment at the end")
    assert not is_comment("*/ This is the end of a block comment")
    assert not is_comment("")


def test_avoid_cmt_handles_single_line_comments() -> None:
    assert avoid_cmt("// This is a comment", is_block_cmt=False) == ("", False)
    assert avoid_cmt("code // This is a comment", is_block_cmt=False) == ("code ", False)
    assert avoid_cmt("  // This is a comment with spaces", is_block_cmt=False) == ("  ", False)


def test_avoid_cmt_handles_block_comments() -> None:
    assert avoid_cmt("/* This is a block comment */", is_block_cmt=False) == ("", False)
    assert avoid_cmt("code /* This is a block comment */", is_block_cmt=False) == ("code ", False)
    assert avoid_cmt("  /* This is a block comment with spaces */", is_block_cmt=False) == (
        "  ",
        False,
    )


def test_avoid_cmt_handles_nested_block_comments() -> None:
    assert avoid_cmt("/* This is a /* nested */ block comment */", is_block_cmt=False) == (
        " block comment */",
        False,
    )


def test_avoid_cmt_handles_unclosed_block_comments() -> None:
    assert avoid_cmt("/* This is an unclosed comment", is_block_cmt=False) == ("", True)
    assert avoid_cmt("code /* This is an unclosed comment", is_block_cmt=False) == ("code ", True)


def test_avoid_cmt_handles_block_comment_continuation() -> None:
    assert avoid_cmt("This is a continuation */", is_block_cmt=True) == ("", False)
    assert avoid_cmt("*/ This is the end", is_block_cmt=True) == (" This is the end", False)


def test_avoid_cmt_handles_mixed_comment_types() -> None:
    assert avoid_cmt("code /* comment */ more code", is_block_cmt=False) == (
        "code  more code",
        False,
    )
    assert avoid_cmt("code // line comment /* block comment */", is_block_cmt=False) == (
        "code ",
        False,
    )


def test_avoid_cmt_handles_content_inside_block_comments() -> None:
    assert avoid_cmt("This is inside a block comment", is_block_cmt=True) == ("", True)
    assert avoid_cmt("  This is inside a block comment with spaces", is_block_cmt=True) == (
        "",
        True,
    )
    assert avoid_cmt(
        "This is inside a block comment with /* nested */ comment",
        is_block_cmt=True,
    ) == (" comment", False)
    assert avoid_cmt("This is inside a block comment with // line comment", is_block_cmt=True) == (
        "",
        True,
    )


def test_get_block_deps_skips_blocks_without_version() -> None:
    content = """
    implementation("org.example:test") {
        // No version specified
    }
    """
    configs = {"implementation"}
    regexes = build_regex_with_configs(configs)
    dependencies = get_block_deps(content, regexes)
    assert len(dependencies) == 0


def test_get_block_deps_skips_blocks_with_empty_version() -> None:
    content = """
    implementation("org.example:test") {
        version {
            strictly("")
        }
    }
    implementation("org.example:test2") {
        version {
            strictly("1.0.0")
        }
    }
    """
    configs = {"implementation"}
    regexes = build_regex_with_configs(configs)
    dependencies = get_block_deps(content, regexes)
    assert len(dependencies) == 1
    assert dependencies[0].version == "1.0.0"
    assert dependencies[0].name == "org.example:test2"


def test_create_packages_skips_dependencies_with_empty_name_or_version() -> None:
    dependencies = [
        LockFileDependency(group="org.example", name="", version="1.0.0", line=1),
        LockFileDependency(group="org.example", name="test", version="", line=2),
        LockFileDependency(group="org.example", name="", version="", line=3),
        LockFileDependency(group="org.example", name="test", version="1.0.0", line=4),
    ]

    location = Location(
        scope=Scope.PROD,
        coordinates=Coordinates(
            real_path="test.gradle",
            file_system_id=None,
            line=None,
        ),
        access_path="test.gradle",
        annotations={},
        dependency_type=DependencyType.UNKNOWN,
    )

    packages = create_packages(dependencies, location)
    assert len(packages) == 1
    assert packages[0].name == "test"
    assert packages[0].version == "1.0.0"


def test_create_packages_handles_location_without_coordinates() -> None:
    dependencies = [
        LockFileDependency(group="org.example", name="test", version="1.0.0", line=42),
    ]

    location = Location(
        scope=Scope.PROD,
        coordinates=None,
        access_path="test.gradle",
        annotations={},
        dependency_type=DependencyType.UNKNOWN,
    )

    packages = create_packages(dependencies, location)
    assert len(packages) == 1
    assert packages[0].name == "test"
    assert packages[0].version == "1.0.0"
    assert packages[0].locations[0].coordinates is None


async def test_create_packages_handles_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    dependencies = [
        LockFileDependency(group="org.example", name="test", version="1.0.0", line=42),
    ]

    location = Location(
        scope=Scope.PROD,
        coordinates=Coordinates(
            real_path="test.gradle",
            file_system_id=None,
            line=None,
        ),
        access_path="test.gradle",
        annotations={},
        dependency_type=DependencyType.UNKNOWN,
    )

    with patch("labels.model.package.Package.__init__") as mock_init:
        mock_init.side_effect = ValidationError.from_exception_data(
            title="",
            line_errors=[
                InitErrorDetails(
                    type="missing",
                    loc=("name",),
                    input=None,
                    ctx={},
                ),
            ],
        )

        packages = create_packages(dependencies, location)
        assert len(packages) == 0
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )
