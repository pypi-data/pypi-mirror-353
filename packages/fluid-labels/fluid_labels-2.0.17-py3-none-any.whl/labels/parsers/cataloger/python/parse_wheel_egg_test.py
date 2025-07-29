import json
from io import BytesIO, StringIO, TextIOWrapper
from pathlib import Path
from unittest.mock import MagicMock

from labels.model.file import Coordinates, Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.python import parse_wheel_egg
from labels.parsers.cataloger.python.model import PythonFileDigest, PythonFileRecord, PythonPackage
from labels.parsers.cataloger.python.parse_wheel_egg import (
    assemble_egg_or_wheel_metadata,
    fetch_direct_url_data,
    fetch_installed_packages,
    fetch_record_files,
    fetch_top_level_packages,
    parse_wheel_or_egg,
)
from labels.parsers.cataloger.python.parse_wheel_egg_metadata import ParsedData
from labels.resolvers.directory import Directory
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.helpers import get_test_data_path


def test_parse_wheel_or_egg() -> None:
    test_data_path = Path(get_test_data_path("dependencies/python/urllib3-2.4.0.dist-info"))
    metadata_path = test_data_path / "METADATA"

    resolver = Directory(str(test_data_path))
    location = Location(
        coordinates=Coordinates(
            real_path=str(metadata_path.absolute()),
        ),
    )

    expected = Package(
        name="urllib3",
        version="2.4.0",
        language=Language.PYTHON,
        licenses=[],
        locations=[location],
        type=PackageType.PythonPkg,
        metadata=PythonPackage(
            name="urllib3",
            version="2.4.0",
            author=None,
            author_email="Andrey Petrov <andrey.petrov@shazow.net>",
            platform=None,
            files=[
                PythonFileRecord(
                    path="urllib3-2.4.0.dist-info/INSTALLER",
                    digest=PythonFileDigest(
                        value="zuuue4knoyJ-UwPPXg8fezS7VCrXJQrAP7zeNuwvFQg",
                        algorithm="sha256",
                    ),
                    size="4",
                ),
                PythonFileRecord(
                    path="urllib3-2.4.0.dist-info/METADATA",
                    digest=PythonFileDigest(
                        value="5BVhBpx5cN1xNfUe-sQ0BvBbMfaEsQ09LDq9rSQTZYo",
                        algorithm="sha256",
                    ),
                    size="6461",
                ),
                PythonFileRecord(
                    path="urllib3-2.4.0.dist-info/REQUESTED",
                    digest=PythonFileDigest(
                        value="47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU",
                        algorithm="sha256",
                    ),
                    size="0",
                ),
                PythonFileRecord(
                    path="urllib3-2.4.0.dist-info/WHEEL",
                    digest=PythonFileDigest(
                        value="qtCwoSJWgHk21S1Kb4ihdzI2rlJ1ZKaIurTj_ngOhyQ",
                        algorithm="sha256",
                    ),
                    size="87",
                ),
                PythonFileRecord(
                    path="urllib3-2.4.0.dist-info/direct_url.json",
                    digest=PythonFileDigest(
                        value="l2yAszeAyc-vvrxb7VicP0ATEC572y-EnWZYjNSZJQY",
                        algorithm="sha256",
                    ),
                    size="165",
                ),
                PythonFileRecord(
                    path="urllib3-2.4.0.dist-info/licenses/LICENSE.txt",
                    digest=PythonFileDigest(
                        value="Ew46ZNX91dCWp1JpRjSn2d8oRGnehuVzIQAmgEHj1oY",
                        algorithm="sha256",
                    ),
                    size="1093",
                ),
                PythonFileRecord(
                    path="urllib3/__init__.py",
                    digest=PythonFileDigest(
                        value="JMo1tg1nIV1AeJ2vENC_Txfl0e5h6Gzl9DGVk1rWRbo",
                        algorithm="sha256",
                    ),
                    size="6979",
                ),
                PythonFileRecord(
                    path="urllib3/_base_connection.py",
                    digest=PythonFileDigest(
                        value="T1cwH3RhzsrBh6Bz3AOGVDboRsE7veijqZPXXQTR2Rg",
                        algorithm="sha256",
                    ),
                    size="5568",
                ),
                PythonFileRecord(
                    path="urllib3/_collections.py",
                    digest=PythonFileDigest(
                        value="tM7c6J1iKtWZYV_QGYb8-r7Nr1524Dehnsa0Ufh6_mU",
                        algorithm="sha256",
                    ),
                    size="17295",
                ),
                PythonFileRecord(
                    path="urllib3/_request_methods.py",
                    digest=PythonFileDigest(
                        value="gCeF85SO_UU4WoPwYHIoz_tw-eM_EVOkLFp8OFsC7DA",
                        algorithm="sha256",
                    ),
                    size="9931",
                ),
                PythonFileRecord(
                    path="urllib3/_version.py",
                    digest=PythonFileDigest(
                        value="KyHVhKcn4Ob8_JP09Buz8x5uB4b7RJZLl3FBlZ8sWSY",
                        algorithm="sha256",
                    ),
                    size="511",
                ),
                PythonFileRecord(
                    path="urllib3/connection.py",
                    digest=PythonFileDigest(
                        value="dsVIUaPrOdATuO9OGnF5GzMhlVKlAw-2qH9FWYuic4s",
                        algorithm="sha256",
                    ),
                    size="39875",
                ),
                PythonFileRecord(
                    path="urllib3/connectionpool.py",
                    digest=PythonFileDigest(
                        value="ZEhudsa8BIubD2M0XoxBBsjxbsXwMgUScH7oQ9i-j1Y",
                        algorithm="sha256",
                    ),
                    size="43371",
                ),
                PythonFileRecord(
                    path="urllib3/contrib/__init__.py",
                    digest=PythonFileDigest(
                        value="47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU",
                        algorithm="sha256",
                    ),
                    size="0",
                ),
                PythonFileRecord(
                    path="urllib3/contrib/emscripten/__init__.py",
                    digest=PythonFileDigest(
                        value="u6KNgzjlFZbuAAXa_ybCR7gQ71VJESnF-IIdDA73brw",
                        algorithm="sha256",
                    ),
                    size="733",
                ),
                PythonFileRecord(
                    path="urllib3/contrib/emscripten/connection.py",
                    digest=PythonFileDigest(
                        value="j8DR_flE7hsoFhNfiqHLiaPaCsVbzG44jgahwvsQ52A",
                        algorithm="sha256",
                    ),
                    size="8771",
                ),
                PythonFileRecord(
                    path="urllib3/contrib/emscripten/emscripten_fetch_worker.js",
                    digest=PythonFileDigest(
                        value="CDfYF_9CDobtx2lGidyJ1zjDEvwNT5F-dchmVWXDh0E",
                        algorithm="sha256",
                    ),
                    size="3655",
                ),
                PythonFileRecord(
                    path="urllib3/contrib/emscripten/fetch.py",
                    digest=PythonFileDigest(
                        value="Li6sUnFuFog0fBiahk1Y0C0tdn5fxmj4ucDofPWFiXc",
                        algorithm="sha256",
                    ),
                    size="22867",
                ),
                PythonFileRecord(
                    path="urllib3/contrib/emscripten/request.py",
                    digest=PythonFileDigest(
                        value="mL28szy1KvE3NJhWor5jNmarp8gwplDU-7gwGZY5g0Q",
                        algorithm="sha256",
                    ),
                    size="566",
                ),
                PythonFileRecord(
                    path="urllib3/contrib/emscripten/response.py",
                    digest=PythonFileDigest(
                        value="7oVPENYZHuzEGRtG40HonpH5tAIYHsGcHPbJt2Z0U-Y",
                        algorithm="sha256",
                    ),
                    size="9507",
                ),
                PythonFileRecord(
                    path="urllib3/contrib/pyopenssl.py",
                    digest=PythonFileDigest(
                        value="Xp5Ym05VgXGhHa0C4wlutvHxY8SnKSS6WLb2t5Miu0s",
                        algorithm="sha256",
                    ),
                    size="19720",
                ),
                PythonFileRecord(
                    path="urllib3/contrib/socks.py",
                    digest=PythonFileDigest(
                        value="-iardc61GypsJzD6W6yuRS7KVCyfowcQrl_719H7lIM",
                        algorithm="sha256",
                    ),
                    size="7549",
                ),
                PythonFileRecord(
                    path="urllib3/exceptions.py",
                    digest=PythonFileDigest(
                        value="pziumHf0Vwx3z4gvUy7ou8nlM2yIYX0N3l3znEdeF5U",
                        algorithm="sha256",
                    ),
                    size="9938",
                ),
                PythonFileRecord(
                    path="urllib3/fields.py",
                    digest=PythonFileDigest(
                        value="FCf7UULSkf10cuTRUWTQESzxgl1WT8e2aCy3kfyZins",
                        algorithm="sha256",
                    ),
                    size="10829",
                ),
                PythonFileRecord(
                    path="urllib3/filepost.py",
                    digest=PythonFileDigest(
                        value="U8eNZ-mpKKHhrlbHEEiTxxgK16IejhEa7uz42yqA_dI",
                        algorithm="sha256",
                    ),
                    size="2388",
                ),
                PythonFileRecord(
                    path="urllib3/http2/__init__.py",
                    digest=PythonFileDigest(
                        value="xzrASH7R5ANRkPJOot5lGnATOq3KKuyXzI42rcnwmqs",
                        algorithm="sha256",
                    ),
                    size="1741",
                ),
                PythonFileRecord(
                    path="urllib3/http2/connection.py",
                    digest=PythonFileDigest(
                        value="4DB0DkZEC3yIkhGjUDIHB17wrYCLaL0Ag5bDW2_mGPI",
                        algorithm="sha256",
                    ),
                    size="12694",
                ),
                PythonFileRecord(
                    path="urllib3/http2/probe.py",
                    digest=PythonFileDigest(
                        value="nnAkqbhAakOiF75rz7W0udZ38Eeh_uD8fjV74N73FEI",
                        algorithm="sha256",
                    ),
                    size="3014",
                ),
                PythonFileRecord(
                    path="urllib3/poolmanager.py",
                    digest=PythonFileDigest(
                        value="2_L2AjVDgoQ0qBmYbX9u9QqyU1u5J37zQbtv_-ueZQA",
                        algorithm="sha256",
                    ),
                    size="22913",
                ),
                PythonFileRecord(
                    path="urllib3/py.typed",
                    digest=PythonFileDigest(
                        value="UaCuPFa3H8UAakbt-5G8SPacldTOGvJv18pPjUJ5gDY",
                        algorithm="sha256",
                    ),
                    size="93",
                ),
                PythonFileRecord(
                    path="urllib3/response.py",
                    digest=PythonFileDigest(
                        value="PBW5ZnK3kYeq0fqeUYywyASKQWK7uRzSa-HgDBzZedU",
                        algorithm="sha256",
                    ),
                    size="45190",
                ),
                PythonFileRecord(
                    path="urllib3/util/__init__.py",
                    digest=PythonFileDigest(
                        value="-qeS0QceivazvBEKDNFCAI-6ACcdDOE4TMvo7SLNlAQ",
                        algorithm="sha256",
                    ),
                    size="1001",
                ),
                PythonFileRecord(
                    path="urllib3/util/connection.py",
                    digest=PythonFileDigest(
                        value="JjO722lzHlzLXPTkr9ZWBdhseXnMVjMSb1DJLVrXSnQ",
                        algorithm="sha256",
                    ),
                    size="4444",
                ),
                PythonFileRecord(
                    path="urllib3/util/proxy.py",
                    digest=PythonFileDigest(
                        value="seP8-Q5B6bB0dMtwPj-YcZZQ30vHuLqRu-tI0JZ2fzs",
                        algorithm="sha256",
                    ),
                    size="1148",
                ),
                PythonFileRecord(
                    path="urllib3/util/request.py",
                    digest=PythonFileDigest(
                        value="qSwxEsJJ-9DUfFDEAZIgQe8sgyywKY0o3faH3ixi3i8",
                        algorithm="sha256",
                    ),
                    size="8218",
                ),
                PythonFileRecord(
                    path="urllib3/util/response.py",
                    digest=PythonFileDigest(
                        value="vQE639uoEhj1vpjEdxu5lNIhJCSUZkd7pqllUI0BZOA",
                        algorithm="sha256",
                    ),
                    size="3374",
                ),
                PythonFileRecord(
                    path="urllib3/util/retry.py",
                    digest=PythonFileDigest(
                        value="bj-2YUqblxLlv8THg5fxww-DM54XCbjgZXIQ71XioCY",
                        algorithm="sha256",
                    ),
                    size="18459",
                ),
                PythonFileRecord(
                    path="urllib3/util/ssl_.py",
                    digest=PythonFileDigest(
                        value="oqb0OXHb09LFDqcWI84KLMxg4Y3GvoelPj2Tf179IwA",
                        algorithm="sha256",
                    ),
                    size="19786",
                ),
                PythonFileRecord(
                    path="urllib3/util/ssl_match_hostname.py",
                    digest=PythonFileDigest(
                        value="Di7DU7zokoltapT_F0Sj21ffYxwaS_cE5apOtwueeyA",
                        algorithm="sha256",
                    ),
                    size="5845",
                ),
                PythonFileRecord(
                    path="urllib3/util/ssltransport.py",
                    digest=PythonFileDigest(
                        value="Ez4O8pR_vT8dan_FvqBYS6dgDfBXEMfVfrzcdUoWfi4",
                        algorithm="sha256",
                    ),
                    size="8847",
                ),
                PythonFileRecord(
                    path="urllib3/util/timeout.py",
                    digest=PythonFileDigest(
                        value="4eT1FVeZZU7h7mYD1Jq2OXNe4fxekdNvhoWUkZusRpA",
                        algorithm="sha256",
                    ),
                    size="10346",
                ),
                PythonFileRecord(
                    path="urllib3/util/url.py",
                    digest=PythonFileDigest(
                        value="WRh-TMYXosmgp8m8lT4H5spoHw5yUjlcMCfU53AkoAs",
                        algorithm="sha256",
                    ),
                    size="15205",
                ),
                PythonFileRecord(
                    path="urllib3/util/util.py",
                    digest=PythonFileDigest(
                        value="j3lbZK1jPyiwD34T8IgJzdWEZVT-4E-0vYIJi9UjeNA",
                        algorithm="sha256",
                    ),
                    size="1146",
                ),
                PythonFileRecord(
                    path="urllib3/util/wait.py",
                    digest=PythonFileDigest(
                        value="_ph8IrUR3sqPqi0OopQgJUlH4wzkGeM5CiyA7XGGtmI",
                        algorithm="sha256",
                    ),
                    size="4423",
                ),
            ],
            site_package_root_path=str(test_data_path.parent),
            top_level_packages=["urllib3"],
            direct_url_origin=None,
            dependencies=[],
        ),
        p_url="pkg:pypi/urllib3@2.4.0",
        dependencies=None,
        found_by=None,
        health_metadata=None,
        is_dev=False,
    )

    with Path(metadata_path).open(encoding="utf-8") as reader:
        packages, relationships = parse_wheel_or_egg(
            resolver,
            None,
            LocationReadCloser(location=location, read_closer=reader),
        )

    assert len(packages) == 1
    package = packages[0]
    assert package == expected
    assert len(relationships) == 0


def test_parse_wheel_or_egg_without_coordinates() -> None:
    resolver = Directory("./")
    location = Location(
        coordinates=None,
    )

    files, sources = fetch_record_files(
        resolver,
        location,
    )

    assert files is None
    assert sources is None


def test_parse_wheel_or_egg_without_record_ref() -> None:
    resolver = MagicMock(spec=Directory)
    resolver.relative_file_path.return_value = None

    location = Location(
        coordinates=Coordinates(
            real_path="./",
        ),
    )

    files, sources = fetch_record_files(
        resolver,
        location,
    )

    assert files is None
    assert sources is None


def test_parse_wheel_or_egg_without_record_content() -> None:
    resolver = MagicMock(spec=Directory)
    resolver.relative_file_path.return_value = Location(coordinates=Coordinates(real_path="RECORD"))
    resolver.file_contents_by_location.return_value = None

    location = Location(
        coordinates=Coordinates(
            real_path="dummy/path/METADATA",
        ),
    )

    files, sources = fetch_record_files(
        resolver,
        location,
    )

    assert files is None
    assert sources is None


def test_fetch_installed_packages_without_coordinates() -> None:
    resolver = MagicMock(spec=Directory)
    location = Location(coordinates=None)

    files, sources = fetch_installed_packages(
        resolver,
        location,
        "dummy/path",
    )

    assert files is None
    assert sources is None


def test_fetch_installed_packages_without_content() -> None:
    resolver = MagicMock(spec=Directory)
    resolver.relative_file_path.return_value = Location(
        coordinates=Coordinates(real_path="installed-files.txt"),
    )
    resolver.file_contents_by_location.return_value = None

    location = Location(
        coordinates=Coordinates(real_path="./"),
    )

    files, sources = fetch_installed_packages(
        resolver,
        location,
        "./",
    )

    assert files is None
    assert sources is None


def test_fetch_top_level_packages_without_coordinates() -> None:
    resolver = MagicMock(spec=Directory)

    location = Location(
        coordinates=None,
    )

    packages, sources = fetch_top_level_packages(
        resolver,
        location,
    )

    assert packages is None
    assert sources is None


def test_fetch_top_level_packages_without_location() -> None:
    resolver = MagicMock(spec=Directory)
    resolver.relative_file_path.return_value = None

    location = Location(
        coordinates=Coordinates(real_path="./"),
    )

    packages, sources = fetch_top_level_packages(
        resolver,
        location,
    )

    assert packages is None
    assert sources is None


def test_fetch_top_level_packages_without_content() -> None:
    resolver = MagicMock(spec=Directory)
    resolver.relative_file_path.return_value = Location(
        coordinates=Coordinates(real_path="top_level.txt"),
    )
    resolver.file_contents_by_location.return_value = None

    location = Location(
        coordinates=Coordinates(
            real_path="./",
        ),
    )

    packages, sources = fetch_top_level_packages(
        resolver,
        location,
    )

    assert packages is None
    assert sources is None


def test_fetch_direct_url_data_without_coordinates() -> None:
    resolver = MagicMock(spec=Directory)
    location = Location(coordinates=None)

    direct_url, sources = fetch_direct_url_data(
        resolver,
        location,
    )

    assert direct_url is None
    assert sources is None


def test_fetch_direct_url_data_without_location() -> None:
    resolver = MagicMock(spec=Directory)
    resolver.relative_file_path.return_value = None

    location = Location(
        coordinates=Coordinates(
            real_path="./",
        ),
    )

    direct_url, sources = fetch_direct_url_data(
        resolver,
        location,
    )

    assert direct_url is None
    assert sources is None


def test_fetch_direct_url_data_without_content() -> None:
    resolver = MagicMock(spec=Directory)
    resolver.relative_file_path.return_value = Location(
        coordinates=Coordinates(real_path="direct_url.json"),
    )
    resolver.file_contents_by_location.return_value = None

    location = Location(
        coordinates=Coordinates(
            real_path="./",
        ),
    )

    direct_url, sources = fetch_direct_url_data(
        resolver,
        location,
    )

    assert direct_url is None
    assert sources is None


@mocks(
    mocks=[
        Mock(
            parse_wheel_egg,
            "parse_wheel_or_egg_metadata",
            "sync",
            ParsedData(
                python_package=PythonPackage(
                    name="test",
                    version="1.0.0",
                    author=None,
                    author_email=None,
                    platform=None,
                    files=None,
                    site_package_root_path="./",
                    top_level_packages=None,
                    direct_url_origin=None,
                    dependencies=None,
                ),
                licenses="",
                license_file="",
                license_expresion="",
                license_location=None,
            ),
        ),
        Mock(
            parse_wheel_egg,
            "fetch_record_files",
            "sync",
            (None, None),
        ),
    ],
)
async def test_assemble_egg_or_wheel_metadata_without_sources() -> None:
    resolver = MagicMock(spec=Directory)
    resolver.file_contents_by_location.return_value = Location(
        coordinates=Coordinates(real_path="./"),
    )
    resolver.relative_file_path.return_value = None

    location = Location(
        coordinates=Coordinates(real_path="./"),
    )

    p_data, sources = assemble_egg_or_wheel_metadata(
        resolver,
        location,
    )

    assert p_data is not None
    assert sources == [location]


@mocks(
    mocks=[
        Mock(
            parse_wheel_egg,
            "parse_wheel_or_egg_metadata",
            "sync",
            None,
        ),
    ],
)
async def test_assemble_egg_or_wheel_metadata_without_p_data() -> None:
    resolver = MagicMock(spec=Directory)
    resolver.file_contents_by_location.return_value = Location(
        coordinates=Coordinates(real_path="./"),
    )

    location = Location(
        coordinates=Coordinates(real_path="./"),
    )

    p_data, sources = assemble_egg_or_wheel_metadata(
        resolver,
        location,
    )

    assert p_data is None
    assert sources is None


@mocks(
    mocks=[
        Mock(
            parse_wheel_egg,
            "parse_wheel_or_egg_metadata",
            "sync",
            None,
        ),
    ],
)
async def test_assemble_egg_or_wheel_metadata_without_records() -> None:
    resolver = MagicMock(spec=Directory)
    resolver.file_contents_by_location.return_value = Location(
        coordinates=Coordinates(real_path="./"),
    )
    resolver.relative_file_path.return_value = None

    location = Location(
        coordinates=Coordinates(real_path="./"),
    )

    p_data, sources = assemble_egg_or_wheel_metadata(
        resolver,
        location,
    )

    assert p_data is None
    assert sources is None


@mocks(
    mocks=[
        Mock(
            parse_wheel_egg,
            "parse_wheel_or_egg_metadata",
            "sync",
            ParsedData(
                python_package=PythonPackage(
                    name="test",
                    version="1.0.0",
                    author=None,
                    author_email=None,
                    platform=None,
                    files=None,
                    site_package_root_path="./",
                    top_level_packages=None,
                    direct_url_origin=None,
                    dependencies=None,
                ),
                licenses="",
                license_file="",
                license_expresion="",
                license_location=None,
            ),
        ),
        Mock(
            parse_wheel_egg,
            "fetch_record_files",
            "sync",
            (None, None),
        ),
    ],
)
async def test_assemble_egg_or_wheel_metadata_with_direct_url() -> None:
    resolver = MagicMock(spec=Directory)
    json_data = {
        "url": "https://github.com/urllib3/urllib3.git",
        "vcs_info": {
            "commit_id": "a5ff7ac3bbb8659e2ec3ed41dd43889f06a7d7bc",
            "requested_revision": "2.4.0",
            "vcs": "git",
        },
    }
    json_str = json.dumps(json_data)
    resolver.file_contents_by_location.side_effect = lambda _: StringIO(json_str)
    resolver.relative_file_path.return_value = Location(
        coordinates=Coordinates(real_path="direct_url.json"),
    )

    location = Location(
        coordinates=Coordinates(real_path="./"),
    )

    p_data, sources = assemble_egg_or_wheel_metadata(
        resolver,
        location,
    )

    assert p_data is not None
    assert p_data.python_package.direct_url_origin is not None
    assert sources is not None


@mocks(
    mocks=[
        Mock(
            parse_wheel_egg,
            "parse_wheel_or_egg_metadata",
            "sync",
            None,
        ),
    ],
)
async def test_parse_wheel_or_egg_without_p_data() -> None:
    resolver = MagicMock(spec=Directory)

    location = Location(
        coordinates=Coordinates(real_path="./"),
    )

    reader = TextIOWrapper(BytesIO(b""))
    packages, relationships = parse_wheel_or_egg(
        resolver,
        None,
        LocationReadCloser(location=location, read_closer=reader),
    )

    assert len(packages) == 0
    assert len(relationships) == 0


def test_assemble_egg_or_wheel_metadata_without_coordinates() -> None:
    resolver = MagicMock(spec=Directory)
    resolver.file_contents_by_location.return_value = None

    location = Location(
        coordinates=None,
    )

    p_data, sources = assemble_egg_or_wheel_metadata(
        resolver,
        location,
    )

    assert p_data is None
    assert sources is None
