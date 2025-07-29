from io import BytesIO, TextIOWrapper
from pathlib import Path

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.java.parse_gradle_properties import parse_gradle_properties
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_gradle_properties() -> None:
    test_data_path = get_test_data_path(
        "dependencies/java/gradle-properties/gradle-wrapper.properties",
    )
    expected_packages = [
        Package(
            name="gradle",
            version="7.5",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=3,
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
            metadata=None,
            p_url="pkg:maven/gradle/gradle@7.5",
        ),
    ]

    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, relations = parse_gradle_properties(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )

        assert pkgs == expected_packages
        assert relations == []


def test_parse_gradle_properties_without_coordinates() -> None:
    test_data_path = "test.gradle"
    content = r"""#Mon Mar 18 2024
distributionBase=GRADLE_USER_HOME
distributionUrl=https\://services.gradle.org/distributions/gradle-8.6-bin.zip
distributionPath=wrapper/dists
zipStorePath=wrapper/dists
zipStoreBase=GRADLE_USER_HOME
"""
    expected_packages = [
        Package(
            name="gradle",
            version="8.6",
            language=Language.JAVA,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=None,
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
            metadata=None,
            p_url="pkg:maven/gradle/gradle@8.6",
        ),
    ]

    location = Location(
        scope=Scope.PROD,
        coordinates=None,
        access_path=test_data_path,
        annotations={},
        dependency_type=DependencyType.UNKNOWN,
    )

    reader = TextIOWrapper(BytesIO(content.encode()))
    pkgs, relations = parse_gradle_properties(
        None,
        None,
        LocationReadCloser(location=location, read_closer=reader),
    )

    assert pkgs == expected_packages
    assert relations == []
