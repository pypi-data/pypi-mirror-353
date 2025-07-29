from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, Location
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.python.model import PythonDirectURLOriginInfo, PythonPackage
from labels.parsers.cataloger.python.package import new_package_for_package
from labels.parsers.cataloger.python.parse_wheel_egg_metadata import ParsedData


def test_new_package_for_package_without_name_or_version() -> None:
    data = ParsedData(
        python_package=PythonPackage(name="", version="1.0.0"),
        licenses="",
        license_file="",
        license_expresion="",
        license_location=None,
    )
    sources = Location(access_path="./", coordinates=Coordinates(real_path="./"))

    result = new_package_for_package(data, sources)

    assert result is None


def test_new_package_for_package_with_valid_data() -> None:
    data = ParsedData(
        python_package=PythonPackage(name="test-package", version="1.0.0"),
        licenses="",
        license_file="",
        license_expresion="",
        license_location=None,
    )
    sources = Location(access_path="./", coordinates=Coordinates(real_path="./"))

    result = new_package_for_package(data, sources)

    assert isinstance(result, Package)
    assert result.name == "test-package"
    assert result.version == "1.0.0"
    assert result.language == Language.PYTHON
    assert result.type == PackageType.PythonPkg
    assert result.locations == [sources]
    assert result.licenses == []


def test_new_package_for_package_with_vcs_url() -> None:
    python_package = PythonPackage(
        name="test-package",
        version="1.0.0",
        direct_url_origin=PythonDirectURLOriginInfo(
            vcs="git",
            url="https://github.com/test/repo",
            commit_id="abc123",
        ),
    )
    data = ParsedData(
        python_package=python_package,
        licenses="",
        license_file="",
        license_expresion="",
        license_location=None,
    )
    sources = Location(access_path="./", coordinates=Coordinates(real_path="./"))

    result = new_package_for_package(data, sources)

    assert isinstance(result, Package)
    assert (
        result.p_url
        == "pkg:pypi/test-package@1.0.0?vcs_url=git%2Bhttps://github.com/test/repo%40abc123"
    )


async def test_new_package_malformed_warning(caplog: pytest.LogCaptureFixture) -> None:
    data = ParsedData(
        python_package=PythonPackage(name="test-package", version="1.0.0"),
        licenses="",
        license_file="",
        license_expresion="",
        license_location=None,
    )
    sources = Location(access_path="./", coordinates=Coordinates(real_path="./"))

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

        result = new_package_for_package(data, sources)

        assert result is None
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )
