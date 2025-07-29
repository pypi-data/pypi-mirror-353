from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.dotnet.parse_dotnet_package_config import parse_dotnet_pkgs_config
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_dotnet_pkgs_config() -> None:
    test_data_path = get_test_data_path("dependencies/dotnet/packages.config")
    expected_packages = [
        Package(
            name="ClosedXML",
            version="0.94.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=3,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/ClosedXML@0.94.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="DocumentFormat.OpenXml",
            version="2.7.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=4,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/DocumentFormat.OpenXml@2.7.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="ExcelDataReader",
            version="3.6.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=5,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/ExcelDataReader@3.6.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="ExcelDataReader.DataSet",
            version="3.6.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=6,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/ExcelDataReader.DataSet@3.6.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="ExcelNumberFormat",
            version="1.0.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=7,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/ExcelNumberFormat@1.0.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="FastMember",
            version="1.3.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=8,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/FastMember@1.3.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="jQuery",
            version="3.4.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=9,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/jQuery@3.4.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="Logs.Management",
            version="1.0.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=10,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/Logs.Management@1.0.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="Microsoft.Azure.Amqp",
            version="2.4.9",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=11,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/Microsoft.Azure.Amqp@2.4.9",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="Microsoft.Azure.ServiceBus",
            version="5.1.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=12,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/Microsoft.Azure.ServiceBus@5.1.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="Microsoft.Azure.Services.AppAuthentication",
            version="1.0.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=13,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/Microsoft.Azure.Services.AppAuthentication@1.0.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="Microsoft.IdentityModel.Clients.ActiveDirectory",
            version="3.14.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=14,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url=("pkg:nuget/Microsoft.IdentityModel.Clients.ActiveDirectory@3.14.2"),
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="Microsoft.IdentityModel.JsonWebTokens",
            version="5.4.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=15,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/Microsoft.IdentityModel.JsonWebTokens@5.4.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="Microsoft.IdentityModel.Logging",
            version="5.4.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=16,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/Microsoft.IdentityModel.Logging@5.4.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="Microsoft.IdentityModel.Tokens",
            version="5.4.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=17,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/Microsoft.IdentityModel.Tokens@5.4.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="Microsoft.Rest.ClientRuntime",
            version="2.3.18",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=18,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/Microsoft.Rest.ClientRuntime@2.3.18",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="Microsoft.Rest.ClientRuntime.Azure",
            version="3.3.18",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=19,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/Microsoft.Rest.ClientRuntime.Azure@3.3.18",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="Newtonsoft.Json",
            version="12.0.3",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=20,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/Newtonsoft.Json@12.0.3",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="System.Diagnostics.DiagnosticSource",
            version="4.5.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=21,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/System.Diagnostics.DiagnosticSource@4.5.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="System.IdentityModel.Tokens.Jwt",
            version="5.4.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=22,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/System.IdentityModel.Tokens.Jwt@5.4.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="System.IO",
            version="4.1.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=23,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/System.IO@4.1.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="System.Net.WebSockets",
            version="4.0.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=24,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/System.Net.WebSockets@4.0.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="System.Net.WebSockets.Client",
            version="4.0.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=25,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/System.Net.WebSockets.Client@4.0.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="System.Runtime",
            version="4.1.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=26,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/System.Runtime@4.1.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="System.Runtime.Serialization.Primitives",
            version="4.1.1",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=27,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/System.Runtime.Serialization.Primitives@4.1.1",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="System.Security.Cryptography.Algorithms",
            version="4.2.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=28,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/System.Security.Cryptography.Algorithms@4.2.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="System.Security.Cryptography.Encoding",
            version="4.0.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=29,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/System.Security.Cryptography.Encoding@4.0.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="System.Security.Cryptography.Primitives",
            version="4.0.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=30,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/System.Security.Cryptography.Primitives@4.0.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="System.Security.Cryptography.X509Certificates",
            version="4.1.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=31,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url=("pkg:nuget/System.Security.Cryptography.X509Certificates@4.1.0"),
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="Wire",
            version="1.0.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=get_test_data_path("dependencies/dotnet/packages.config"),
                        file_system_id=None,
                        line=32,
                    ),
                    dependency_type=DependencyType.DIRECT,
                    access_path=get_test_data_path("dependencies/dotnet/packages.config"),
                    annotations={},
                ),
            ],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url="pkg:nuget/Wire@1.0.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_dotnet_pkgs_config(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        assert pkgs == expected_packages


def test_parse_dotnet_pkgs_config_missing_fields() -> None:
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<packages>
  <package id="ValidPackage" version="1.0.0" />
  <package id="" version="2.0.0" />
  <package id="NoVersion" />
  <package version="3.0.0" />
</packages>"""

    bytes_io = BytesIO(xml_content.encode())
    reader = TextIOWrapper(bytes_io, encoding="utf-8")
    location = new_location("test_packages.config")

    pkgs, _ = parse_dotnet_pkgs_config(
        None,
        None,
        LocationReadCloser(location=location, read_closer=reader),
    )

    assert len(pkgs) == 1
    assert pkgs[0].name == "ValidPackage"
    assert pkgs[0].version == "1.0.0"


def test_parse_dotnet_pkgs_config_no_coordinates() -> None:
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<packages>
  <package id="TestPackage" version="1.0.0" />
</packages>"""

    bytes_io = BytesIO(xml_content.encode())
    reader = TextIOWrapper(bytes_io, encoding="utf-8")

    location = new_location("test.config")
    location.coordinates = None

    pkgs, _ = parse_dotnet_pkgs_config(
        None,
        None,
        LocationReadCloser(location=location, read_closer=reader),
    )

    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.name == "TestPackage"
    assert pkg.version == "1.0.0"
    assert pkg.locations[0].coordinates is None


def test_parse_dotnet_pkgs_config_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<packages>
  <package id="TestPackage" version="1.0.0" />
</packages>"""

    bytes_io = BytesIO(xml_content.encode())
    reader = TextIOWrapper(bytes_io, encoding="utf-8")
    location = new_location("test.config")

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

        pkgs, _ = parse_dotnet_pkgs_config(
            None,
            None,
            LocationReadCloser(location=location, read_closer=reader),
        )

        assert len(pkgs) == 0
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )
