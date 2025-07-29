import logging
from io import BytesIO, StringIO, TextIOWrapper
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup, Tag
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

import labels.parsers.cataloger.java.maven_repo_utils
from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.resolver import Resolver
from labels.parsers.cataloger.java.model import (
    JavaArchive,
    JavaPomParent,
    JavaPomProperties,
    PomContext,
)
from labels.parsers.cataloger.java.parse_pom_xml import (
    _add_properties_vars,
    _evaluate_pom_files_in_project,
    _get_deps_management,
    _get_text,
    _is_module_parent,
    _is_parent_pom,
    decode_pom_xml,
    extract_bracketed_text,
    get_pom_project,
    new_package_from_pom_xml,
    parse_pom_xml,
    parse_pom_xml_project,
    pom_parent,
    resolve_managed_version,
    resolve_parent_version,
    resolve_property_version,
    update_location_with_dependency_info,
)
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.helpers import get_test_data_path
from labels.testing.utils.pytest_marks import parametrize_sync
from labels.utils.file import new_location

POM_XML = get_test_data_path("dependencies/java/pom/pom.xml")
COMMONS_TEXT_POM_XML = get_test_data_path("dependencies/java/pom/commons-text.pom.xml")

LOGGER = logging.getLogger(__name__)


@parametrize_sync(
    args=["test_data_path", "expected"],
    cases=[
        [
            POM_XML,
            [
                Package(
                    name="joda-time:joda-time",
                    version="2.9.2",
                    locations=[
                        Location(
                            coordinates=Coordinates(
                                real_path=POM_XML,
                                file_system_id=None,
                                line=20,
                            ),
                            dependency_type=DependencyType.DIRECT,
                            access_path=POM_XML,
                            annotations={},
                        ),
                    ],
                    language=Language.JAVA,
                    licenses=[],
                    type=PackageType.JavaPkg,
                    metadata=JavaArchive(
                        virtual_path=None,
                        manifest=None,
                        pom_properties=JavaPomProperties(
                            name=None,
                            group_id="joda-time",
                            artifact_id="joda-time",
                            version="2.9.2",
                            path=None,
                            scope=None,
                            extra={},
                        ),
                        pom_project=None,
                        archive_digests=[],
                        parent=None,
                    ),
                    p_url="pkg:maven/joda-time/joda-time@2.9.2",
                    dependencies=None,
                    found_by=None,
                    health_metadata=None,
                ),
                Package(
                    name="junit:junit",
                    version="4.12",
                    locations=[
                        Location(
                            coordinates=Coordinates(
                                real_path=POM_XML,
                                file_system_id=None,
                                line=27,
                            ),
                            dependency_type=DependencyType.DIRECT,
                            access_path=POM_XML,
                            annotations={},
                        ),
                    ],
                    language=Language.JAVA,
                    licenses=[],
                    type=PackageType.JavaPkg,
                    metadata=JavaArchive(
                        virtual_path=None,
                        manifest=None,
                        pom_properties=JavaPomProperties(
                            name=None,
                            group_id="junit",
                            artifact_id="junit",
                            version="4.12",
                            path=None,
                            scope=None,
                            extra={},
                        ),
                        pom_project=None,
                        archive_digests=[],
                        parent=None,
                    ),
                    p_url="pkg:maven/junit/junit@4.12",
                    dependencies=None,
                    found_by=None,
                    health_metadata=None,
                ),
            ],
        ],
        [
            COMMONS_TEXT_POM_XML,
            [
                Package(
                    name="org.apache.commons:commons-lang3",
                    version="3.12.0",
                    locations=[
                        Location(
                            coordinates=Coordinates(
                                real_path=COMMONS_TEXT_POM_XML,
                                file_system_id=None,
                                line=91,
                            ),
                            dependency_type=DependencyType.DIRECT,
                            access_path=COMMONS_TEXT_POM_XML,
                            annotations={},
                        ),
                    ],
                    language=Language.JAVA,
                    licenses=[],
                    type=PackageType.JavaPkg,
                    metadata=JavaArchive(
                        virtual_path=None,
                        manifest=None,
                        pom_properties=JavaPomProperties(
                            name=None,
                            group_id="org.apache.commons",
                            artifact_id="commons-lang3",
                            version="3.12.0",
                            path=None,
                            scope=None,
                            extra={},
                        ),
                        pom_project=None,
                        archive_digests=[],
                        parent=None,
                    ),
                    p_url="pkg:maven/org.apache.commons/commons-lang3@3.12.0",
                    dependencies=None,
                    found_by=None,
                    health_metadata=None,
                ),
                Package(
                    name="org.junit.jupiter:junit-jupiter",
                    version="3.0.0",
                    locations=[
                        Location(
                            coordinates=Coordinates(
                                real_path=COMMONS_TEXT_POM_XML,
                                file_system_id=None,
                                line=97,
                            ),
                            dependency_type=DependencyType.DIRECT,
                            access_path=COMMONS_TEXT_POM_XML,
                            annotations={},
                        ),
                    ],
                    language=Language.JAVA,
                    licenses=[],
                    type=PackageType.JavaPkg,
                    metadata=JavaArchive(
                        virtual_path=None,
                        manifest=None,
                        pom_properties=JavaPomProperties(
                            name=None,
                            group_id="org.junit.jupiter",
                            artifact_id="junit-jupiter",
                            version="3.0.0",
                            path=None,
                            scope=None,
                            extra={},
                        ),
                        pom_project=None,
                        archive_digests=[],
                        parent=None,
                    ),
                    p_url="pkg:maven/org.junit.jupiter/junit-jupiter@3.0.0",
                    dependencies=None,
                    found_by=None,
                    health_metadata=None,
                ),
                Package(
                    name="org.assertj:assertj-core",
                    version="3.23.1",
                    locations=[
                        Location(
                            coordinates=Coordinates(
                                real_path=COMMONS_TEXT_POM_XML,
                                file_system_id=None,
                                line=103,
                            ),
                            dependency_type=DependencyType.DIRECT,
                            access_path=COMMONS_TEXT_POM_XML,
                            annotations={},
                        ),
                    ],
                    language=Language.JAVA,
                    licenses=[],
                    type=PackageType.JavaPkg,
                    metadata=JavaArchive(
                        virtual_path=None,
                        manifest=None,
                        pom_properties=JavaPomProperties(
                            name=None,
                            group_id="org.assertj",
                            artifact_id="assertj-core",
                            version="3.23.1",
                            path=None,
                            scope=None,
                            extra={},
                        ),
                        pom_project=None,
                        archive_digests=[],
                        parent=None,
                    ),
                    p_url="pkg:maven/org.assertj/assertj-core@3.23.1",
                    dependencies=None,
                    found_by=None,
                    health_metadata=None,
                ),
                Package(
                    name="commons-io:commons-io",
                    version="2.11.0",
                    locations=[
                        Location(
                            coordinates=Coordinates(
                                real_path=COMMONS_TEXT_POM_XML,
                                file_system_id=None,
                                line=109,
                            ),
                            dependency_type=DependencyType.DIRECT,
                            access_path=COMMONS_TEXT_POM_XML,
                            annotations={},
                        ),
                    ],
                    language=Language.JAVA,
                    licenses=[],
                    type=PackageType.JavaPkg,
                    metadata=JavaArchive(
                        virtual_path=None,
                        manifest=None,
                        pom_properties=JavaPomProperties(
                            name=None,
                            group_id="commons-io",
                            artifact_id="commons-io",
                            version="2.11.0",
                            path=None,
                            scope=None,
                            extra={},
                        ),
                        pom_project=None,
                        archive_digests=[],
                        parent=None,
                    ),
                    p_url="pkg:maven/commons-io/commons-io@2.11.0",
                    dependencies=None,
                    found_by=None,
                    health_metadata=None,
                ),
                Package(
                    name="org.mockito:mockito-inline",
                    version="4.8.0",
                    locations=[
                        Location(
                            coordinates=Coordinates(
                                real_path=COMMONS_TEXT_POM_XML,
                                file_system_id=None,
                                line=116,
                            ),
                            dependency_type=DependencyType.DIRECT,
                            access_path=COMMONS_TEXT_POM_XML,
                            annotations={},
                        ),
                    ],
                    language=Language.JAVA,
                    licenses=[],
                    type=PackageType.JavaPkg,
                    metadata=JavaArchive(
                        virtual_path=None,
                        manifest=None,
                        pom_properties=JavaPomProperties(
                            name=None,
                            group_id="org.mockito",
                            artifact_id="mockito-inline",
                            version="${commons.mockito.version}",
                            path=None,
                            scope=None,
                            extra={},
                        ),
                        pom_project=None,
                        archive_digests=[],
                        parent=None,
                    ),
                    p_url="pkg:maven/org.mockito/mockito-inline@4.8.0",
                    dependencies=None,
                    found_by=None,
                    health_metadata=None,
                ),
                Package(
                    name="org.graalvm.js:js",
                    version="22.0.0.2",
                    locations=[
                        Location(
                            coordinates=Coordinates(
                                real_path=COMMONS_TEXT_POM_XML,
                                file_system_id=None,
                                line=122,
                            ),
                            dependency_type=DependencyType.DIRECT,
                            access_path=COMMONS_TEXT_POM_XML,
                            annotations={},
                        ),
                    ],
                    language=Language.JAVA,
                    licenses=[],
                    type=PackageType.JavaPkg,
                    metadata=JavaArchive(
                        virtual_path=None,
                        manifest=None,
                        pom_properties=JavaPomProperties(
                            name=None,
                            group_id="org.graalvm.js",
                            artifact_id="js",
                            version="${graalvm.version}",
                            path=None,
                            scope=None,
                            extra={},
                        ),
                        pom_project=None,
                        archive_digests=[],
                        parent=None,
                    ),
                    p_url="pkg:maven/org.graalvm.js/js@22.0.0.2",
                    dependencies=None,
                    found_by=None,
                    health_metadata=None,
                ),
                Package(
                    name="org.graalvm.js:js-scriptengine",
                    version="22.0.0.2",
                    locations=[
                        Location(
                            coordinates=Coordinates(
                                real_path=COMMONS_TEXT_POM_XML,
                                file_system_id=None,
                                line=128,
                            ),
                            dependency_type=DependencyType.DIRECT,
                            access_path=COMMONS_TEXT_POM_XML,
                            annotations={},
                        ),
                    ],
                    language=Language.JAVA,
                    licenses=[],
                    type=PackageType.JavaPkg,
                    metadata=JavaArchive(
                        virtual_path=None,
                        manifest=None,
                        pom_properties=JavaPomProperties(
                            name=None,
                            group_id="org.graalvm.js",
                            artifact_id="js-scriptengine",
                            version="${graalvm.version}",
                            path=None,
                            scope=None,
                            extra={},
                        ),
                        pom_project=None,
                        archive_digests=[],
                        parent=None,
                    ),
                    p_url="pkg:maven/org.graalvm.js/js-scriptengine@22.0.0.2",
                    dependencies=None,
                    found_by=None,
                    health_metadata=None,
                ),
                Package(
                    name="org.apache.commons:commons-rng-simple",
                    version="1.4",
                    locations=[
                        Location(
                            coordinates=Coordinates(
                                real_path=COMMONS_TEXT_POM_XML,
                                file_system_id=None,
                                line=134,
                            ),
                            dependency_type=DependencyType.DIRECT,
                            access_path=COMMONS_TEXT_POM_XML,
                            annotations={},
                        ),
                    ],
                    language=Language.JAVA,
                    licenses=[],
                    type=PackageType.JavaPkg,
                    metadata=JavaArchive(
                        virtual_path=None,
                        manifest=None,
                        pom_properties=JavaPomProperties(
                            name=None,
                            group_id="org.apache.commons",
                            artifact_id="commons-rng-simple",
                            version="${commons.rng.version}",
                            path=None,
                            scope=None,
                            extra={},
                        ),
                        pom_project=None,
                        archive_digests=[],
                        parent=None,
                    ),
                    p_url=("pkg:maven/org.apache.commons/commons-rng-simple@1.4"),
                    dependencies=None,
                    found_by=None,
                    health_metadata=None,
                ),
                Package(
                    name="org.openjdk.jmh:jmh-core",
                    version="1.35",
                    locations=[
                        Location(
                            coordinates=Coordinates(
                                real_path=COMMONS_TEXT_POM_XML,
                                file_system_id=None,
                                line=140,
                            ),
                            dependency_type=DependencyType.DIRECT,
                            access_path=COMMONS_TEXT_POM_XML,
                            annotations={},
                        ),
                    ],
                    language=Language.JAVA,
                    licenses=[],
                    type=PackageType.JavaPkg,
                    metadata=JavaArchive(
                        virtual_path=None,
                        manifest=None,
                        pom_properties=JavaPomProperties(
                            name=None,
                            group_id="org.openjdk.jmh",
                            artifact_id="jmh-core",
                            version="${jmh.version}",
                            path=None,
                            scope=None,
                            extra={},
                        ),
                        pom_project=None,
                        archive_digests=[],
                        parent=None,
                    ),
                    p_url="pkg:maven/org.openjdk.jmh/jmh-core@1.35",
                    dependencies=None,
                    found_by=None,
                    health_metadata=None,
                ),
                Package(
                    name="org.openjdk.jmh:jmh-generator-annprocess",
                    version="1.35",
                    locations=[
                        Location(
                            coordinates=Coordinates(
                                real_path=COMMONS_TEXT_POM_XML,
                                file_system_id=None,
                                line=146,
                            ),
                            dependency_type=DependencyType.DIRECT,
                            access_path=COMMONS_TEXT_POM_XML,
                            annotations={},
                        ),
                    ],
                    language=Language.JAVA,
                    licenses=[],
                    type=PackageType.JavaPkg,
                    metadata=JavaArchive(
                        virtual_path=None,
                        manifest=None,
                        pom_properties=JavaPomProperties(
                            name=None,
                            group_id="org.openjdk.jmh",
                            artifact_id="jmh-generator-annprocess",
                            version="${jmh.version}",
                            path=None,
                            scope=None,
                            extra={},
                        ),
                        pom_project=None,
                        archive_digests=[],
                        parent=None,
                    ),
                    p_url=("pkg:maven/org.openjdk.jmh/jmh-generator-annprocess@1.35"),
                    dependencies=None,
                    found_by=None,
                    health_metadata=None,
                ),
            ],
        ],
    ],
)
def test_parse_pom_xml(
    test_data_path: str,
    expected: list[Package],
) -> None:
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_pom_xml(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        assert pkgs == expected


@parametrize_sync(
    args=["pom_content", "expected_result"],
    cases=[
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <groupId>test.group</groupId>
                <artifactId>test-artifact</artifactId>
                <version>1.0.0</version>
            </project>""",
            True,
        ],
        [
            "<invalid>",
            False,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <root>
                <someElement>value</someElement>
            </root>
            """,
            False,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://wrong.namespace">
                <groupId>test.group</groupId>
                <artifactId>test-artifact</artifactId>
                <version>1.0.0</version>
            </project>
            """,
            False,
        ],
    ],
)
def test_get_pom_project_valid_xml(pom_content: str, expected_result: bool) -> None:  # noqa: FBT001
    result = get_pom_project(StringIO(pom_content))
    if expected_result:
        assert result is not None
        assert result.name == "project"
        assert result.get("xmlns") == "http://maven.apache.org/POM/4.0.0"
    else:
        assert result is None


def test_get_pom_project_valid_content() -> None:
    valid_pom = BytesIO(b"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>test.group</groupId>
    <artifactId>test-artifact</artifactId>
    <version>1.0.0</version>
</project>""")

    result = get_pom_project(TextIOWrapper(valid_pom))

    assert result is not None
    assert result.name == "project"
    assert result.get("xmlns") == "http://maven.apache.org/POM/4.0.0"

    group_id = result.find("groupid")
    assert group_id is not None
    assert group_id.get_text() == "test.group"

    artifact_id = result.find("artifactid")
    assert artifact_id is not None
    assert artifact_id.get_text() == "test-artifact"

    version = result.find("version")
    assert version is not None
    assert version.get_text() == "1.0.0"


@parametrize_sync(
    args=["input_text", "expected"],
    cases=[
        ["${project.version}", "project.version"],
        ["${commons.version}", "commons.version"],
        ["${spring.version}", "spring.version"],
        ["${parent.version}", "parent.version"],
        ["${custom.property}", "custom.property"],
        ["no-brackets", ""],
        ["${incomplete", ""],
        ["incomplete}", ""],
        ["", ""],
        ["${}", ""],
        ["${ }", " "],
    ],
)
def test_extract_bracketed_text(input_text: str, expected: str) -> None:
    assert extract_bracketed_text(input_text) == expected


@parametrize_sync(
    args=["xml_content", "element_name", "expected"],
    cases=[
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <root>
                <test>value</test>
            </root>""",
            "test",
            "value",
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <root>
                <test>value with spaces</test>
            </root>""",
            "test",
            "value with spaces",
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <root>
                <test>
                    <nested>nested value</nested>
                </test>
            </root>""",
            "nested",
            "nested value",
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <root>
                <other>value</other>
            </root>""",
            "test",
            None,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <root>
                <test></test>
            </root>""",
            "test",
            "",
        ],
    ],
)
def test_get_text(xml_content: str, element_name: str, expected: str | None) -> None:
    root = BeautifulSoup(xml_content, features="xml")
    assert root.root is not None
    result = _get_text(root.root, element_name)
    assert result == expected


@parametrize_sync(
    args=["pom_content", "parent_info", "expected"],
    cases=[
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <groupId>test.group</groupId>
                <artifactId>test-artifact</artifactId>
                <version>1.0.0</version>
            </project>""",
            {
                "group": "test.group",
                "artifact": "test-artifact",
                "version": "1.0.0",
            },
            True,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <groupId>different.group</groupId>
                <artifactId>test-artifact</artifactId>
                <version>1.0.0</version>
            </project>""",
            {
                "group": "test.group",
                "artifact": "test-artifact",
                "version": "1.0.0",
            },
            False,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <groupId>test.group</groupId>
                <artifactId>different-artifact</artifactId>
                <version>1.0.0</version>
            </project>""",
            {
                "group": "test.group",
                "artifact": "test-artifact",
                "version": "1.0.0",
            },
            False,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <groupId>test.group</groupId>
                <artifactId>test-artifact</artifactId>
                <version>2.0.0</version>
            </project>""",
            {
                "group": "test.group",
                "artifact": "test-artifact",
                "version": "1.0.0",
            },
            False,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <artifactId>test-artifact</artifactId>
                <version>1.0.0</version>
            </project>""",
            {
                "group": "test.group",
                "artifact": "test-artifact",
                "version": "1.0.0",
            },
            False,
        ],
    ],
)
def test_is_parent_pom(pom_content: str, parent_info: dict[str, str], expected: bool) -> None:  # noqa: FBT001
    root = BeautifulSoup(pom_content, features="html.parser")
    assert root.project is not None
    result = _is_parent_pom(root.project, parent_info)
    assert result == expected


@parametrize_sync(
    args=["pom_content", "pom_module", "expected"],
    cases=[
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <modules>
                    <module>module1</module>
                    <module>module2</module>
                </modules>
            </project>""",
            "module1/pom.xml",
            True,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <modules>
                    <module>module1</module>
                    <module>module2</module>
                </modules>
            </project>""",
            "module2/pom.xml",
            True,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <modules>
                    <module>module1</module>
                    <module>module2</module>
                </modules>
            </project>""",
            "module3/pom.xml",
            False,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <modules>
                    <module>module1</module>
                </modules>
                <modules>
                    <module>module2</module>
                </modules>
            </project>""",
            "module2/pom.xml",
            True,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
            </project>""",
            "module1/pom.xml",
            False,
        ],
    ],
)
def test_is_module_parent(pom_content: str, pom_module: str, expected: bool) -> None:  # noqa: FBT001
    root = BeautifulSoup(pom_content, features="xml")
    assert root.project is not None
    result = _is_module_parent(root.project, pom_module)
    assert result == expected


@parametrize_sync(
    args=["pom_content", "initial_properties", "expected_properties"],
    cases=[
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <properties>
                    <java.version>1.8</java.version>
                    <spring.version>2.5.0</spring.version>
                </properties>
            </project>""",
            {"existing.prop": "value"},
            {
                "existing.prop": "value",
                "java.version": "1.8",
                "spring.version": "2.5.0",
            },
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <properties>
                    <prop1>value1</prop1>
                </properties>
                <properties>
                    <prop2>value2</prop2>
                </properties>
            </project>""",
            {},
            {
                "prop1": "value1",
                "prop2": "value2",
            },
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <properties>
                    <prop1>value1</prop1>
                </properties>
            </project>""",
            {"prop1": "old_value"},
            {
                "prop1": "value1",
            },
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
            </project>""",
            {"existing.prop": "value"},
            {
                "existing.prop": "value",
            },
        ],
    ],
)
def test_add_properties_vars(
    pom_content: str,
    initial_properties: dict[str, str],
    expected_properties: dict[str, str],
) -> None:
    root = BeautifulSoup(pom_content, features="xml")
    assert root.project is not None

    properties_vars = initial_properties.copy()
    _add_properties_vars(properties_vars, root.project)
    assert properties_vars == expected_properties


@parametrize_sync(
    args=["pom_content", "expected_deps"],
    cases=[
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <dependencymanagement>
                    <dependencies>
                        <dependency>
                            <groupId>org.springframework</groupId>
                            <artifactId>spring-core</artifactId>
                            <version>5.3.0</version>
                        </dependency>
                        <dependency>
                            <groupId>junit</groupId>
                            <artifactId>junit</artifactId>
                            <version>4.13.2</version>
                        </dependency>
                    </dependencies>
                </dependencymanagement>
            </project>""",
            {
                "org.springframework:spring-core": "5.3.0",
                "junit:junit": "4.13.2",
            },
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <dependencymanagement>
                    <dependencies>
                        <dependency>
                            <groupId>org.springframework</groupId>
                            <artifactId>spring-core</artifactId>
                            <version>5.3.0</version>
                        </dependency>
                    </dependencies>
                </dependencymanagement>
                <dependencymanagement>
                    <dependencies>
                        <dependency>
                            <groupId>junit</groupId>
                            <artifactId>junit</artifactId>
                            <version>4.13.2</version>
                        </dependency>
                    </dependencies>
                </dependencymanagement>
            </project>""",
            {
                "org.springframework:spring-core": "5.3.0",
                "junit:junit": "4.13.2",
            },
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <dependencymanagement>
                    <dependencies>
                        <dependency>
                            <groupId>org.springframework</groupId>
                            <artifactId>spring-core</artifactId>
                        </dependency>
                        <dependency>
                            <groupId>junit</groupId>
                            <artifactId>junit</artifactId>
                            <version>4.13.2</version>
                        </dependency>
                    </dependencies>
                </dependencymanagement>
            </project>""",
            {
                "junit:junit": "4.13.2",
            },
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <dependencymanagement>
                    <dependencies>
                        <dependency>
                            <groupId>org.springframework</groupId>
                            <artifactId>spring-core</artifactId>
                            <version>5.3.0</version>
                            <scope>test</scope>
                        </dependency>
                    </dependencies>
                </dependencymanagement>
            </project>""",
            {
                "org.springframework:spring-core": "5.3.0",
            },
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
            </project>""",
            {},
        ],
    ],
)
def test_get_deps_management(pom_content: str, expected_deps: dict[str, str]) -> None:
    root = BeautifulSoup(pom_content, features="html.parser")
    assert root.project is not None
    result = _get_deps_management(root.project)
    assert result == expected_deps


@parametrize_sync(
    args=[
        "parent_pom_content",
        "current_pom_content",
        "current_pom_path",
        "expected_properties",
        "expected_deps",
    ],
    cases=[
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <groupId>test.group</groupId>
                <artifactId>parent-artifact</artifactId>
                <version>1.0.0</version>
                <modules>
                    <module>module1</module>
                </modules>
                <properties>
                    <java.version>1.8</java.version>
                </properties>
                <dependencymanagement>
                    <dependencies>
                        <dependency>
                            <groupId>org.springframework</groupId>
                            <artifactId>spring-core</artifactId>
                            <version>5.3.0</version>
                        </dependency>
                    </dependencies>
                </dependencymanagement>
            </project>""",
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <parent>
                    <groupId>test.group</groupId>
                    <artifactId>parent-artifact</artifactId>
                    <version>1.0.0</version>
                </parent>
                <dependencymanagement>
                    <dependencies>
                        <dependency>
                            <groupId>junit</groupId>
                            <artifactId>junit</artifactId>
                            <version>4.13.2</version>
                        </dependency>
                    </dependencies>
                </dependencymanagement>
            </project>""",
            "module1/pom.xml",
            {
                "java.version": "1.8",
            },
            {
                "org.springframework:spring-core": "5.3.0",
                "junit:junit": "4.13.2",
            },
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <groupId>test.group</groupId>
                <artifactId>parent-artifact</artifactId>
                <version>1.0.0</version>
                <modules>
                    <module>module2</module>
                </modules>
                <properties>
                    <spring.version>2.5.0</spring.version>
                </properties>
                <dependencymanagement>
                    <dependencies>
                        <dependency>
                            <groupId>org.springframework</groupId>
                            <artifactId>spring-core</artifactId>
                            <version>${spring.version}</version>
                        </dependency>
                    </dependencies>
                </dependencymanagement>
            </project>""",
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <parent>
                    <groupId>test.group</groupId>
                    <artifactId>parent-artifact</artifactId>
                    <version>1.0.0</version>
                </parent>
            </project>""",
            "module2/pom.xml",
            {
                "spring.version": "2.5.0",
            },
            {
                "org.springframework:spring-core": "${spring.version}",
            },
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <groupId>different.group</groupId>
                <artifactId>parent-artifact</artifactId>
                <version>1.0.0</version>
            </project>""",
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <parent>
                    <groupId>test.group</groupId>
                    <artifactId>parent-artifact</artifactId>
                    <version>1.0.0</version>
                </parent>
            </project>""",
            "module1/pom.xml",
            {},
            {},
        ],
    ],
)
def test_evaluate_pom_files_in_project(
    parent_pom_content: str,
    current_pom_content: str,
    current_pom_path: str,
    expected_properties: dict[str, str],
    expected_deps: dict[str, str],
) -> None:
    mock_resolver = MagicMock(spec=Resolver)
    mock_resolver.files_by_glob.return_value = ["parent/pom.xml"]
    mock_resolver.file_contents_by_location.return_value = parent_pom_content

    parent_info = {
        "group": "test.group",
        "artifact": "parent-artifact",
        "version": "1.0.0",
    }

    current_pom = BeautifulSoup(current_pom_content, features="html.parser")
    assert current_pom.project is not None

    properties_vars, manage_deps = _evaluate_pom_files_in_project(
        mock_resolver,
        parent_info,
        current_pom_path,
        current_pom.project,
    )

    assert properties_vars == expected_properties
    assert manage_deps == expected_deps


def test_update_location_with_dependency_info() -> None:
    dependency_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <dependency>
        <groupId>test.group</groupId>
        <artifactId>test-artifact</artifactId>
        <version>1.0.0</version>
    </dependency>"""

    dependency = BeautifulSoup(dependency_xml, features="xml").dependency
    assert dependency is not None

    if dependency.version:
        dependency.version.sourceline = 4
    dependency.sourceline = 2

    location = Location(
        coordinates=None,
        dependency_type=DependencyType.UNKNOWN,
        access_path="test.xml",
        annotations={},
    )

    update_location_with_dependency_info(location, dependency)

    assert location.coordinates is None
    assert location.dependency_type == DependencyType.UNKNOWN


def test_new_package_from_pom_xml_without_name() -> None:
    dependency_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <dependency>
        <groupId>test.group</groupId>
        <version>1.0.0</version>
    </dependency>"""

    project_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0">
        <groupId>test.group</groupId>
        <artifactId>test-artifact</artifactId>
        <version>1.0.0</version>
    </project>"""

    dependency = BeautifulSoup(dependency_xml, features="xml").dependency
    project = BeautifulSoup(project_xml, features="xml").project
    assert dependency is not None
    assert project is not None

    location = Location(
        coordinates=None,
        dependency_type=DependencyType.UNKNOWN,
        access_path="test.xml",
        annotations={},
    )

    context = PomContext(
        parent_info=None,
        parent_version_properties=None,
        manage_deps=None,
    )

    result = new_package_from_pom_xml(project, dependency, location, context)
    assert result is None


def test_new_package_from_pom_xml_with_invalid_version() -> None:
    dependency_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <dependency>
        <groupId>test.group</groupId>
        <artifactId>test-artifact</artifactId>
        <version>${project.version}</version>
    </dependency>"""

    project_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0">
        <groupId>test.group</groupId>
        <artifactId>test-artifact</artifactId>
        <version>1.0.0</version>
    </project>"""

    dependency = BeautifulSoup(dependency_xml, features="html.parser").dependency
    project = BeautifulSoup(project_xml, features="html.parser").project
    assert dependency is not None
    assert project is not None

    location = Location(
        coordinates=None,
        dependency_type=DependencyType.UNKNOWN,
        access_path="test.xml",
        annotations={},
    )

    context = PomContext(
        parent_info=None,
        parent_version_properties=None,
        manage_deps=None,
    )

    result = new_package_from_pom_xml(project, dependency, location, context)
    assert result is None


async def test_new_package_from_pom_xml_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    dependency_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <dependency>
        <groupId>test.group</groupId>
        <artifactId>test-artifact</artifactId>
        <version>1.0.0</version>
    </dependency>"""

    project_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0">
        <groupId>test.group</groupId>
        <artifactId>test-artifact</artifactId>
        <version>1.0.0</version>
    </project>"""

    dependency = BeautifulSoup(dependency_xml, features="html.parser").dependency
    project = BeautifulSoup(project_xml, features="html.parser").project
    assert dependency is not None
    assert project is not None

    location = Location(
        coordinates=Coordinates(
            real_path="test.xml",
            file_system_id=None,
            line=0,
        ),
        dependency_type=DependencyType.UNKNOWN,
        access_path="test.xml",
        annotations={},
    )

    context = PomContext(
        parent_info={
            "group": "test.group",
            "artifact": "parent-artifact",
            "version": "1.0.0",
        },
        parent_version_properties={"spring.version": "2.0.0"},
        manage_deps=None,
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

        result = new_package_from_pom_xml(project, dependency, location, context)
        assert result is None
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


@mocks(
    mocks=[
        Mock(
            labels.parsers.cataloger.java.parse_pom_xml,
            "resolve_parent_version",
            "sync",
            "2.0.0",
        ),
    ],
)
async def test_new_package_from_pom_xml_resolve_parent_version() -> None:
    dependency_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <dependency>
        <groupId>test.group</groupId>
        <artifactId>test-artifact</artifactId>
    </dependency>"""

    project_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0">
        <groupId>test.group</groupId>
        <artifactId>test-artifact</artifactId>
        <version>1.0.0</version>
    </project>"""

    dependency = BeautifulSoup(dependency_xml, features="html.parser").dependency
    project = BeautifulSoup(project_xml, features="html.parser").project
    assert dependency is not None
    assert project is not None

    location = Location(
        coordinates=Coordinates(
            real_path="test.xml",
            file_system_id=None,
            line=0,
        ),
        dependency_type=DependencyType.UNKNOWN,
        access_path="test.xml",
        annotations={},
    )

    context = PomContext(
        parent_info={
            "group": "test.group",
            "artifact": "parent-artifact",
            "version": "1.0.0",
        },
        parent_version_properties=None,
        manage_deps=None,
    )

    result = new_package_from_pom_xml(project, dependency, location, context)
    assert result is not None
    assert result.version == "2.0.0"


def test_new_package_from_pom_xml_resolve_managed_version() -> None:
    dependency_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <dependency>
        <groupId>test.group</groupId>
        <artifactId>test-artifact</artifactId>
    </dependency>"""

    project_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0">
        <groupId>test.group</groupId>
        <artifactId>test-artifact</artifactId>
        <version>1.0.0</version>
    </project>"""

    dependency = BeautifulSoup(dependency_xml, features="html.parser").dependency
    project = BeautifulSoup(project_xml, features="html.parser").project
    assert dependency is not None
    assert project is not None

    location = Location(
        coordinates=Coordinates(
            real_path="test.xml",
            file_system_id=None,
            line=0,
        ),
        dependency_type=DependencyType.UNKNOWN,
        access_path="test.xml",
        annotations={},
    )

    context = PomContext(
        parent_info=None,
        parent_version_properties={"spring.version": "2.5.0"},
        manage_deps={"test.group:test-artifact": "${spring.version}"},
    )

    result = new_package_from_pom_xml(project, dependency, location, context)
    assert result is not None
    assert result.version == "2.5.0"


@parametrize_sync(
    args=["version", "project_content", "parent_properties", "expected"],
    cases=[
        [
            "${spring.version}",
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <properties>
                    <spring.version>2.5.0</spring.version>
                </properties>
            </project>""",
            None,
            "2.5.0",
        ],
        [
            "${spring.version}",
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
            </project>""",
            {"spring.version": "2.5.0"},
            "2.5.0",
        ],
        [
            "${spring.version}",
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <properties>
                    <spring.version>${parent.version}</spring.version>
                </properties>
            </project>""",
            None,
            None,
        ],
        [
            "${spring.version}",
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
            </project>""",
            None,
            None,
        ],
    ],
)
def test_resolve_property_version(
    version: str,
    project_content: str,
    parent_properties: dict[str, str] | None,
    expected: str | None,
) -> None:
    project = BeautifulSoup(project_content, features="xml").project
    assert project is not None
    result = resolve_property_version(version, project, parent_properties)
    assert result == expected


@parametrize_sync(
    args=["java_archive", "parent_info", "mock_return", "expected"],
    cases=[
        [
            JavaArchive(
                pom_properties=JavaPomProperties(
                    group_id="test.group",
                    artifact_id="test-artifact",
                    version="1.0.0",
                ),
            ),
            {
                "group": "parent.group",
                "artifact": "parent-artifact",
                "version": "2.0.0",
            },
            "1.5.0",
            "1.5.0",
        ],
        [
            JavaArchive(
                pom_properties=JavaPomProperties(
                    group_id="test.group",
                    artifact_id="test-artifact",
                    version="1.0.0",
                ),
            ),
            {
                "group": "parent.group",
                "artifact": "parent-artifact",
                "version": "2.0.0",
            },
            None,
            None,
        ],
        [
            JavaArchive(
                pom_properties=JavaPomProperties(
                    group_id=None,
                    artifact_id="test-artifact",
                    version="1.0.0",
                ),
            ),
            {
                "group": "parent.group",
                "artifact": "parent-artifact",
                "version": "2.0.0",
            },
            "1.5.0",
            None,
        ],
        [
            JavaArchive(
                pom_properties=JavaPomProperties(
                    group_id="test.group",
                    artifact_id=None,
                    version="1.0.0",
                ),
            ),
            {
                "group": "parent.group",
                "artifact": "parent-artifact",
                "version": "2.0.0",
            },
            "1.5.0",
            None,
        ],
        [
            JavaArchive(
                pom_properties=None,
            ),
            {
                "group": "parent.group",
                "artifact": "parent-artifact",
                "version": "2.0.0",
            },
            "1.5.0",
            None,
        ],
    ],
)
def test_resolve_parent_version(
    java_archive: JavaArchive,
    parent_info: dict[str, str],
    mock_return: str | None,
    expected: str | None,
) -> None:
    with patch(
        "labels.parsers.cataloger.java.parse_pom_xml.recursively_find_versions_from_parent_pom",
        return_value=mock_return,
    ):
        result = resolve_parent_version(java_archive, parent_info)
        assert result == expected


@parametrize_sync(
    args=["manage_deps", "parent_version_properties", "full_name", "expected"],
    cases=[
        [
            {"test.group:test-artifact": "1.0.0"},
            {},
            "test.group:test-artifact",
            "1.0.0",
        ],
        [
            {"test.group:test-artifact": "${spring.version}"},
            {"spring.version": "2.5.0"},
            "test.group:test-artifact",
            "2.5.0",
        ],
        [
            {"test.group:test-artifact": "${spring.version}"},
            {},
            "test.group:test-artifact",
            None,
        ],
        [
            {"test.group:test-artifact": "${spring.version}"},
            {"other.version": "2.5.0"},
            "test.group:test-artifact",
            None,
        ],
        [
            {},
            {"spring.version": "2.5.0"},
            "test.group:test-artifact",
            None,
        ],
        [
            {"other.group:other-artifact": "1.0.0"},
            {},
            "test.group:test-artifact",
            None,
        ],
    ],
)
def test_resolve_managed_version(
    manage_deps: dict[str, str],
    parent_version_properties: dict[str, str],
    full_name: str,
    expected: str | None,
) -> None:
    result = resolve_managed_version(manage_deps, parent_version_properties, full_name)
    assert result == expected


def test_parse_pom_xml_assertion_error() -> None:
    reader = TextIOWrapper(BytesIO(b""), encoding="utf-8")
    with patch(
        "labels.parsers.cataloger.java.parse_pom_xml.BeautifulSoup",
        side_effect=AssertionError("Invalid XML"),
    ):
        pkgs, rels = parse_pom_xml(
            None,
            None,
            LocationReadCloser(location=new_location("test.xml"), read_closer=reader),
        )
        assert pkgs == []
        assert rels == []


def test_parse_pom_xml_no_root() -> None:
    reader = TextIOWrapper(BytesIO(b""), encoding="utf-8")
    with patch("labels.parsers.cataloger.java.parse_pom_xml.BeautifulSoup", return_value=None):
        pkgs, rels = parse_pom_xml(
            None,
            None,
            LocationReadCloser(location=new_location("test.xml"), read_closer=reader),
        )
        assert pkgs == []
        assert rels == []


def test_parse_pom_xml_invalid_namespace() -> None:
    xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://wrong.namespace">
        <dependencies>
            <dependency>
                <groupId>test.group</groupId>
                <artifactId>test-artifact</artifactId>
                <version>1.0.0</version>
            </dependency>
        </dependencies>
    </project>"""

    reader = TextIOWrapper(BytesIO(xml_content), encoding="utf-8")
    pkgs, rels = parse_pom_xml(
        None,
        None,
        LocationReadCloser(location=new_location("test.xml"), read_closer=reader),
    )
    assert pkgs == []
    assert rels == []


def test_parse_pom_xml_invalid_dependency() -> None:
    xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0">
        <dependencies>
            <dependency>
                <groupId>test.group</groupId>
                <artifactId>test-artifact</artifactId>
                <version>${invalid.property}</version>
            </dependency>
        </dependencies>
    </project>"""

    reader = TextIOWrapper(BytesIO(xml_content), encoding="utf-8")
    pkgs, rels = parse_pom_xml(
        None,
        None,
        LocationReadCloser(location=new_location("test.xml"), read_closer=reader),
    )
    assert pkgs == []
    assert rels == []


def test_parse_pom_xml_with_resolver_and_parent_info() -> None:
    xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0">
        <parent>
            <groupId>test.group</groupId>
            <artifactId>parent-artifact</artifactId>
            <version>1.0.0</version>
        </parent>
        <dependencies>
            <dependency>
                <groupId>test.group</groupId>
                <artifactId>test-artifact</artifactId>
                <version>1.0.0</version>
            </dependency>
        </dependencies>
    </project>"""

    parent_pom_content = """<?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0">
        <groupId>test.group</groupId>
        <artifactId>parent-artifact</artifactId>
        <version>1.0.0</version>
        <modules>
            <module>module1</module>
        </modules>
        <properties>
            <java.version>1.8</java.version>
        </properties>
        <dependencymanagement>
            <dependencies>
                <dependency>
                    <groupId>org.springframework</groupId>
                    <artifactId>spring-core</artifactId>
                    <version>5.3.0</version>
                </dependency>
            </dependencies>
        </dependencymanagement>
    </project>"""

    mock_resolver = MagicMock(spec=Resolver)
    mock_resolver.files_by_glob.return_value = ["parent/pom.xml"]
    mock_resolver.file_contents_by_location.return_value = parent_pom_content

    reader = TextIOWrapper(BytesIO(xml_content), encoding="utf-8")
    pkgs, rels = parse_pom_xml(
        mock_resolver,
        None,
        LocationReadCloser(location=new_location("module1/pom.xml"), read_closer=reader),
    )

    assert len(pkgs) == 1
    assert pkgs[0].name == "test.group:test-artifact"
    assert pkgs[0].version == "1.0.0"
    assert rels == []


@parametrize_sync(
    args=["xml_content", "expected_tag_name"],
    cases=[
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <groupId>test.group</groupId>
                <artifactId>test-artifact</artifactId>
                <version>1.0.0</version>
            </project>""",
            "project",
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <root>
                <child>value</child>
            </root>""",
            "root",
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <dependencies>
                <dependency>
                    <groupId>test.group</groupId>
                    <artifactId>test-artifact</artifactId>
                </dependency>
            </dependencies>""",
            "dependencies",
        ],
    ],
)
def test_decode_pom_xml(xml_content: str, expected_tag_name: str) -> None:
    result = decode_pom_xml(xml_content)
    root_element = result.find()
    assert root_element is not None
    assert root_element.name == expected_tag_name
    assert isinstance(root_element, Tag)


@parametrize_sync(
    args=["parent_xml", "expected_result"],
    cases=[
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <parent>
                    <groupId>test.group</groupId>
                    <artifactId>test-artifact</artifactId>
                    <version>1.0.0</version>
                </parent>
            </project>""",
            JavaPomParent(
                group_id="test.group",
                artifact_id="test-artifact",
                version="1.0.0",
            ),
        ],
        [
            None,
            None,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <parent>
                    <artifactId>test-artifact</artifactId>
                    <version>1.0.0</version>
                </parent>
            </project>""",
            None,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <parent>
                    <groupId>test.group</groupId>
                    <version>1.0.0</version>
                </parent>
            </project>""",
            None,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <parent>
                    <groupId>test.group</groupId>
                    <artifactId>test-artifact</artifactId>
                </parent>
            </project>""",
            None,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <parent>
                    <groupId></groupId>
                    <artifactId></artifactId>
                    <version></version>
                </parent>
            </project>""",
            None,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <parent>
                    <groupId> </groupId>
                    <artifactId> </artifactId>
                    <version> </version>
                </parent>
            </project>""",
            None,
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <parent>
                    <groupId>test.group</groupId>
                    <artifactId>test-artifact</artifactId>
                    <version>1.0.0</version>
                    <extra>extra</extra>
                </parent>
            </project>""",
            JavaPomParent(
                group_id="test.group",
                artifact_id="test-artifact",
                version="1.0.0",
            ),
        ],
    ],
)
def test_pom_parent_edge_cases(
    parent_xml: str | None,
    expected_result: JavaPomParent | None,
) -> None:
    parent = BeautifulSoup(parent_xml, features="xml").project if parent_xml else None
    project = pom_parent(parent)
    assert project == expected_result


@parametrize_sync(
    args=["pom_content", "expected_licenses"],
    cases=[
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <licenses>
                    <license>
                        <name>Apache License 2.0</name>
                        <url>https://www.apache.org/licenses/LICENSE-2.0</url>
                    </license>
                </licenses>
            </project>""",
            ["Apache License 2.0"],
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <licenses>
                    <license>
                        <url>https://www.apache.org/licenses/LICENSE-2.0</url>
                    </license>
                </licenses>
            </project>""",
            ["https://www.apache.org/licenses/LICENSE-2.0"],
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <licenses>
                    <license>
                        <name>Apache License 2.0</name>
                    </license>
                    <license>
                        <url>https://www.apache.org/licenses/LICENSE-2.0</url>
                    </license>
                </licenses>
            </project>""",
            ["Apache License 2.0", "https://www.apache.org/licenses/LICENSE-2.0"],
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <licenses>
                    <license>
                    </license>
                </licenses>
            </project>""",
            [],
        ],
        [
            """<?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <licenses>
                    <license>
                        <name></name>
                        <url></url>
                    </license>
                </licenses>
            </project>""",
            [],
        ],
    ],
)
def test_parse_pom_xml_project_licenses(pom_content: str, expected_licenses: list[str]) -> None:
    result = parse_pom_xml_project(
        "test.xml",
        pom_content,
        Location(
            coordinates=None,
            dependency_type=DependencyType.UNKNOWN,
            access_path="test.xml",
            annotations={},
        ),
    )
    assert result is not None
    assert result.licenses == expected_licenses
