from io import BytesIO, TextIOWrapper
from pathlib import Path

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.dotnet.parse_dotnet_exe_config import parse_dotnet_config_executable
from labels.testing.utils.helpers import get_test_data_path
from labels.testing.utils.pytest_marks import parametrize_sync
from labels.utils.file import new_location


def test_parse_dotnet_config_executable() -> None:
    test_data_path = get_test_data_path("dependencies/dotnet/my_project.exe.config")
    expected_packages: list[Package] = [
        Package(
            name="netframework",
            version="4.5.2",
            language=Language.DOTNET,
            licenses=[],
            locations=[
                Location(
                    scope=Scope.PROD,
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=4,
                    ),
                    access_path=test_data_path,
                    annotations={},
                    dependency_type=DependencyType.DIRECT,
                ),
            ],
            type=PackageType.DotnetPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=None,
            p_url="pkg:nuget/netframework@4.5.2",
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_dotnet_config_executable(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        assert pkgs == expected_packages


@parametrize_sync(
    args=["xml_content"],
    cases=[
        ["<configuration></configuration>"],
        ["<configuration><startup></startup></configuration>"],
        [
            "<configuration><startup><supportedruntime /></startup></configuration>",
        ],
        [
            '<configuration><startup><supportedruntime sku="invalid" /></startup></configuration>',
        ],
    ],
)
def test_parse_dotnet_config_executable_empty_result(xml_content: str, tmp_path: Path) -> None:
    test_file = tmp_path / "test.config"
    test_file.write_text(xml_content)

    with test_file.open(encoding="utf-8") as reader:
        pkgs, relationships = parse_dotnet_config_executable(
            None,
            None,
            LocationReadCloser(location=new_location(str(test_file)), read_closer=reader),
        )

        assert pkgs == []
        assert relationships == []


def test_parse_dotnet_config_executable_no_coordinates() -> None:
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <startup>
    <supportedRuntime sku=".NETFramework,Version=v4.5.2"/>
  </startup>
</configuration>"""

    bytes_io = BytesIO(xml_content.encode())
    reader = TextIOWrapper(bytes_io, encoding="utf-8")
    location = new_location("test.config")
    location.coordinates = None

    pkgs, relationships = parse_dotnet_config_executable(
        None,
        None,
        LocationReadCloser(location=location, read_closer=reader),
    )

    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.name == "netframework"
    assert pkg.version == "4.5.2"
    assert pkg.locations[0].coordinates is None
    assert relationships == []
