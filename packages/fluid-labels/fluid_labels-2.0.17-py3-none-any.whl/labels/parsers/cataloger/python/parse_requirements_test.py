from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails
from requirements.requirement import Requirement

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.python import parse_requirements
from labels.parsers.cataloger.python.model import PythonRequirementsEntry
from labels.parsers.cataloger.python.parse_requirements import (
    create_package,
    parse_requirements_txt,
    parse_url,
    prepare_location,
)
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_requirements() -> None:
    test_data_path = get_test_data_path("dependencies/python/requires/requirements.txt")
    expected = [
        Package(
            name="flask",
            version="4.0.0",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=1,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    reachable_cves=[],
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PythonRequirementsEntry(
                name="flask",
                extras=[],
                markers="pkg:pypi/flask@4.0.0",
                version_constraint="== 4.0.0",
            ),
            p_url="pkg:pypi/flask@4.0.0",
        ),
        Package(
            name="foo",
            version="1.0.0",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=4,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    reachable_cves=[],
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PythonRequirementsEntry(
                name="foo",
                extras=[],
                markers="pkg:pypi/foo@1.0.0",
                version_constraint="== 1.0.0",
            ),
            p_url="pkg:pypi/foo@1.0.0",
        ),
        Package(
            name="SomeProject",
            version="5.4",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=10,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    reachable_cves=[],
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PythonRequirementsEntry(
                name="SomeProject",
                extras=[],
                markers="pkg:pypi/someproject@5.4",
                version_constraint="== 5.4",
            ),
            p_url="pkg:pypi/someproject@5.4",
        ),
        Package(
            name="numpy",
            version=">=3.4.1",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=13,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    reachable_cves=[],
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PythonRequirementsEntry(
                name="numpy",
                extras=[],
                markers="pkg:pypi/numpy@%3E%3D3.4.1",
                version_constraint=">= 3.4.1",
            ),
            p_url="pkg:pypi/numpy@%3E%3D3.4.1",
        ),
        Package(
            name="Mopidy-Dirble",
            version="1.1",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=14,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    reachable_cves=[],
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PythonRequirementsEntry(
                name="Mopidy-Dirble",
                extras=[],
                markers="pkg:pypi/mopidy-dirble@1.1",
                version_constraint="~= 1.1",
            ),
            p_url="pkg:pypi/mopidy-dirble@1.1",
        ),
        Package(
            name="argh",
            version="0.26.2",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=15,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    reachable_cves=[],
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PythonRequirementsEntry(
                name="argh",
                extras=[],
                markers="pkg:pypi/argh@0.26.2",
                version_constraint="== 0.26.2",
            ),
            p_url="pkg:pypi/argh@0.26.2",
        ),
        Package(
            name="argh",
            version="0.26.3",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=18,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    reachable_cves=[],
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PythonRequirementsEntry(
                name="argh",
                extras=[],
                markers="pkg:pypi/argh@0.26.3",
                version_constraint="== 0.26.3",
            ),
            p_url="pkg:pypi/argh@0.26.3",
        ),
        Package(
            name="celery",
            version="4.4.7",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=22,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    reachable_cves=[],
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PythonRequirementsEntry(
                name="celery",
                extras=["pytest", "redis"],
                markers="pkg:pypi/celery@4.4.7",
                version_constraint="== 4.4.7",
            ),
            p_url="pkg:pypi/celery@4.4.7",
        ),
        Package(
            name="requests",
            version="2.8.*",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=23,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    reachable_cves=[],
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PythonRequirementsEntry(
                name="requests",
                extras=["security"],
                markers="pkg:pypi/requests@2.8.%2A",
                version_constraint="== 2.8.*",
            ),
            p_url="pkg:pypi/requests@2.8.%2A",
        ),
        Package(
            name="python-json-logger",
            version="3.2.0",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    dependency_type=DependencyType.DIRECT,
                    scope=Scope.DEV,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=25,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    reachable_cves=[],
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PythonRequirementsEntry(
                name="python-json-logger",
                extras=["dev"],
                markers="pkg:pypi/python-json-logger@3.2.0",
                version_constraint="== 3.2.0",
            ),
            p_url="pkg:pypi/python-json-logger@3.2.0",
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_requirements_txt(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        assert pkgs is not None
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
    assert pkgs == expected


def test_requirements_unicode_decode_error() -> None:
    invalid_content = b"\xff\xfe\x00\x00"
    reader = LocationReadCloser(
        location=new_location("requirements.txt"),
        read_closer=TextIOWrapper(BytesIO(invalid_content)),
    )

    pkgs, rels = parse_requirements_txt(None, None, reader)
    assert pkgs == []
    assert rels == []


def test_requirements_invalid_version_specs() -> None:
    content = """# Package with invalid version specs
flask!=1.0.0
# Package with no version specs
flask
# Package with invalid operator
flask?=1.0.0
"""
    reader = LocationReadCloser(
        location=new_location("requirements.txt"),
        read_closer=TextIOWrapper(BytesIO(content.encode("utf-8"))),
    )

    pkgs, rels = parse_requirements_txt(None, None, reader)
    assert pkgs == []
    assert rels == []


@mocks(
    mocks=[
        Mock(
            module=parse_requirements,
            target="create_package",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_requirements_create_package_returns_none() -> None:
    content = """# Valid dependency that will be skipped due to create_package returning None
flask==1.0.0
"""
    reader = LocationReadCloser(
        location=new_location("requirements.txt"),
        read_closer=TextIOWrapper(BytesIO(content.encode("utf-8"))),
    )

    pkgs, rels = parse_requirements_txt(None, None, reader)
    assert pkgs == []
    assert rels == []


@mocks(
    mocks=[
        Mock(
            module=parse_requirements,
            target="get_parsed_dependency",
            target_type="sync",
            expected=("", "1.0.0", None, False),
        ),
    ],
)
async def test_requirements_empty_name() -> None:
    content = """# Valid dependency
requests==2.8.0
"""
    reader = LocationReadCloser(
        location=new_location("requirements.txt"),
        read_closer=TextIOWrapper(BytesIO(content.encode("utf-8"))),
    )

    pkgs, rels = parse_requirements_txt(None, None, reader)
    assert len(pkgs) == 0
    assert rels == []


def test_prepare_location_no_coordinates() -> None:
    location = new_location("requirements.txt")
    location.coordinates = None
    result = prepare_location(location, 1)
    assert result.coordinates is None
    assert result == location


async def test_create_package_malformed_warning(caplog: pytest.LogCaptureFixture) -> None:
    location = new_location("requirements.txt")
    location.coordinates = Coordinates(real_path="./")
    req = Requirement.parse("test==1.0.0")

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

        result = create_package("test", "1.0.0", req, location, "pkg:pypi/test@1.0.0")
        assert result is None
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


def test_parse_url_no_at() -> None:
    line = "git+https://github.com/user/repo"
    result = parse_url(line)
    assert result == ""


def test_parse_url_with_at_no_git() -> None:
    line = "package@1.0.0"
    result = parse_url(line)
    assert result == ""


def test_parse_url_with_git_after_at() -> None:
    line = "package@git+https://github.com/user/repo"
    result = parse_url(line)
    assert result == "git+https://github.com/user/repo"


def test_parse_url_with_git_before_at() -> None:
    line = "git+https://github.com/user/repo@1.0.0"
    result = parse_url(line)
    assert result == "git+https://github.com/user/repo@1.0.0"


def test_parse_url_with_multiple_at() -> None:
    line = "git+https://github.com/user/repo@branch@1.0.0"
    result = parse_url(line)
    assert result == "git+https://github.com/user/repo@branch@1.0.0"
