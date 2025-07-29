from typing import cast

from labels.model.file import Coordinates, Location
from labels.model.indexables import ParsedValue
from labels.model.package import Language, PackageType
from labels.parsers.cataloger.swift import package
from labels.parsers.cataloger.swift.package import (
    CocoaPodfileLockEntry,
    SwiftPackageManagerResolvedEntry,
    cocoapods_package_url,
    is_stable_package_version,
    new_cocoa_pods_package,
    new_swift_package_manager_package,
    swift_package_manager_package_url,
)
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.pytest_marks import parametrize_sync


def make_location(path: str = "foo/bar.swift") -> Location:
    return Location(
        coordinates=Coordinates(real_path=path),
        access_path=path,
        annotations={},
    )


@parametrize_sync(
    args=["version", "expected"],
    cases=[
        ["1.0.0", True],
        ["2.0.0-alpha", False],
        ["3.0.0-beta1", False],
        ["4.0.0-rc2", False],
        ["5.0.0", True],
        ["6.0.0-dev", False],
        ["7.0.0-nightly", False],
    ],
)
def test_is_stable_package_version(version: str, *, expected: bool) -> None:
    assert is_stable_package_version(version) == expected


@parametrize_sync(
    args=["name", "version", "hash_", "expect_none"],
    cases=[
        ["Alamofire", "5.6.4", "abc123", False],
        ["Alamofire", "5.6.4", 123, True],
    ],
)
def test_new_cocoa_pods_package(
    name: str,
    version: str,
    hash_: object,
    *,
    expect_none: bool,
) -> None:
    location = make_location()
    hash_casted: ParsedValue = cast(ParsedValue, hash_)
    pkg = new_cocoa_pods_package(name, version, hash_casted, location)
    if expect_none:
        assert pkg is None
    else:
        assert pkg is not None
        assert pkg.name == name
        assert pkg.version == version
        assert pkg.type == PackageType.CocoapodsPkg
        assert pkg.language == Language.SWIFT
        assert pkg.locations[0] == location
        metadata = cast(CocoaPodfileLockEntry, pkg.metadata)
        assert metadata.checksum == hash_


@parametrize_sync(
    args=["name", "version", "source_url", "revision", "expect_none"],
    cases=[
        ["MyLib", "1.2.3", "https://github.com/foo/bar.git", "rev123", False],
        ["MyLib", "1.2.3", None, None, False],
    ],
)
def test_new_swift_package_manager_package(
    name: str,
    version: str,
    source_url: str | None,
    revision: str | None,
    *,
    expect_none: bool,
) -> None:
    location = make_location()
    pkg = new_swift_package_manager_package(
        name=name,
        version=version,
        source_url=source_url,
        revision=revision,
        location=location,
    )
    if expect_none:
        assert pkg is None
    else:
        assert pkg is not None
        assert pkg.name == name
        assert pkg.version == version
        assert pkg.type == PackageType.SwiftPkg
        assert pkg.language == Language.SWIFT
        assert pkg.locations[0] == location
        if revision:
            metadata = cast(SwiftPackageManagerResolvedEntry, pkg.metadata)
            assert metadata.revision == revision
        else:
            assert pkg.metadata is None


@parametrize_sync(
    args=["name", "version", "expected"],
    cases=[
        ["Alamofire", "5.6.4", "pkg:cocoapods/Alamofire@5.6.4"],
    ],
)
def test_cocoapods_package_url(name: str, version: str, expected: str) -> None:
    assert cocoapods_package_url(name, version) == expected


@parametrize_sync(
    args=["name", "version", "source_url", "expected"],
    cases=[
        [
            "Alamofire",
            "5.6.4",
            "https://github.com/foo/bar.git",
            "pkg:swift/github.com/foo/bar.git/Alamofire@5.6.4",
        ],
        ["Alamofire", "5.6.4", None, "pkg:swift/Alamofire@5.6.4"],
    ],
)
def test_swift_package_manager_package_url(
    name: str,
    version: str,
    source_url: str | None,
    expected: str,
) -> None:
    assert swift_package_manager_package_url(name, version, source_url) == expected


@mocks(
    mocks=[
        Mock(
            module=package,
            target="cocoapods_package_url",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_new_cocoa_pods_package_url_mocked() -> None:
    location = make_location()
    result = new_cocoa_pods_package("foo", "1.0.0", "hash", location)
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=package,
            target="swift_package_manager_package_url",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_new_swift_package_manager_package_url_mocked() -> None:
    location = make_location()
    result = new_swift_package_manager_package(
        name="foo",
        version="1.0.0",
        source_url=None,
        revision="rev",
        location=location,
    )
    assert result is None
