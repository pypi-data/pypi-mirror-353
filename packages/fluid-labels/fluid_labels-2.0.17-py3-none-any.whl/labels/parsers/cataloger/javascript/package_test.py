from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, Location
from labels.model.indexables import FileCoordinate, IndexedDict, ParsedValue, Position
from labels.parsers.cataloger.javascript.model import NpmPackageLockEntry
from labels.parsers.cataloger.javascript.package import (
    new_package_lock_v1,
    new_package_lock_v2,
    package_url,
)


def create_test_indexed_dict(
    version: str,
    resolved: str = "https://registry.npmjs.org/test-package/-/test-package-1.2.3.tgz",
    integrity: str = "sha512-test",
    *,
    dev: bool = False,
) -> IndexedDict[str, ParsedValue]:
    value = IndexedDict[str, ParsedValue]()
    value.position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=1),
    )

    value[
        (
            "version",
            Position(
                start=FileCoordinate(line=1, column=1),
                end=FileCoordinate(line=1, column=1),
            ),
        )
    ] = (
        version,
        Position(
            start=FileCoordinate(line=1, column=1),
            end=FileCoordinate(line=1, column=1),
        ),
    )
    value[
        (
            "resolved",
            Position(
                start=FileCoordinate(line=1, column=1),
                end=FileCoordinate(line=1, column=1),
            ),
        )
    ] = (
        resolved,
        Position(
            start=FileCoordinate(line=1, column=1),
            end=FileCoordinate(line=1, column=1),
        ),
    )
    value[
        (
            "integrity",
            Position(
                start=FileCoordinate(line=1, column=1),
                end=FileCoordinate(line=1, column=1),
            ),
        )
    ] = (
        integrity,
        Position(
            start=FileCoordinate(line=1, column=1),
            end=FileCoordinate(line=1, column=1),
        ),
    )
    value[
        (
            "dev",
            Position(
                start=FileCoordinate(line=1, column=1),
                end=FileCoordinate(line=1, column=1),
            ),
        )
    ] = (
        dev,
        Position(
            start=FileCoordinate(line=1, column=1),
            end=FileCoordinate(line=1, column=1),
        ),
    )

    return value


def test_new_package_lock_v1_with_npm_alias() -> None:
    location = Location(
        coordinates=Coordinates(
            real_path="package-lock.json",
            line=1,
        ),
        access_path="package-lock.json",
    )
    name = "test-package"
    value = create_test_indexed_dict(
        version="npm:@test-scope/test-package@1.2.3",
        resolved="https://registry.npmjs.org/@test-scope/test-package/-/test-package-1.2.3.tgz",
    )

    result = new_package_lock_v1(location, name, value, is_transitive=False)

    assert result is not None
    assert result.name == "@test-scope/test-package"
    assert result.version == "1.2.3"
    assert result.metadata is not None
    assert isinstance(result.metadata, NpmPackageLockEntry)
    assert (
        result.metadata.resolved
        == "https://registry.npmjs.org/@test-scope/test-package/-/test-package-1.2.3.tgz"
    )
    assert result.metadata.integrity == "sha512-test"
    assert not result.metadata.is_dev


def test_new_package_lock_v1_without_coordinates() -> None:
    location = Location(
        coordinates=None,
        access_path="package-lock.json",
    )
    name = "test-package"
    value = create_test_indexed_dict(
        version="npm:@test-scope/test-package@1.2.3",
        resolved="https://registry.npmjs.org/@test-scope/test-package/-/test-package-1.2.3.tgz",
    )

    result = new_package_lock_v1(location, name, value, is_transitive=False)

    assert result is not None
    assert result.name == "@test-scope/test-package"
    assert result.version == "1.2.3"
    assert result.metadata is not None
    assert isinstance(result.metadata, NpmPackageLockEntry)
    assert (
        result.metadata.resolved
        == "https://registry.npmjs.org/@test-scope/test-package/-/test-package-1.2.3.tgz"
    )
    assert result.metadata.integrity == "sha512-test"
    assert not result.metadata.is_dev
    assert result.locations[0].coordinates is None


def test_new_package_lock_v1_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    location = Location(
        coordinates=Coordinates(
            real_path="package-lock.json",
            line=1,
        ),
        access_path="package-lock.json",
    )
    name = "test-package"
    value = create_test_indexed_dict(
        version="npm:@test-scope/test-package@1.2.3",
        resolved="https://registry.npmjs.org/@test-scope/test-package/-/test-package-1.2.3.tgz",
    )

    with patch("labels.model.package.Package.__init__") as mock_init:
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

        result = new_package_lock_v1(location, name, value, is_transitive=False)

        assert result is None
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


def test_new_package_lock_v2_without_coordinates() -> None:
    location = Location(
        coordinates=None,
        access_path="package-lock.json",
    )
    name = "test-package"
    value = create_test_indexed_dict(version="1.2.3")

    result = new_package_lock_v2(location, name, value, is_transitive=False)

    assert result is not None
    assert result.name == "test-package"
    assert result.version == "1.2.3"
    assert result.metadata is not None
    assert isinstance(result.metadata, NpmPackageLockEntry)
    assert (
        result.metadata.resolved
        == "https://registry.npmjs.org/test-package/-/test-package-1.2.3.tgz"
    )
    assert result.metadata.integrity == "sha512-test"
    assert not result.metadata.is_dev
    assert result.locations[0].coordinates is None


def test_new_package_lock_v2_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    location = Location(
        coordinates=Coordinates(
            real_path="package-lock.json",
            line=1,
        ),
        access_path="package-lock.json",
    )
    name = "test-package"
    value = create_test_indexed_dict(version="1.2.3")

    with patch("labels.model.package.Package.__init__") as mock_init:
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

        result = new_package_lock_v2(location, name, value, is_transitive=False)

        assert result is None
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


def test_package_url_with_empty_name() -> None:
    result = package_url("", "1.2.3")

    assert result == ""
