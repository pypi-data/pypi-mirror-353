import pytest
import requests
from bs4 import BeautifulSoup, Tag

import labels.parsers.cataloger.java.maven_repo_utils
from labels.parsers.cataloger.java.maven_repo_utils import (
    format_maven_pom_ulr,
    get_dependency_version,
    get_parent_information,
    get_pom_from_maven_repo,
    process_pom,
    recursively_find_versions_from_parent_pom,
)
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.fake_response import MockResponse


class MockRepoResponse:
    def __init__(self, status_code: int, text: str) -> None:
        self.status_code = status_code
        self.text = text


def test_format_maven_pom_ulr() -> None:
    url = format_maven_pom_ulr(
        group_id="org.example",
        artifact_id="test-artifact",
        version="1.0.0",
    )
    expected = (
        "https://repo1.maven.org/maven2/org/example/test-artifact/1.0.0/test-artifact-1.0.0.pom"
    )
    assert url == expected

    custom_url = format_maven_pom_ulr(
        group_id="org.example",
        artifact_id="test-artifact",
        version="1.0.0",
        maven_base_url="https://custom.maven.repo",
    )
    expected_custom = (
        "https://custom.maven.repo/org/example/test-artifact/1.0.0/test-artifact-1.0.0.pom"
    )
    assert custom_url == expected_custom


@pytest.mark.flaky(re_runs=3, delay=2)
def test_get_pom_from_maven_repo_success() -> None:
    result = get_pom_from_maven_repo(
        group_id="junit",
        artifact_id="junit",
        version="4.12",
    )
    assert isinstance(result, BeautifulSoup)
    assert result.project is not None


@mocks(
    mocks=[
        Mock(
            module=requests,
            target="get",
            target_type="sync",
            expected=MockResponse(404, {}),
        ),
    ],
)
async def test_get_pom_from_maven_repo_not_found() -> None:
    result = get_pom_from_maven_repo(
        group_id="org.example",
        artifact_id="test-artifact",
        version="1.0.0",
    )
    assert result is None


def test_get_dependency_version() -> None:
    xml = """<?xml version="1.0" encoding="UTF-8"?>
        <dependencyManagement>
            <dependencies>
                <dependency>
                    <groupId>junit</groupId>
                    <artifactId>junit</artifactId>
                    <version>4.12</version>
                </dependency>
            </dependencies>
        </dependencyManagement>"""
    soup = BeautifulSoup(xml, features="html.parser")
    dependency_management = soup.find("dependencymanagement")
    assert isinstance(dependency_management, Tag)

    version = get_dependency_version(dependency_management, "junit", "junit")
    assert version == "4.12"

    version = get_dependency_version(dependency_management, "unknown", "unknown")
    assert version is None


def test_get_parent_information() -> None:
    xml = """<?xml version="1.0" encoding="UTF-8"?>
        <parent>
            <groupId>org.example</groupId>
            <artifactId>parent-artifact</artifactId>
            <version>1.0.0</version>
        </parent>"""
    soup = BeautifulSoup(xml, features="html.parser")
    parent = soup.find("parent")
    assert isinstance(parent, Tag)

    parent_group_id, parent_artifact_id, parent_version = get_parent_information(parent)
    assert parent_group_id == "org.example"
    assert parent_artifact_id == "parent-artifact"
    assert parent_version == "1.0.0"

    xml_incomplete = """<?xml version="1.0" encoding="UTF-8"?>
        <parent>
            <groupId>org.example</groupId>
        </parent>"""
    soup_incomplete = BeautifulSoup(xml_incomplete, features="html.parser")
    parent_incomplete = soup_incomplete.find("parent")
    assert isinstance(parent_incomplete, Tag)

    parent_group_id, parent_artifact_id, parent_version = get_parent_information(parent_incomplete)
    assert parent_group_id == "org.example"
    assert parent_artifact_id is None
    assert parent_version is None


def test_process_pom() -> None:
    xml_with_dependency = """<?xml version="1.0" encoding="UTF-8"?>
        <project>
            <dependencyManagement>
                <dependencies>
                    <dependency>
                        <groupId>junit</groupId>
                        <artifactId>junit</artifactId>
                        <version>4.12</version>
                    </dependency>
                </dependencies>
            </dependencyManagement>
        </project>"""
    soup_with_dependency = BeautifulSoup(xml_with_dependency, features="html.parser")
    version, parent_group_id, parent_artifact_id, parent_version = process_pom(
        soup_with_dependency,
        "junit",
        "junit",
    )
    assert version == "4.12"
    assert parent_group_id is None
    assert parent_artifact_id is None
    assert parent_version is None

    xml_with_parent = """<?xml version="1.0" encoding="UTF-8"?>
        <project>
            <parent>
                <groupId>org.example</groupId>
                <artifactId>parent-artifact</artifactId>
                <version>1.0.0</version>
            </parent>
        </project>"""
    soup_with_parent = BeautifulSoup(xml_with_parent, features="html.parser")
    version, parent_group_id, parent_artifact_id, parent_version = process_pom(
        soup_with_parent,
        "unknown",
        "unknown",
    )
    assert version is None
    assert parent_group_id == "org.example"
    assert parent_artifact_id == "parent-artifact"
    assert parent_version == "1.0.0"


def test_process_pom_no_project() -> None:
    xml_no_project = """<?xml version="1.0" encoding="UTF-8"?>
        <not_a_project></not_a_project>"""
    soup_no_project = BeautifulSoup(xml_no_project, features="html.parser")
    version, parent_group_id, parent_artifact_id, parent_version = process_pom(
        soup_no_project,
        "unknown",
        "unknown",
    )
    assert version is None
    assert parent_group_id is None
    assert parent_artifact_id is None
    assert parent_version is None


def test_process_pom_no_version() -> None:
    xml_no_version = """<?xml version="1.0" encoding="UTF-8"?>
        <project>
            <dependencyManagement>
                <dependencies>
                    <dependency>
                        <groupId>junit</groupId>
                        <artifactId>junit</artifactId>
                    </dependency>
                </dependencies>
            </dependencyManagement>
        </project>"""
    soup_no_version = BeautifulSoup(xml_no_version, features="html.parser")
    version, parent_group_id, parent_artifact_id, parent_version = process_pom(
        soup_no_version,
        "junit",
        "junit",
    )
    assert version is None
    assert parent_group_id is None
    assert parent_artifact_id is None
    assert parent_version is None


@mocks(
    mocks=[
        Mock(
            module=requests,
            target="get",
            target_type="sync",
            expected=MockRepoResponse(
                status_code=200,
                text="""<?xml version="1.0" encoding="UTF-8"?>
                <project>
                    <dependencyManagement>
                        <dependencies>
                            <dependency>
                                <groupId>junit</groupId>
                                <artifactId>junit</artifactId>
                                <version>4.12</version>
                            </dependency>
                        </dependencies>
                    </dependencyManagement>
                </project>""",
            ),
        ),
    ],
)
async def test_recursively_find_versions_from_parent_pom() -> None:
    version = recursively_find_versions_from_parent_pom(
        group_id="junit",
        artifact_id="junit",
        parent_group_id="org.example",
        parent_artifact_id="parent-artifact",
        parent_version="1.0.0",
    )
    assert version == "4.12"


@mocks(
    mocks=[
        Mock(
            module=requests,
            target="get",
            target_type="sync",
            expected=MockRepoResponse(
                status_code=404,
                text="",
            ),
        ),
    ],
)
async def test_recursively_find_versions_from_parent_pom_no_parent_pom() -> None:
    version = recursively_find_versions_from_parent_pom(
        group_id="junit",
        artifact_id="junit",
        parent_group_id="org.example",
        parent_artifact_id="parent-artifact",
        parent_version="1.0.0",
    )
    assert version is None


@mocks(
    mocks=[
        Mock(
            module=requests,
            target="get",
            target_type="sync",
            expected=MockRepoResponse(
                status_code=200,
                text="""<?xml version="1.0" encoding="UTF-8"?>
                <project>
                    <parent>
                        <groupId>org.example</groupId>
                    </parent>
                </project>""",
            ),
        ),
    ],
)
async def test_recursively_find_versions_from_parent_pom_incomplete_parent_details() -> None:
    version = recursively_find_versions_from_parent_pom(
        group_id="junit",
        artifact_id="junit",
        parent_group_id="org.example",
        parent_artifact_id="parent-artifact",
        parent_version="1.0.0",
    )
    assert version is None


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.cataloger.java.maven_repo_utils,
            target="get_pom_from_maven_repo",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_recursively_find_versions_parent_pom_not_found() -> None:
    result = recursively_find_versions_from_parent_pom(
        group_id="com.example",
        artifact_id="my-artifact",
        parent_group_id="com.example.parent",
        parent_artifact_id="parent-artifact",
        parent_version="1.0.0",
        maven_base_url="https://repo.maven.apache.org/maven2",
    )

    assert result is None


@mocks(
    mocks=[
        Mock(
            module=requests,
            target="get",
            target_type="sync",
            expected=MockRepoResponse(
                status_code=200,
                text="""<?xml version="1.0" encoding="UTF-8"?>
                <project>
                    <parent>
                        <groupId>org.example.parent1</groupId>
                        <artifactId>parent-artifact1</artifactId>
                        <version>1.0.0</version>
                    </parent>
                </project>""",
            ),
        ),
        Mock(
            module=requests,
            target="get",
            target_type="sync",
            expected=MockRepoResponse(
                status_code=200,
                text="""<?xml version="1.0" encoding="UTF-8"?>
                <project>
                    <parent>
                        <groupId>org.example.parent2</groupId>
                        <artifactId>parent-artifact2</artifactId>
                        <version>2.0.0</version>
                    </parent>
                </project>""",
            ),
        ),
        Mock(
            module=requests,
            target="get",
            target_type="sync",
            expected=MockRepoResponse(
                status_code=200,
                text="""<?xml version="1.0" encoding="UTF-8"?>
                <project>
                    <parent>
                        <groupId>org.example.parent3</groupId>
                        <artifactId>parent-artifact3</artifactId>
                        <version>3.0.0</version>
                    </parent>
                </project>""",
            ),
        ),
    ],
)
async def test_recursively_find_versions_from_parent_pom_three_iterations() -> None:
    version = recursively_find_versions_from_parent_pom(
        group_id="junit",
        artifact_id="junit",
        parent_group_id="org.example.parent1",
        parent_artifact_id="parent-artifact1",
        parent_version="1.0.0",
    )
    assert version is None
