import logging
from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, Location, LocationReadCloser
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.dotnet.parse_dotnet_deps_json import (
    _get_relationships,
    parse_dotnet_deps_json,
)
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_dotnet_deps_json() -> None:
    test_data_path = get_test_data_path("dependencies/dotnet/TestLibrary.deps.json")
    expected_packages = [
        Package(
            name="TestLibrary",
            version="1.0.0",
            language=Language.DOTNET,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=9,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.DotnetPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:nuget/TestLibrary@1.0.0",
        ),
        Package(
            name="AWSSDK.Core",
            version="3.7.10.6",
            language=Language.DOTNET,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=22,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.DotnetPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:nuget/AWSSDK.Core@3.7.10.6",
        ),
        Package(
            name="Microsoft.Extensions.DependencyInjection",
            version="6.0.0",
            language=Language.DOTNET,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=30,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.DotnetPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:nuget/Microsoft.Extensions.DependencyInjection@6.0.0",
        ),
        Package(
            name="Microsoft.Extensions.DependencyInjection.Abstractions",
            version="6.0.0",
            language=Language.DOTNET,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=42,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.DotnetPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url=("pkg:nuget/Microsoft.Extensions.DependencyInjection.Abstractions@6.0.0"),
        ),
        Package(
            name="Microsoft.Extensions.Logging",
            version="6.0.0",
            language=Language.DOTNET,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=50,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.DotnetPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:nuget/Microsoft.Extensions.Logging@6.0.0",
        ),
        Package(
            name="Microsoft.Extensions.Logging.Abstractions",
            version="6.0.0",
            language=Language.DOTNET,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=65,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.DotnetPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:nuget/Microsoft.Extensions.Logging.Abstractions@6.0.0",
        ),
        Package(
            name="Microsoft.Extensions.Options",
            version="6.0.0",
            language=Language.DOTNET,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=73,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.DotnetPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:nuget/Microsoft.Extensions.Options@6.0.0",
        ),
        Package(
            name="Microsoft.Extensions.Primitives",
            version="6.0.0",
            language=Language.DOTNET,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=85,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.DotnetPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:nuget/Microsoft.Extensions.Primitives@6.0.0",
        ),
        Package(
            name="Newtonsoft.Json",
            version="13.0.1",
            language=Language.DOTNET,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=96,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.DotnetPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:nuget/Newtonsoft.Json@13.0.1",
        ),
        Package(
            name="Serilog",
            version="2.10.0",
            language=Language.DOTNET,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=104,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.DotnetPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:nuget/Serilog@2.10.0",
        ),
        Package(
            name="Serilog.Sinks.Console",
            version="4.0.1",
            language=Language.DOTNET,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=112,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.DotnetPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:nuget/Serilog.Sinks.Console@4.0.1",
        ),
        Package(
            name="System.Diagnostics.DiagnosticSource",
            version="6.0.0",
            language=Language.DOTNET,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=123,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.DotnetPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:nuget/System.Diagnostics.DiagnosticSource@6.0.0",
        ),
        Package(
            name="System.Runtime.CompilerServices.Unsafe",
            version="6.0.0",
            language=Language.DOTNET,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=128,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.DotnetPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:nuget/System.Runtime.CompilerServices.Unsafe@6.0.0",
        ),
        Package(
            name="TestCommon",
            version="1.0.0",
            language=Language.DOTNET,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=129,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.DotnetPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:nuget/TestCommon@1.0.0",
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, relations = parse_dotnet_deps_json(
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


def test_get_relationships_invalid_dependencies() -> None:
    package_a = Package(
        name="PackageA",
        version="1.0.0",
        language=Language.DOTNET,
        licenses=[],
        locations=[],
        type=PackageType.DotnetPkg,
        p_url="pkg:nuget/PackageA@1.0.0",
    )
    package_b = Package(
        name="PackageB",
        version="2.0.0",
        language=Language.DOTNET,
        licenses=[],
        locations=[],
        type=PackageType.DotnetPkg,
        p_url="pkg:nuget/PackageB@2.0.0",
    )

    invalid_dependencies: dict[str, ParsedValue] = {
        "PackageA": "not_a_dict",
        "PackageB": IndexedDict(),
    }
    relationships = _get_relationships([package_a, package_b], invalid_dependencies)
    assert len(relationships) == 0


def test_parse_dotnet_deps_json_no_targets(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)

    content = b'{"targets": "invalid"}'

    reader = TextIOWrapper(BytesIO(content), encoding="utf-8")

    pkgs, relations = parse_dotnet_deps_json(
        None,
        None,
        LocationReadCloser(location=new_location("test.deps.json"), read_closer=reader),
    )

    assert len(pkgs) == 0
    assert len(relations) == 0
    assert "No targets found in package JSON" in caplog.text


def test_get_relationships_package_not_found() -> None:
    package_a = Package(
        name="PackageA",
        version="1.0.0",
        language=Language.DOTNET,
        licenses=[],
        locations=[],
        type=PackageType.DotnetPkg,
        p_url="pkg:nuget/PackageA@1.0.0",
    )

    dependencies: dict[str, ParsedValue] = {
        "NonExistentPackage": IndexedDict(),
    }

    relationships = _get_relationships([package_a], dependencies)
    assert len(relationships) == 0


def test_parse_dotnet_deps_json_invalid_package_key(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)

    content = b"""{
        "targets": {
            "net6.0": {
                "invalid_key": {
                    "dependencies": {}
                }
            }
        }
    }"""

    reader = TextIOWrapper(BytesIO(content), encoding="utf-8")

    pkgs, relations = parse_dotnet_deps_json(
        None,
        None,
        LocationReadCloser(location=new_location("test.deps.json"), read_closer=reader),
    )

    assert len(pkgs) == 0
    assert len(relations) == 0


def test_parse_dotnet_deps_json_invalid_package_value(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)

    content = b"""{
        "targets": {
            "net6.0": {
                "PackageA/1.0.0": "invalid_value"
            }
        }
    }"""

    reader = TextIOWrapper(BytesIO(content), encoding="utf-8")

    pkgs, relations = parse_dotnet_deps_json(
        None,
        None,
        LocationReadCloser(location=new_location("test.deps.json"), read_closer=reader),
    )

    assert len(pkgs) == 0
    assert len(relations) == 0


def test_parse_dotnet_deps_json_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)

    content = b"""{
        "targets": {
            "net6.0": {
                "PackageA/1.0.0": {
                    "dependencies": {}
                }
            }
        }
    }"""

    reader = TextIOWrapper(BytesIO(content), encoding="utf-8")

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

        pkgs, relations = parse_dotnet_deps_json(
            None,
            None,
            LocationReadCloser(location=new_location("test.deps.json"), read_closer=reader),
        )

        assert len(pkgs) == 0
        assert len(relations) == 0
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


def test_parse_dotnet_deps_json_without_coordinates() -> None:
    content = b"""{
        "targets": {
            "net6.0": {
                "PackageA/1.0.0": {
                    "dependencies": {}
                }
            }
        }
    }"""

    reader = TextIOWrapper(BytesIO(content), encoding="utf-8")
    location = Location(
        coordinates=None,
        access_path="test.deps.json",
        annotations={},
    )

    pkgs, _ = parse_dotnet_deps_json(
        None,
        None,
        LocationReadCloser(location=location, read_closer=reader),
    )

    assert len(pkgs) == 1
    assert pkgs[0].locations[0].coordinates is None
