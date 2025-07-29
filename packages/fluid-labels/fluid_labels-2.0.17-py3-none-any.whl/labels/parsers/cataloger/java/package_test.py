from labels.parsers.cataloger.java.model import (
    JavaArchive,
    JavaPomParent,
    JavaPomProject,
    JavaPomProperties,
)
from labels.parsers.cataloger.java.package import (
    group_id_from_java_metadata,
    group_id_from_pom_properties,
    group_id_pom_project,
    looks_like_group_id,
)


def test_looks_like_group_id_with_valid_inputs() -> None:
    assert looks_like_group_id("com.example") is True
    assert looks_like_group_id("org.apache.commons") is True
    assert looks_like_group_id("io.github.user") is True
    assert looks_like_group_id("net.something.else") is True


def test_looks_like_group_id_with_invalid_inputs() -> None:
    assert looks_like_group_id("") is False
    assert looks_like_group_id("simple") is False
    assert looks_like_group_id("no-dots-here") is False
    assert looks_like_group_id("just_underscores") is False


def test_group_id_from_pom_properties() -> None:
    assert group_id_from_pom_properties(None) == ""

    properties_with_group_id = JavaPomProperties(group_id="com.example", artifact_id="test")
    assert group_id_from_pom_properties(properties_with_group_id) == "com.example"

    properties_with_artifact_as_group = JavaPomProperties(
        group_id="",
        artifact_id="org.apache.commons",
    )
    assert group_id_from_pom_properties(properties_with_artifact_as_group) == "org.apache.commons"

    properties_with_invalid_artifact = JavaPomProperties(group_id="", artifact_id="simple-artifact")
    assert group_id_from_pom_properties(properties_with_invalid_artifact) == ""

    properties_with_both = JavaPomProperties(
        group_id="com.example",
        artifact_id="org.apache.commons",
    )
    assert group_id_from_pom_properties(properties_with_both) == "com.example"


def test_group_id_pom_project() -> None:
    assert group_id_pom_project(None) == ""

    project_with_group_id = JavaPomProject(group_id="com.example", artifact_id="test")
    assert group_id_pom_project(project_with_group_id) == "com.example"

    project_with_artifact_as_group = JavaPomProject(group_id="", artifact_id="org.apache.commons")
    assert group_id_pom_project(project_with_artifact_as_group) == "org.apache.commons"

    parent_with_group_id = JavaPomParent(
        group_id="com.parent",
        artifact_id="parent-artifact",
        version="1.0.0",
    )
    project_with_parent_group = JavaPomProject(
        group_id="",
        artifact_id="simple-artifact",
        parent=parent_with_group_id,
    )
    assert group_id_pom_project(project_with_parent_group) == "com.parent"

    parent_with_artifact_as_group = JavaPomParent(
        group_id="",
        artifact_id="io.github.parent",
        version="1.0.0",
    )
    project_with_parent_artifact = JavaPomProject(
        group_id="",
        artifact_id="simple-artifact",
        parent=parent_with_artifact_as_group,
    )
    assert group_id_pom_project(project_with_parent_artifact) == "io.github.parent"

    project_without_valid_group = JavaPomProject(group_id="", artifact_id="simple-artifact")
    assert group_id_pom_project(project_without_valid_group) == ""

    parent_without_valid_group = JavaPomParent(
        group_id="",
        artifact_id="simple-parent",
        version="1.0.0",
    )
    project_with_invalid_parent = JavaPomProject(
        group_id="",
        artifact_id="simple-artifact",
        parent=parent_without_valid_group,
    )
    assert group_id_pom_project(project_with_invalid_parent) == ""


def test_group_id_from_java_metadata() -> None:
    assert group_id_from_java_metadata("test-package", None) is None

    properties_with_group_id = JavaPomProperties(group_id="com.example", artifact_id="test")
    metadata_with_properties = JavaArchive(
        pom_properties=properties_with_group_id,
        pom_project=None,
    )
    assert group_id_from_java_metadata("test-package", metadata_with_properties) == "com.example"

    project_with_group_id = JavaPomProject(group_id="org.example", artifact_id="test")
    metadata_with_project = JavaArchive(pom_properties=None, pom_project=project_with_group_id)
    assert group_id_from_java_metadata("test-package", metadata_with_project) == "org.example"

    metadata_without_valid_group = JavaArchive(pom_properties=None, pom_project=None)
    assert group_id_from_java_metadata("test-package", metadata_without_valid_group) is None

    properties_with_group_id = JavaPomProperties(group_id="com.example", artifact_id="test")
    project_with_group_id = JavaPomProject(group_id="org.example", artifact_id="test")
    metadata_with_both = JavaArchive(
        pom_properties=properties_with_group_id,
        pom_project=project_with_group_id,
    )
    assert group_id_from_java_metadata("test-package", metadata_with_both) == "com.example"
