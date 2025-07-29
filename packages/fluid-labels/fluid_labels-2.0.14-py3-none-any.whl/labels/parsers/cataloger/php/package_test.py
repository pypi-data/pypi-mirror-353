from labels.model.file import DependencyType, Location
from labels.model.indexables import FileCoordinate, IndexedDict, ParsedValue, Position
from labels.parsers.cataloger.php.package import new_package_from_composer, package_url
from labels.testing.utils.pytest_methods import raises


def test_package_url_simple_name() -> None:
    result = package_url("monolog", "2.0.0")
    expected = "pkg:composer/monolog@2.0.0"
    assert result == expected


def test_package_url_with_vendor() -> None:
    result = package_url("monolog/monolog", "2.0.0")
    expected = "pkg:composer/monolog/monolog@2.0.0"
    assert result == expected


def test_package_url_with_multiple_segments() -> None:
    result = package_url("vendor/package/subpackage", "1.0.0")
    expected = "pkg:composer/vendor/package-subpackage@1.0.0"
    assert result == expected


def test_package_url_with_empty_version() -> None:
    result = package_url("monolog/monolog", "")
    expected = "pkg:composer/monolog/monolog"
    assert result == expected


def test_package_url_with_vendor_and_subname() -> None:
    result = package_url("vendor/package", "2.3.4")
    assert "vendor" in result
    assert "package@2.3.4" in result


def test_package_url_without_vendor() -> None:
    result = package_url("simple-package", "1.0.0")
    expected = "pkg:composer/simple-package@1.0.0"
    assert result == expected


def test_package_url_empty_name() -> None:
    with raises(ValueError, match="Package name cannot be empty"):
        package_url("", "1.0.0")


def test_new_package_without_coordinates() -> None:
    package = IndexedDict[str, ParsedValue]()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=10),
    )
    package[("name", position)] = ("test/package", position)
    package[("version", position)] = ("1.0.0", position)

    location = Location(
        coordinates=None,
        access_path="composer.json",
    )
    result = new_package_from_composer(package, location)

    assert result is not None
    assert result.locations[0].coordinates is None
    assert result.locations[0].dependency_type == DependencyType.UNKNOWN
