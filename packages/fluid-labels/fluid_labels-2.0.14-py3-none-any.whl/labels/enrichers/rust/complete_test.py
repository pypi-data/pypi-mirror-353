import labels.enrichers.rust.complete
from labels.enrichers.rust.complete import complete_package
from labels.model.package import Artifact, Digest, HealthMetadata, Language, Package, PackageType
from labels.testing.mocks import Mock, mocks

MOCK_RESPONSE = {
    "crate": {
        "id": "serde",
        "name": "serde",
        "updated_at": "2025-03-09T19:13:49.968038Z",
        "versions": [
            1476368,
            1453061,
            1387964,
        ],
        "keywords": [
            "serialization",
            "no_std",
            "serde",
        ],
        "categories": [
            "encoding",
            "no-std",
            "no-std::no-alloc",
        ],
        "badges": [],
        "created_at": "2014-12-05T20:20:39.487502Z",
        "downloads": 542765570,
        "recent_downloads": 74515876,
        "default_version": "1.0.219",
        "num_versions": 306,
        "yanked": False,
        "max_version": "1.0.219",
        "newest_version": "1.0.219",
        "max_stable_version": "1.0.219",
        "description": "A generic serialization/deserialization framework",
        "homepage": "https://serde.rs",
        "documentation": "https://docs.rs/serde",
        "repository": "https://github.com/serde-rs/serde",
        "links": {
            "version_downloads": "/api/v1/crates/serde/downloads",
            "versions": None,
            "owners": "/api/v1/crates/serde/owners",
            "owner_team": "/api/v1/crates/serde/owner_team",
            "owner_user": "/api/v1/crates/serde/owner_user",
            "reverse_dependencies": "/api/v1/crates/serde/reverse_dependencies",
        },
        "exact_match": False,
    },
    "versions": [
        {
            "id": 1476368,
            "crate": "serde",
            "num": "1.0.219",
            "dl_path": "/api/v1/crates/serde/1.0.219/download",
            "readme_path": "/api/v1/crates/serde/1.0.219/readme",
            "updated_at": "2025-03-09T19:13:49.968038Z",
            "created_at": "2025-03-09T19:13:49.968038Z",
            "downloads": 35451540,
            "features": {
                "alloc": [],
                "default": [
                    "std",
                ],
                "derive": [
                    "serde_derive",
                ],
                "rc": [],
                "std": [],
                "unstable": [],
            },
            "yanked": False,
            "yank_message": None,
            "lib_links": None,
            "license": "MIT, Apache-2.0",
            "links": {
                "dependencies": "/api/v1/crates/serde/1.0.219/dependencies",
                "version_downloads": "/api/v1/crates/serde/1.0.219/downloads",
                "authors": "/api/v1/crates/serde/1.0.219/authors",
            },
            "crate_size": 78983,
            "published_by": {
                "id": 3618,
                "login": "dtolnay",
                "name": "David Tolnay",
                "avatar": "https://avatars.githubusercontent.com/u/1940490?v=4",
                "url": "https://github.com/dtolnay",
            },
            "audit_actions": [
                {
                    "action": "publish",
                    "user": {
                        "id": 3618,
                        "login": "dtolnay",
                        "name": "David Tolnay",
                        "avatar": "https://avatars.githubusercontent.com/u/1940490?v=4",
                        "url": "https://github.com/dtolnay",
                    },
                    "time": "2025-03-09T19:13:49.968038Z",
                },
            ],
            "checksum": "5f0e2c6ed6606019b4e29e69dbaba95b11854410e5347d525002456dbbb786b6",
            "rust_version": "1.31",
            "has_lib": True,
            "bin_names": [],
            "edition": "2018",
            "description": "A generic serialization/deserialization framework",
            "homepage": "https://serde.rs",
            "documentation": "https://docs.rs/serde",
            "repository": "https://github.com/serde-rs/serde",
        },
        {
            "id": 1453061,
            "crate": "serde",
            "num": "1.0.218",
            "dl_path": "/api/v1/crates/serde/1.0.218/download",
            "readme_path": "/api/v1/crates/serde/1.0.218/readme",
            "updated_at": "2025-02-20T05:20:38.173116Z",
            "created_at": "2025-02-20T05:20:38.173116Z",
            "downloads": 8662713,
            "features": {
                "alloc": [],
                "default": [
                    "std",
                ],
                "derive": [
                    "serde_derive",
                ],
                "rc": [],
                "std": [],
                "unstable": [],
            },
            "yanked": False,
            "yank_message": None,
            "lib_links": None,
            "license": "MIT, Apache-2.0",
            "links": {
                "dependencies": "/api/v1/crates/serde/1.0.218/dependencies",
                "version_downloads": "/api/v1/crates/serde/1.0.218/downloads",
                "authors": "/api/v1/crates/serde/1.0.218/authors",
            },
            "crate_size": 78968,
            "published_by": {
                "id": 3618,
                "login": "dtolnay",
                "name": "David Tolnay",
                "avatar": "https://avatars.githubusercontent.com/u/1940490?v=4",
                "url": "https://github.com/dtolnay",
            },
            "audit_actions": [
                {
                    "action": "publish",
                    "user": {
                        "id": 3618,
                        "login": "dtolnay",
                        "name": "David Tolnay",
                        "avatar": "https://avatars.githubusercontent.com/u/1940490?v=4",
                        "url": "https://github.com/dtolnay",
                    },
                    "time": "2025-02-20T05:20:38.173116Z",
                },
            ],
            "checksum": "e8dfc9d19bdbf6d17e22319da49161d5d0108e4188e8b680aef6299eed22df60",
            "rust_version": "1.31",
            "has_lib": True,
            "bin_names": [],
            "edition": "2018",
            "description": "A generic serialization/deserialization framework",
            "homepage": "https://serde.rs",
            "documentation": "https://docs.rs/serde",
            "repository": "https://github.com/serde-rs/serde",
        },
        {
            "id": 1387964,
            "crate": "serde",
            "num": "1.0.217",
            "dl_path": "/api/v1/crates/serde/1.0.217/download",
            "readme_path": "/api/v1/crates/serde/1.0.217/readme",
            "updated_at": "2024-12-27T20:42:01.491864Z",
            "created_at": "2024-12-27T20:42:01.491864Z",
            "downloads": 25293085,
            "features": {
                "alloc": [],
                "default": [
                    "std",
                ],
                "derive": [
                    "serde_derive",
                ],
                "rc": [],
                "std": [],
                "unstable": [],
            },
            "yanked": False,
            "yank_message": None,
            "lib_links": None,
            "license": "MIT, Apache-2.0",
            "links": {
                "dependencies": "/api/v1/crates/serde/1.0.217/dependencies",
                "version_downloads": "/api/v1/crates/serde/1.0.217/downloads",
                "authors": "/api/v1/crates/serde/1.0.217/authors",
            },
            "crate_size": 79019,
            "published_by": {
                "id": 3618,
                "login": "dtolnay",
                "name": "David Tolnay",
                "avatar": "https://avatars.githubusercontent.com/u/1940490?v=4",
                "url": "https://github.com/dtolnay",
            },
            "audit_actions": [
                {
                    "action": "publish",
                    "user": {
                        "id": 3618,
                        "login": "dtolnay",
                        "name": "David Tolnay",
                        "avatar": "https://avatars.githubusercontent.com/u/1940490?v=4",
                        "url": "https://github.com/dtolnay",
                    },
                    "time": "2024-12-27T20:42:01.491864Z",
                },
            ],
            "checksum": "02fc4265df13d6fa1d00ecff087228cc0a2b5f3c0e87e258d8b94a156e984c70",
            "rust_version": "1.31",
            "has_lib": True,
            "bin_names": [],
            "edition": "2018",
            "description": "A generic serialization/deserialization framework",
            "homepage": "https://serde.rs",
            "documentation": "https://docs.rs/serde",
            "repository": "https://github.com/serde-rs/serde",
        },
    ],
    "keywords": [
        {
            "id": "serialization",
            "keyword": "serialization",
            "created_at": "2014-11-20T20:14:31.726180Z",
            "crates_cnt": 884,
        },
        {
            "id": "no_std",
            "keyword": "no_std",
            "created_at": "2015-06-20T04:34:42.753830Z",
            "crates_cnt": 1592,
        },
        {
            "id": "serde",
            "keyword": "serde",
            "created_at": "2015-08-10T17:10:09.021436Z",
            "crates_cnt": 1031,
        },
    ],
    "categories": [
        {
            "id": "encoding",
            "category": "Encoding",
            "slug": "encoding",
            "description": "Encoding and/or decoding data from one data format to another.",
            "created_at": "2017-01-17T19:13:05.112025Z",
            "crates_cnt": 3343,
        },
        {
            "id": "no-std",
            "category": "No standard library",
            "slug": "no-std",
            "description": "Crates that are able to function without the Rust standard library.\n",
            "created_at": "2017-02-10T01:52:09.447906Z",
            "crates_cnt": 7720,
        },
        {
            "id": "no-std::no-alloc",
            "category": "No dynamic allocation",
            "slug": "no-std::no-alloc",
            "description": "Crates that are able to function without the Rust alloc crate.",
            "created_at": "2023-01-23T10:07:45.986892Z",
            "crates_cnt": 862,
        },
    ],
}


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.rust.complete,
            target="get_cargo_package",
            target_type="sync",
            expected=MOCK_RESPONSE,
        ),
    ],
)
async def test_complete_package() -> None:
    package = Package(
        name="serde",
        version="1.0.218",
        language=Language.RUST,
        licenses=[],
        locations=[],
        type=PackageType.RustPkg,
        p_url="pkg:rust/serde@1.0.218",
    )

    expected_health_metadata = HealthMetadata(
        latest_version="1.0.219",
        latest_version_created_at="2025-03-09T19:13:49.968038Z",
        authors="David Tolnay",
        artifact=Artifact(
            url="https://crates.io/api/v1/crates/serde/1.0.218/download",
            integrity=Digest(
                algorithm="sha256",
                value="e8dfc9d19bdbf6d17e22319da49161d5d0108e4188e8b680aef6299eed22df60",
            ),
        ),
    )

    completed_package = complete_package(package)
    assert completed_package.health_metadata == expected_health_metadata
    assert completed_package.licenses == ["Apache-2.0", "MIT"]


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.rust.complete,
            target="get_cargo_package",
            target_type="sync",
            expected={
                "crate": {
                    "id": "error_package",
                    "name": "error_package",
                    "updated_at": "2025-03-09T19:13:49.968038Z",
                    "versions": [1476368],
                    "max_stable_version": "1.0.0",
                    "created_at": "2025-03-09T19:13:49.968038Z",
                },
                "versions": [
                    {
                        "id": 1476368,
                        "crate": "serde",
                        "num": "1.0.219",
                        "license": "MIT, Apache-2.0",
                        "published_by": {},
                    },
                ],
            },
        ),
    ],
)
async def test_complete_package_without_artifact() -> None:
    package = Package(
        name="error_package",
        version="1.0.0",
        language=Language.RUST,
        licenses=[],
        locations=[],
        type=PackageType.RustPkg,
        p_url="pkg:rust/error_package@1.0.0",
    )

    expected_health_metadata = HealthMetadata(
        latest_version="1.0.0",
        latest_version_created_at="2025-03-09T19:13:49.968038Z",
        authors=None,
        artifact=None,
    )

    completed_package = complete_package(package)
    assert completed_package.health_metadata == expected_health_metadata
    assert completed_package.licenses == []


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.rust.complete,
            target="get_cargo_package",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_complete_package_not_found() -> None:
    package = Package(
        name="not_found",
        version="1.0.0",
        language=Language.RUST,
        licenses=[],
        locations=[],
        type=PackageType.RustPkg,
        p_url="pkg:rust/not_found@1.0.0",
    )

    completed_package = complete_package(package)
    assert completed_package == package
    assert completed_package.health_metadata is None
    assert completed_package.licenses == []
