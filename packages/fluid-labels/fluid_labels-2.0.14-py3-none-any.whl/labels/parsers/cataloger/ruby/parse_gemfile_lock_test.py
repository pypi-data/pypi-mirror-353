from io import BytesIO, TextIOWrapper
from pathlib import Path

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.ruby.parse_gemfile_lock import build_location, parse_gemfile_lock
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_gem_file_lock() -> None:
    test_data_path = get_test_data_path("dependencies/ruby/Gemfile.lock")
    expected_packages = [
        Package(
            name="actionmailer",
            version="4.1.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=16,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUBY,
            licenses=[],
            type=PackageType.GemPkg,
            metadata=None,
            p_url="pkg:gem/actionmailer@4.1.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="actionpack",
            version="4.1.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=20,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUBY,
            licenses=[],
            type=PackageType.GemPkg,
            metadata=None,
            p_url="pkg:gem/actionpack@4.1.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="actionview",
            version="4.1.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=25,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUBY,
            licenses=[],
            type=PackageType.GemPkg,
            metadata=None,
            p_url="pkg:gem/actionview@4.1.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="activemodel",
            version="4.1.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=29,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUBY,
            licenses=[],
            type=PackageType.GemPkg,
            metadata=None,
            p_url="pkg:gem/activemodel@4.1.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="activerecord",
            version="4.1.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=32,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUBY,
            licenses=[],
            type=PackageType.GemPkg,
            metadata=None,
            p_url="pkg:gem/activerecord@4.1.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="activesupport",
            version="4.1.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=36,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUBY,
            licenses=[],
            type=PackageType.GemPkg,
            metadata=None,
            p_url="pkg:gem/activesupport@4.1.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="arel",
            version="5.0.1.20140414130214",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=42,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUBY,
            licenses=[],
            type=PackageType.GemPkg,
            metadata=None,
            p_url="pkg:gem/arel@5.0.1.20140414130214",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="bootstrap-sass",
            version="3.1.1.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=43,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUBY,
            licenses=[],
            type=PackageType.GemPkg,
            metadata=None,
            p_url="pkg:gem/bootstrap-sass@3.1.1.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="builder",
            version="3.2.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=45,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUBY,
            licenses=[],
            type=PackageType.GemPkg,
            metadata=None,
            p_url="pkg:gem/builder@3.2.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="coffee-rails",
            version="4.0.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=46,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUBY,
            licenses=[],
            type=PackageType.GemPkg,
            metadata=None,
            p_url="pkg:gem/coffee-rails@4.0.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="coffee-script",
            version="2.2.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=49,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUBY,
            licenses=[],
            type=PackageType.GemPkg,
            metadata=None,
            p_url="pkg:gem/coffee-script@2.2.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="coffee-script-source",
            version="1.7.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=52,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUBY,
            licenses=[],
            type=PackageType.GemPkg,
            metadata=None,
            p_url="pkg:gem/coffee-script-source@1.7.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_gemfile_lock(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        assert pkgs == expected_packages


def test_build_location_without_coordinates() -> None:
    reader = LocationReadCloser(
        read_closer=TextIOWrapper(BytesIO(b"")),
        location=Location(
            coordinates=None,
            dependency_type=DependencyType.DIRECT,
            access_path="test/path",
            annotations={},
        ),
    )

    result = build_location(reader, 42)

    assert result.scope == Scope.PROD
    assert result.dependency_type == DependencyType.DIRECT
    assert result.coordinates is None


def test_parse_gem_file_lock_empty_content() -> None:
    content = ""
    test_path = "test/path"

    with TextIOWrapper(BytesIO(content.encode())) as reader:
        location = Location(
            coordinates=Coordinates(
                real_path=test_path,
                file_system_id=None,
                line=None,
            ),
            dependency_type=DependencyType.DIRECT,
            access_path=test_path,
            annotations={},
        )
        pkgs, relationships = parse_gemfile_lock(
            None,
            None,
            LocationReadCloser(location=location, read_closer=reader),
        )

        assert len(pkgs) == 0
        assert len(relationships) == 0
