from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.java.model import JavaArchive, JavaPomProject
from labels.parsers.cataloger.java.parse_gradle_lockfile import parse_gradle_lockfile
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_gradle_lock_file() -> None:
    test_data_path = get_test_data_path("dependencies/java/gradle/gradle.lockfile")
    expected = [
        Package(
            name="joda-time",
            version="2.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=4,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVA,
            licenses=[],
            type=PackageType.JavaPkg,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="joda-time",
                    artifact_id="joda-time",
                    version="2.2",
                    name="joda-time",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/joda-time/joda-time@2.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="junit",
            version="4.12",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=5,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVA,
            licenses=[],
            type=PackageType.JavaPkg,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="junit",
                    artifact_id="junit",
                    version="4.12",
                    name="junit",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/junit/junit@4.12",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="hamcrest-core",
            version="1.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=6,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVA,
            licenses=[],
            type=PackageType.JavaPkg,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="org.hamcrest",
                    artifact_id="hamcrest-core",
                    version="1.3",
                    name="hamcrest-core",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/org.hamcrest/hamcrest-core@1.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="commons-text",
            version="1.8",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=8,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.JAVA,
            licenses=[],
            type=PackageType.JavaPkg,
            metadata=JavaArchive(
                virtual_path=None,
                manifest=None,
                pom_properties=None,
                pom_project=JavaPomProject(
                    path=None,
                    group_id="org.apache.commons",
                    artifact_id="commons-text",
                    version="1.8",
                    name="commons-text",
                    parent=None,
                    description=None,
                    url=None,
                ),
                archive_digests=[],
                parent=None,
            ),
            p_url="pkg:maven/org.apache.commons/commons-text@1.8",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_gradle_lockfile(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        assert pkgs == expected


def test_parse_gradle_lock_file_with_empty_fields() -> None:
    content = """joda-time:joda-time:2.2=2.2
junit:junit:4.12=4.12
org.hamcrest:hamcrest-core:1.3=1.3
com.example::1.0.0=somevalue
org.test:test:"":2.0
org.test:test:2.0=2.0"""

    bytes_io = BytesIO(content.encode("utf-8"))
    text_wrapper = TextIOWrapper(bytes_io, encoding="utf-8")

    modified_reader = LocationReadCloser(
        location=new_location("test.lockfile"),
        read_closer=text_wrapper,
    )

    pkgs, _ = parse_gradle_lockfile(None, None, modified_reader)

    assert len(pkgs) == 4
    pkg_names = {pkg.name for pkg in pkgs}
    assert pkg_names == {"joda-time", "junit", "hamcrest-core", "test"}

    assert "empty-name" not in pkg_names
    assert "org.test:test:" not in pkg_names


def test_parse_gradle_lock_file_without_coordinates() -> None:
    content = """joda-time:joda-time:2.2=2.2
junit:junit:4.12=4.12"""

    bytes_io = BytesIO(content.encode("utf-8"))
    text_wrapper = TextIOWrapper(bytes_io, encoding="utf-8")

    location = new_location("test.lockfile")
    location.coordinates = None

    modified_reader = LocationReadCloser(
        location=location,
        read_closer=text_wrapper,
    )

    pkgs, _ = parse_gradle_lockfile(None, None, modified_reader)

    assert len(pkgs) == 2
    pkg_names = {pkg.name for pkg in pkgs}
    assert pkg_names == {"joda-time", "junit"}

    for pkg in pkgs:
        assert pkg.locations[0].coordinates is None


def test_parse_gradle_lock_file_with_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    content = """joda-time:joda-time:2.2=2.2
junit:junit:4.12=4.12"""

    bytes_io = BytesIO(content.encode("utf-8"))
    text_wrapper = TextIOWrapper(bytes_io, encoding="utf-8")

    modified_reader = LocationReadCloser(
        location=new_location("test.lockfile"),
        read_closer=text_wrapper,
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

        pkgs, _ = parse_gradle_lockfile(None, None, modified_reader)
        assert len(pkgs) == 0
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )
