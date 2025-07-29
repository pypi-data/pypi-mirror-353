import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.javascript.parse_html_scripts import _get_location, parse_html_scripts
from labels.testing.utils.helpers import get_test_data_path


def test_get_location_with_coordinates() -> None:
    test_path = "/test/path"
    initial_location = Location(
        access_path=test_path,
        coordinates=Coordinates(
            real_path=test_path,
            line=1,
        ),
    )

    result = _get_location(initial_location, sourceline=5)

    assert result.coordinates is not None
    assert result.coordinates.line == 5
    assert result.coordinates.real_path == test_path
    assert result.access_path == test_path


def test_get_location_without_coordinates() -> None:
    test_path = "/test/path"
    initial_location = Location(
        access_path=test_path,
        coordinates=None,
    )

    result = _get_location(initial_location, sourceline=5)

    assert result == initial_location


def test_parse_html_scripts() -> None:
    test_data_path = get_test_data_path("dependencies/html/script_dependencies.html")
    expected_packages = [
        Package(
            name="react",
            version="17.0.2",
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        line=5,
                        real_path=test_data_path,
                    ),
                    access_path=test_data_path,
                ),
            ],
            language=Language.JAVASCRIPT,
            type=PackageType.NpmPkg,
            p_url="pkg:npm/react@17.0.2",
        ),
        Package(
            name="lodash",
            version="4.17.21",
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        line=6,
                        real_path=test_data_path,
                    ),
                    access_path=test_data_path,
                ),
            ],
            language=Language.JAVASCRIPT,
            type=PackageType.NpmPkg,
            p_url="pkg:npm/lodash@4.17.21",
        ),
    ]

    with Path(test_data_path).open(encoding="utf-8") as file:
        reader = LocationReadCloser(
            read_closer=file,
            location=Location(
                access_path=test_data_path,
                coordinates=Coordinates(
                    real_path=test_data_path,
                ),
            ),
        )
        packages, relationships = parse_html_scripts(None, None, reader)

    assert packages == expected_packages
    assert relationships == []


def test_parse_html_scripts_assertion_error() -> None:
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp:
        temp_path = Path(temp.name)
        temp.write("")
        temp.close()

        try:
            with temp_path.open("r") as file:
                reader = LocationReadCloser(
                    read_closer=file,
                    location=Location(
                        access_path=str(temp_path),
                        coordinates=Coordinates(
                            real_path=str(temp_path),
                        ),
                    ),
                )

                with patch.object(file, "read", side_effect=AssertionError()):
                    packages, relationships = parse_html_scripts(None, None, reader)

                assert packages == []
                assert relationships == []
        finally:
            temp_path.unlink(missing_ok=True)


def test_parse_html_scripts_none_html() -> None:
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp:
        temp_path = Path(temp.name)
        temp.write("invalid html")
        temp.close()

        try:
            with temp_path.open("r") as file:
                reader = LocationReadCloser(
                    read_closer=file,
                    location=Location(
                        access_path=str(temp_path),
                        coordinates=Coordinates(
                            real_path=str(temp_path),
                        ),
                    ),
                )

                with patch(
                    "labels.parsers.cataloger.javascript.parse_html_scripts.BeautifulSoup",
                    return_value=None,
                ):
                    packages, relationships = parse_html_scripts(None, None, reader)

                assert packages == []
                assert relationships == []
        finally:
            temp_path.unlink(missing_ok=True)


def test_parse_html_scripts_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    test_data_path = get_test_data_path("dependencies/html/script_dependencies.html")

    with (
        Path(test_data_path).open(encoding="utf-8") as file,
        patch("labels.model.package.Package.__init__") as mock_init,
    ):
        reader = LocationReadCloser(
            read_closer=file,
            location=Location(
                access_path=test_data_path,
                coordinates=Coordinates(
                    real_path=test_data_path,
                ),
            ),
        )

        mock_init.side_effect = ValidationError.from_exception_data(
            title="",
            line_errors=[
                InitErrorDetails(  # type: ignore[misc]
                    type="missing",
                    loc=("name",),
                    input=None,
                    ctx={},
                ),
            ],
        )

        packages, relationships = parse_html_scripts(None, None, reader)

        assert packages == []
        assert relationships == []
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


def test_parse_html_scripts_empty_name_or_version() -> None:
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.example.com/@1.2.3/dist/empty-name.js"></script>
        <script src="https://cdn.example.com/empty-version@/dist/lib.js"></script>
    </head>
    </html>
    """

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp:
        temp_path = Path(temp.name)
        temp.write(html_content)
        temp.close()

        try:
            with temp_path.open("r") as file:
                reader = LocationReadCloser(
                    read_closer=file,
                    location=Location(
                        access_path=str(temp_path),
                        coordinates=Coordinates(
                            real_path=str(temp_path),
                        ),
                    ),
                )

                packages, relationships = parse_html_scripts(None, None, reader)

                assert packages == []
                assert relationships == []
        finally:
            temp_path.unlink(missing_ok=True)
