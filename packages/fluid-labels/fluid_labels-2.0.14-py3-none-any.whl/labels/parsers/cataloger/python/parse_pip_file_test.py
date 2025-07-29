from pathlib import Path

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.python.model import PythonPackage
from labels.parsers.cataloger.python.parse_pipfile_deps import parse_pipfile_deps
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_pip_file() -> None:
    test_data_path = get_test_data_path("dependencies/python/Pipfile")
    expected = [
        Package(
            name="records",
            version="0.5.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=11,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.PYTHON,
            licenses=[],
            type=PackageType.PythonPkg,
            metadata=PythonPackage(
                name="records",
                version="0.5.0",
                author=None,
                author_email=None,
                platform=None,
                files=None,
                site_package_root_path=None,
                top_level_packages=None,
                direct_url_origin=None,
                dependencies=None,
            ),
            p_url="pkg:pypi/records@0.5.0",
            dependencies=None,
            found_by=None,
        ),
        Package(
            name="unittest2",
            version="1.0,<3.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=19,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                    scope=Scope.DEV,
                ),
            ],
            language=Language.PYTHON,
            licenses=[],
            type=PackageType.PythonPkg,
            metadata=PythonPackage(
                name="unittest2",
                version="1.0,<3.0",
                author=None,
                author_email=None,
                platform=None,
                files=None,
                site_package_root_path=None,
                top_level_packages=None,
                direct_url_origin=None,
                dependencies=None,
            ),
            p_url="pkg:pypi/unittest2@1.0%2C%3C3.0",
            dependencies=None,
            found_by=None,
            is_dev=True,
        ),
    ]

    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_pipfile_deps(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        assert pkgs is not None
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
    assert pkgs == expected
