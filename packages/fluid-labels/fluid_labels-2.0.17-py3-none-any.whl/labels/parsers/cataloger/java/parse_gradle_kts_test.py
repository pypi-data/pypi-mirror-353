from pathlib import Path
from unittest.mock import Mock as UnittestMock
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.java import parse_gradle_kts
from labels.parsers.cataloger.java.model import JavaArchive, JavaPomProject
from labels.parsers.cataloger.java.parse_gradle_kts import (
    LockFileDependency,
    create_package,
    create_packages,
    extract_dependency,
    parse_gradle_lockfile_kts,
)
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.helpers import get_test_data_path
from labels.testing.utils.pytest_marks import parametrize_sync
from labels.utils.file import new_location


def test_parse_gradle_lockfile_kts() -> None:
    test_data_path = get_test_data_path("dependencies/java/gradle/build.gradle.kts")
    expected_packages = [
        Package(
            name="org.codehaus.groovy:groovy",
            version="2.4.10",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=26,
                    ),
                    access_path=test_data_path,
                    annotations={},
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
                    group_id="org.codehaus.groovy",
                    artifact_id="groovy",
                    version="2.4.10",
                    name="groovy",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/org.codehaus.groovy/groovy@2.4.10",
        ),
        Package(
            name="androidx.core:core-ktx",
            version="1.1.0-alpha03",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=33,
                    ),
                    access_path=test_data_path,
                    annotations={},
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
                    group_id="androidx.core",
                    artifact_id="core-ktx",
                    version="1.1.0-alpha03",
                    name="core-ktx",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/androidx.core/core-ktx@1.1.0-alpha03",
        ),
        Package(
            name="androidx.constraintlayout:constraintlayout",
            version="1.1.3",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=34,
                    ),
                    access_path=test_data_path,
                    annotations={},
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
                    group_id="androidx.constraintlayout",
                    artifact_id="constraintlayout",
                    version="1.1.3",
                    name="constraintlayout",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/androidx.constraintlayout/constraintlayout@1.1.3",
        ),
        Package(
            name="com.google.android.material:material",
            version="1.0.0-beta01",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=35,
                    ),
                    access_path=test_data_path,
                    annotations={},
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
                    group_id="com.google.android.material",
                    artifact_id="material",
                    version="1.0.0-beta01",
                    name="material",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url=("pkg:maven/com.google.android.material/material@1.0.0-beta01"),
        ),
        Package(
            name="org.jetbrains.kotlinx:kotlinx-html-js",
            version="0.8.0",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=44,
                    ),
                    access_path=test_data_path,
                    annotations={},
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
                    group_id="org.jetbrains.kotlinx",
                    artifact_id="kotlinx-html-js",
                    version="0.8.0",
                    name="kotlinx-html-js",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/org.jetbrains.kotlinx/kotlinx-html-js@0.8.0",
        ),
        Package(
            name="org.jetbrains.kotlinx:kotlinx-html-js",
            version="0.8.0",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=45,
                    ),
                    access_path=test_data_path,
                    annotations={},
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
                    group_id="org.jetbrains.kotlinx",
                    artifact_id="kotlinx-html-js",
                    version="0.8.0",
                    name="kotlinx-html-js",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/org.jetbrains.kotlinx/kotlinx-html-js@0.8.0",
        ),
        Package(
            name="io.springfox:springfox-swagger-ui",
            version="2.6.3",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=46,
                    ),
                    access_path=test_data_path,
                    annotations={},
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
                    artifact_id="springfox-swagger-ui",
                    version="2.6.3",
                    name="springfox-swagger-ui",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/io.springfox/springfox-swagger-ui@2.6.3",
        ),
        Package(
            name="org.slf4j:slf4j-api",
            version="1.7.21",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=47,
                    ),
                    access_path=test_data_path,
                    annotations={},
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
                    group_id="org.slf4j",
                    artifact_id="slf4j-api",
                    version="1.7.21",
                    name="slf4j-api",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/org.slf4j/slf4j-api@1.7.21",
        ),
        Package(
            name="io.kotest:kotest-core-jvm",
            version="4.0.1",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=63,
                    ),
                    access_path=test_data_path,
                    annotations={},
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
                    group_id="io.kotest",
                    artifact_id="kotest-core-jvm",
                    version="4.0.1",
                    name="kotest-core-jvm",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/io.kotest/kotest-core-jvm@4.0.1",
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, relations = parse_gradle_lockfile_kts(
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


@parametrize_sync(
    args=["dependency", "expected_packages"],
    cases=[
        [
            LockFileDependency(group="org.example", name="", version="1.0.0", line=1),
            [],
        ],
        [
            LockFileDependency(group="org.example", name="library", version="", line=1),
            [],
        ],
        [
            LockFileDependency(group="org.example", name="", version="", line=1),
            [],
        ],
    ],
)
def test_create_packages_with_empty_values(
    dependency: LockFileDependency,
    expected_packages: list[Package],
) -> None:
    location = Location(access_path="test/path")
    result = create_packages([dependency], location)
    assert result == expected_packages


@parametrize_sync(
    args=["line", "expected"],
    cases=[
        ["implementation('org.example:library:${version}')", None],
        ["implementation('org.example:library:$version')", None],
        ["implementation('org.example:library:${getVersion()}')", None],
        ["implementation('org.example:library:$someVersion')", None],
        ["implementation('org.example:library')", None],
        ["implementation('org.example:library:')", None],
        ["implementation('org.example:library:  ')", None],
        ["implementation('org.example:library::')", None],
        [
            "implementation('org.example:library:1.0.0')",
            LockFileDependency(
                group="org.example",
                name="library",
                version="1.0.0",
                line=1,
            ),
        ],
    ],
)
def test_extract_dependency_version_cases(
    line: str,
    expected: LockFileDependency | None,
) -> None:
    result = extract_dependency(line, line_no=1)
    assert result == expected


def test_create_packages_without_coordinates() -> None:
    dependency = LockFileDependency(
        group="org.example",
        name="library",
        version="1.0.0",
        line=42,
    )

    location = Location(access_path="test/path", coordinates=None)

    packages = create_packages([dependency], location)

    assert len(packages) == 1
    package = packages[0]
    assert package.name == "org.example:library"
    assert package.version == "1.0.0"
    assert len(package.locations) == 1
    assert package.locations[0].coordinates is None


def test_extract_dependency_version_group_none() -> None:
    mock_match = UnittestMock()
    mock_match.group.side_effect = lambda x: {
        "group": "org.example",
        "name": "library",
        "version": None,
    }.get(x)

    mock_pattern = UnittestMock()
    mock_pattern.match = UnittestMock(return_value=mock_match)

    with patch("labels.parsers.cataloger.java.parse_gradle_kts.RE_GRADLE_KTS", mock_pattern):
        result = extract_dependency("implementation('org.example:library')", line_no=1)
        assert result is None


@mocks(
    mocks=[
        Mock(
            module=parse_gradle_kts,
            target="create_package",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_create_packages_with_none_package() -> None:
    dependency = LockFileDependency(
        group="org.example",
        name="library",
        version="1.0.0",
        line=1,
    )
    location = Location(access_path="test/path")
    result = create_packages([dependency], location)
    assert result == []


def test_create_package_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    location = Location(access_path="test/path")
    archive = JavaArchive(
        pom_project=JavaPomProject(
            group_id="org.example",
            name="library",
            artifact_id="library",
            version="1.0.0",
        ),
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
        result = create_package("org.example:library", "1.0.0", location, archive, "org.example")

    assert result is None
    assert (
        "Malformed package. Required fields are missing or data types are incorrect." in caplog.text
    )
