from io import BytesIO, TextIOWrapper
from pathlib import Path

from labels.model.file import Coordinates, Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.python.model import PythonFileDigest, PythonFileRecord, PythonPackage
from labels.parsers.cataloger.python.parse_wheel_egg import parse_wheel_or_egg
from labels.parsers.cataloger.python.parse_wheel_egg_record import (
    parse_installed_files,
    parse_wheel_or_egg_record,
)
from labels.resolvers.directory import Directory
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_egg_file() -> None:
    test_data_path = get_test_data_path("dependencies/python/egg-info/PKG-INFO")
    expected = [
        Package(
            name="requests",
            version="2.22.0",
            language=Language.PYTHON,
            licenses=[],
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=None,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            type=PackageType.PythonPkg,
            advisories=None,
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
            metadata=PythonPackage(
                name="requests",
                version="2.22.0",
                author="Kenneth Reitz",
                author_email="me@kennethreitz.org",
                platform="UNKNOWN",
                files=[
                    PythonFileRecord(
                        path="requests-2.22.0.dist-info/INSTALLER",
                        digest=PythonFileDigest(
                            algorithm="sha256",
                            value=("zuuue4knoyJ-UwPPXg8fezS7VCrXJQrAP7zeNuwvFQg"),
                        ),
                        size="4",
                    ),
                    PythonFileRecord(
                        path="requests/__init__.py",
                        digest=PythonFileDigest(
                            algorithm="sha256",
                            value=("PnKCgjcTq44LaAMzB-7--B2FdewRrE8F_vjZeaG9NhA"),
                        ),
                        size="3921",
                    ),
                    PythonFileRecord(
                        path="requests/__version__.py",
                        digest=PythonFileDigest(
                            algorithm="sha256",
                            value=("Bm-GFstQaFezsFlnmEMrJDe8JNROz9n2XXYtODdvjjc"),
                        ),
                        size="436",
                    ),
                    PythonFileRecord(
                        path="requests/utils.py",
                        digest=PythonFileDigest(
                            algorithm="sha256",
                            value=("LtPJ1db6mJff2TJSJWKi7rBpzjPS3mSOrjC9zRhoD3A"),
                        ),
                        size="30049",
                    ),
                ],
                site_package_root_path=str(Path(test_data_path).parent.parent),
                top_level_packages=["requests"],
                direct_url_origin=None,
                dependencies=None,
            ),
            p_url="pkg:pypi/requests@2.22.0",
        ),
    ]

    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_wheel_or_egg(
            Directory(root=test_data_path, exclude=()),
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        assert pkgs is not None
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
    assert pkgs == expected


def test_parse_wheel_or_egg_record_with_invalid_lines() -> None:
    test_data = b"""valid/path/file.py,sha256=abc123,100
invalid_line
another/invalid/line,missing_parts
valid/path/other.py,sha256=def456,200
invalid_digest_format,not_a_digest,300
"""

    reader = TextIOWrapper(BytesIO(test_data))
    records = parse_wheel_or_egg_record(reader)

    assert len(records) == 2

    first_record = records[0]
    assert first_record.path == "valid/path/file.py"
    assert first_record.digest is not None
    assert first_record.digest.algorithm == "sha256"
    assert first_record.digest.value == "abc123"
    assert first_record.size == "100"

    second_record = records[1]
    assert second_record.path == "valid/path/other.py"
    assert second_record.digest is not None
    assert second_record.digest.algorithm == "sha256"
    assert second_record.digest.value == "def456"
    assert second_record.size == "200"


def test_parse_installed_files_basic() -> None:
    test_data = b"""package/file1.py
package/subdir/file2.py
package/__init__.py
"""
    reader = TextIOWrapper(BytesIO(test_data))
    records = parse_installed_files(reader, "", "")

    assert len(records) == 3
    assert records[0].path == "package/file1.py"
    assert records[1].path == "package/subdir/file2.py"
    assert records[2].path == "package/__init__.py"

    for record in records:
        assert record.digest is None
        assert record.size is None


def test_parse_installed_files_with_paths() -> None:
    test_data = b"""package/file1.py
package/subdir/file2.py
package/__init__.py
"""
    reader = TextIOWrapper(BytesIO(test_data))

    location = "/usr/local/lib/python3.8/site-packages/package.egg-info"
    site_packages_root = "/usr/local/lib/python3.8/site-packages"

    records = parse_installed_files(reader, location, site_packages_root)
    assert len(records) == 3

    expected_base = str(Path(site_packages_root, "package.egg-info").parent)
    assert records[0].path == str(Path(expected_base, "package/file1.py").resolve())
    assert records[1].path == str(Path(expected_base, "package/subdir/file2.py").resolve())
    assert records[2].path == str(Path(expected_base, "package/__init__.py").resolve())


def test_parse_installed_files_empty() -> None:
    test_data = b""
    reader = TextIOWrapper(BytesIO(test_data))
    records = parse_installed_files(reader, "", "")
    assert len(records) == 0


def test_parse_installed_files_single_line() -> None:
    test_data = b"package/file.py"
    reader = TextIOWrapper(BytesIO(test_data))
    records = parse_installed_files(reader, "", "")

    assert len(records) == 1
    assert records[0].path == "package/file.py"
    assert records[0].digest is None
    assert records[0].size is None
