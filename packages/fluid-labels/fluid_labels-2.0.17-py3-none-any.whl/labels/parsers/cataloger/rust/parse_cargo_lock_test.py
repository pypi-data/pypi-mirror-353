from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, Location, LocationReadCloser
from labels.model.indexables import FileCoordinate, IndexedDict, IndexedList, ParsedValue, Position
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.rust.parse_cargo_lock import (
    RustCargoLockEntry,
    _create_package,
    _create_relationships,
    parse_cargo_lock,
)
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_cargo_lock() -> None:
    test_data_path = get_test_data_path("dependencies/rust/Cargo.lock")
    expected = [
        Package(
            name="byteorder",
            version="1.5.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=7,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUST,
            licenses=[],
            type=PackageType.RustPkg,
            metadata=RustCargoLockEntry(
                name="byteorder",
                version="1.5.0",
                source="registry+https://github.com/rust-lang/crates.io-index",
                checksum=("1fd0f2584146f6f2ef48085050886acf353beff7305ebd1ae69500e27c67f64b"),
                dependencies=[],
            ),
            p_url="pkg:cargo/byteorder@1.5.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="lazy_static",
            version="1.4.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=13,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUST,
            licenses=[],
            type=PackageType.RustPkg,
            metadata=RustCargoLockEntry(
                name="lazy_static",
                version="1.4.0",
                source="registry+https://github.com/rust-lang/crates.io-index",
                checksum=("e2abad23fbc42b3700f2f279844dc832adb2b2eb069b2df918f455c4e18cc646"),
                dependencies=[],
            ),
            p_url="pkg:cargo/lazy_static@1.4.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="lazy-init",
            version="0.3.0",
            language=Language.RUST,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=19,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.RustPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=RustCargoLockEntry(
                name="lazy-init",
                version="0.3.0",
                source="registry+https://github.com/rust-lang/crates.io-index",
                checksum="e2abad23fbc42b3700f2f279844dc832adb2b2eb069b2df918f455c4e18aa646",
                dependencies=[],
            ),
            p_url="pkg:cargo/lazy-init@0.3.0",
        ),
        Package(
            name="lde",
            version="0.3.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=25,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUST,
            licenses=[],
            type=PackageType.RustPkg,
            metadata=RustCargoLockEntry(
                name="lde",
                version="0.3.0",
                source="registry+https://github.com/rust-lang/crates.io-index",
                checksum=("7094800262acbe78630f1fd9725c45e3da32655d1b9652b852fc84a913e3d4da"),
                dependencies=[],
            ),
            p_url="pkg:cargo/lde@0.3.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="log",
            version="0.4.20",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=31,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUST,
            licenses=[],
            type=PackageType.RustPkg,
            metadata=RustCargoLockEntry(
                name="log",
                version="0.4.20",
                source="registry+https://github.com/rust-lang/crates.io-index",
                checksum=("b5e6163cb8c49088c2c36f57875e58ccd8c87c7427f7fbd50ea6710b2f3f2e8f"),
                dependencies=[],
            ),
            p_url="pkg:cargo/log@0.4.20",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="symflow",
            version="0.1.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=37,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUST,
            licenses=[],
            type=PackageType.RustPkg,
            metadata=RustCargoLockEntry(
                name="symflow",
                version="0.1.0",
                source=None,
                checksum=None,
                dependencies=["byteorder", "lazy_static", "lde", "z3"],
            ),
            p_url="pkg:cargo/symflow@0.1.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="z3",
            version="0.3.2",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=47,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUST,
            licenses=[],
            type=PackageType.RustPkg,
            metadata=RustCargoLockEntry(
                name="z3",
                version="0.3.2",
                source=(
                    "git+https://github.com/laurmaedje"
                    "/z3.rs#b35c30aad36d84947672e5dec53a036273fbb3af"
                ),
                checksum=None,
                dependencies=["lazy_static", "log", "z3-sys"],
            ),
            p_url="pkg:cargo/z3@0.3.2",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
        Package(
            name="z3-sys",
            version="0.4.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=57,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.RUST,
            licenses=[],
            type=PackageType.RustPkg,
            metadata=RustCargoLockEntry(
                name="z3-sys",
                version="0.4.0",
                source=(
                    "git+https://github.com/laurmaedje"
                    "/z3.rs#b35c30aad36d84947672e5dec53a036273fbb3af"
                ),
                checksum=None,
                dependencies=[],
            ),
            p_url="pkg:cargo/z3-sys@0.4.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_cargo_lock(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
    assert pkgs == expected


def test_create_package_with_invalid_type() -> None:
    location = Location(access_path="test/path")
    invalid_pkg: IndexedList[ParsedValue] = IndexedList()

    result = _create_package(invalid_pkg, location)
    assert result is None


def test_create_package_without_required_fields() -> None:
    location = Location(access_path="test/path")
    pkg: IndexedDict[str, ParsedValue] = IndexedDict()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=1),
    )

    result = _create_package(pkg, location)
    assert result is None

    pkg[("name", position)] = ("test-package", position)
    result = _create_package(pkg, location)
    assert result is None


def test_create_package_with_validation_error() -> None:
    location = Location(access_path="test/path")
    pkg: IndexedDict[str, ParsedValue] = IndexedDict()
    position = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=1),
    )

    pkg[("name", position)] = ("test-package", position)
    pkg[("version", position)] = ("1.0.0", position)

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

        result = _create_package(pkg, location)
        assert result is None


def test_create_relationships_with_invalid_metadata() -> None:
    pkg = Package(
        name="test-package",
        version="1.0.0",
        locations=[],
        language=Language.RUST,
        licenses=[],
        p_url="pkg:cargo/test-package@1.0.0",
        type=PackageType.RustPkg,
        metadata=None,
    )

    relationships = _create_relationships([pkg])
    assert len(relationships) == 0


def test_parse_cargo_lock_without_coordinates() -> None:
    location = Location(access_path="test/path")
    content = BytesIO(b"")
    reader = LocationReadCloser(location=location, read_closer=TextIOWrapper(content))

    packages, relationships = parse_cargo_lock(None, None, reader)
    assert len(packages) == 0
    assert len(relationships) == 0


def test_parse_cargo_lock_without_packages_list() -> None:
    location = Location(
        access_path="test/path",
        coordinates=Coordinates(real_path="test/path", line=1),
    )
    content = BytesIO(b"")
    reader = LocationReadCloser(location=location, read_closer=TextIOWrapper(content))

    with patch(
        "labels.parsers.cataloger.rust.parse_cargo_lock.parse_toml_with_tree_sitter",
    ) as mock_parse:
        mock_parse.return_value = IndexedDict[str, ParsedValue]()
        packages, relationships = parse_cargo_lock(None, None, reader)
        assert len(packages) == 0
        assert len(relationships) == 0
