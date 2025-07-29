from io import BytesIO, TextIOWrapper
from pathlib import Path

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.github.parse_github_actions import parse_github_actions_deps
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_github_actions() -> None:
    test_data_path = get_test_data_path("dependencies/.github/workflows/dev.yaml")
    expected_packages = [
        Package(
            name="aws-actions/configure-aws-credentials",
            version="v1",
            language=Language.GITHUB_ACTIONS,
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
                    reachable_cves=[],
                ),
            ],
            type=PackageType.GithubActionPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:github/aws-actions/configure-aws-credentials@v1",
        ),
        Package(
            name="actions/checkout",
            version="v2",
            language=Language.GITHUB_ACTIONS,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=43,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.GithubActionPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:github/actions/checkout@v2",
        ),
        Package(
            name="ruby/setup-ruby",
            version="v1",
            language=Language.GITHUB_ACTIONS,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=47,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.GithubActionPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:github/ruby/setup-ruby@v1",
        ),
        Package(
            name="gradle/gradle-build-action",
            version="2.4.0",
            language=Language.GITHUB_ACTIONS,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=52,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.GithubActionPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:github/gradle/gradle-build-action@2.4.0",
        ),
        Package(
            name="actions/setup-node",
            version="v1",
            language=Language.GITHUB_ACTIONS,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=60,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.GithubActionPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:github/actions/setup-node@v1",
        ),
    ]

    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_github_actions_deps(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        assert pkgs == expected_packages


def test_parse_github_actions_with_invalid_job() -> None:
    yaml_content = """
name: Test Workflow

on:
  push:
    branches: [ main ]

jobs:
  invalid-job: "this is not a dictionary"
"""
    expected_packages: list[Package] = []

    bytes_io = BytesIO(yaml_content.encode("utf-8"))
    reader = TextIOWrapper(bytes_io)
    pkgs, _ = parse_github_actions_deps(
        None,
        None,
        LocationReadCloser(location=new_location("test.yaml"), read_closer=reader),
    )
    assert pkgs == expected_packages


def test_parse_github_actions_with_invalid_steps() -> None:
    yaml_content = """
name: Test Workflow

on:
  push:
    branches: [ main ]

jobs:
  invalid-steps-job:
    runs-on: ubuntu-latest
    steps: "this is not a list"
"""
    expected_packages: list[Package] = []

    bytes_io = BytesIO(yaml_content.encode("utf-8"))
    reader = TextIOWrapper(bytes_io)
    pkgs, _ = parse_github_actions_deps(
        None,
        None,
        LocationReadCloser(location=new_location("test.yaml"), read_closer=reader),
    )
    assert pkgs == expected_packages


def test_parse_github_actions_with_empty_content() -> None:
    yaml_content = ""
    expected_packages: list[Package] = []

    bytes_io = BytesIO(yaml_content.encode("utf-8"))
    reader = TextIOWrapper(bytes_io)
    pkgs, _ = parse_github_actions_deps(
        None,
        None,
        LocationReadCloser(location=new_location("test.yaml"), read_closer=reader),
    )
    assert pkgs == expected_packages


def test_parse_github_actions_with_invalid_jobs() -> None:
    yaml_content = """
name: Test Workflow

on:
  push:
    branches: [ main ]

jobs: "this is not a dictionary"
"""
    expected_packages: list[Package] = []

    bytes_io = BytesIO(yaml_content.encode("utf-8"))
    reader = TextIOWrapper(bytes_io)
    pkgs, _ = parse_github_actions_deps(
        None,
        None,
        LocationReadCloser(location=new_location("test.yaml"), read_closer=reader),
    )
    assert pkgs == expected_packages


def test_parse_github_actions_without_coordinates() -> None:
    yaml_content = """
name: Test Workflow

on:
  push:
    branches: [ main ]

jobs:
  test-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
"""
    expected_packages = [
        Package(
            name="actions/checkout",
            version="v2",
            language=Language.GITHUB_ACTIONS,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=None,
                    access_path="test.yaml",
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.GithubActionPkg,
            metadata=None,
            p_url="pkg:github/actions/checkout@v2",
        ),
    ]

    bytes_io = BytesIO(yaml_content.encode("utf-8"))
    reader = TextIOWrapper(bytes_io)
    location = new_location("test.yaml")
    location.coordinates = None
    pkgs, _ = parse_github_actions_deps(
        None,
        None,
        LocationReadCloser(location=location, read_closer=reader),
    )
    assert pkgs == expected_packages


def test_parse_github_actions_with_invalid_dep_format() -> None:
    yaml_content = """
name: Test Workflow

on:
  push:
    branches: [ main ]

jobs:
  test-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout
      - uses: actions/setup-node@v1@extra
"""
    expected_packages = [
        Package(
            name="actions/setup-node@v1",
            version="extra",
            language=Language.GITHUB_ACTIONS,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path="test.yaml",
                        file_system_id=None,
                        line=13,
                    ),
                    access_path="test.yaml",
                    annotations={},
                    dependency_type=DependencyType.UNKNOWN,
                    reachable_cves=[],
                ),
            ],
            type=PackageType.GithubActionPkg,
            metadata=None,
            p_url="pkg:github/actions/setup-node%40v1@extra",
        ),
    ]

    bytes_io = BytesIO(yaml_content.encode("utf-8"))
    reader = TextIOWrapper(bytes_io)
    pkgs, _ = parse_github_actions_deps(
        None,
        None,
        LocationReadCloser(location=new_location("test.yaml"), read_closer=reader),
    )
    assert pkgs == expected_packages
