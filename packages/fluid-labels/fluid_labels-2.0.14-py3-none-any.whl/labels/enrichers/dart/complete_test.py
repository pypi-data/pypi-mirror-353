from labels.enrichers.dart import complete
from labels.enrichers.dart.complete import complete_package
from labels.model.package import Artifact, Digest, HealthMetadata, Language, Package, PackageType
from labels.testing.mocks import Mock, mocks

MOCK_RESPONSE = {
    "name": "http",
    "latest": {
        "version": "1.4.0",
        "pubspec": {
            "name": "http",
            "version": "1.4.0",
            "author": "John Doe <john.doe@example.com>",
            "description": "A composable, multi-platform, Future-based API for HTTP requests.",
            "repository": "https://github.com/dart-lang/http/tree/master/pkgs/http",
            "topics": [
                "http",
                "network",
                "protocols",
            ],
            "environment": {
                "sdk": "^3.4.0",
            },
            "dependencies": {
                "async": "^2.5.0",
                "http_parser": "^4.0.0",
                "meta": "^1.3.0",
                "web": "\u003e=0.5.0 \u003c2.0.0",
            },
            "dev_dependencies": {
                "dart_flutter_team_lints": "^3.0.0",
                "fake_async": "^1.2.0",
                "http_client_conformance_tests": {
                    "path": "../http_client_conformance_tests/",
                },
                "shelf": "^1.1.0",
                "stream_channel": "^2.1.1",
                "test": "^1.21.2",
            },
        },
        "archive_url": "https://pub.dev/api/archives/http-1.4.0.tar.gz",
        "archive_sha256": "2c11f3f94c687ee9bad77c171151672986360b2b001d109814ee7140b2cf261b",
        "published": "2025-05-06T00:17:13.636460Z",
    },
    "versions": [
        {
            "version": "1.2.2",
            "pubspec": {
                "name": "http",
                "version": "1.2.2",
                "author": "John Doe <john.doe@example.com>",
                "description": "A composable, multi-platform, Future-based API for HTTP requests.",
                "repository": "https://github.com/dart-lang/http/tree/master/pkgs/http",
                "topics": [
                    "http",
                    "network",
                    "protocols",
                ],
                "environment": {
                    "sdk": "^3.3.0",
                },
                "dependencies": {
                    "async": "^2.5.0",
                    "http_parser": "^4.0.0",
                    "meta": "^1.3.0",
                    "web": "\u003e=0.5.0 \u003c2.0.0",
                },
                "dev_dependencies": {
                    "dart_flutter_team_lints": "^3.0.0",
                    "fake_async": "^1.2.0",
                    "http_client_conformance_tests": {
                        "path": "../http_client_conformance_tests/",
                    },
                    "shelf": "^1.1.0",
                    "stream_channel": "^2.1.1",
                    "test": "^1.21.2",
                },
            },
            "archive_url": "https://pub.dev/api/archives/http-1.2.2.tar.gz",
            "archive_sha256": "b9c29a161230ee03d3ccf545097fccd9b87a5264228c5d348202e0f0c28f9010",
            "published": "2024-07-16T20:09:47.863320Z",
        },
        {
            "version": "1.4.0",
            "pubspec": {
                "name": "http",
                "version": "1.4.0",
                "author": "John Doe <john.doe@example.com>",
                "description": "A composable, multi-platform, Future-based API for HTTP requests.",
                "repository": "https://github.com/dart-lang/http/tree/master/pkgs/http",
                "topics": [
                    "http",
                    "network",
                    "protocols",
                ],
                "environment": {
                    "sdk": "^3.4.0",
                },
                "dependencies": {
                    "async": "^2.5.0",
                    "http_parser": "^4.0.0",
                    "meta": "^1.3.0",
                    "web": "\u003e=0.5.0 \u003c2.0.0",
                },
                "dev_dependencies": {
                    "dart_flutter_team_lints": "^3.0.0",
                    "fake_async": "^1.2.0",
                    "http_client_conformance_tests": {
                        "path": "../http_client_conformance_tests/",
                    },
                    "shelf": "^1.1.0",
                    "stream_channel": "^2.1.1",
                    "test": "^1.21.2",
                },
            },
            "archive_url": "https://pub.dev/api/archives/http-1.4.0.tar.gz",
            "archive_sha256": "2c11f3f94c687ee9bad77c171151672986360b2b001d109814ee7140b2cf261b",
            "published": "2025-05-06T00:17:13.636460Z",
        },
    ],
    "advisoriesUpdated": "2024-04-28T09:27:57.869544Z",
}


@mocks(
    mocks=[
        Mock(
            module=complete,
            target="get_pub_package",
            target_type="sync",
            expected=MOCK_RESPONSE,
        ),
    ],
)
async def test_complete_package() -> None:
    package = Package(
        name="http",
        version="1.2.2",
        language=Language.DART,
        licenses=[],
        locations=[],
        type=PackageType.DartPubPkg,
        p_url="pkg:dart/http@1.2.2",
    )

    expected_health_metadata = HealthMetadata(
        latest_version="1.4.0",
        latest_version_created_at="2025-05-06T00:17:13.636460Z",
        authors="John Doe <john.doe@example.com>",
        artifact=Artifact(
            url="https://pub.dev/api/archives/http-1.2.2.tar.gz",
            integrity=Digest(
                algorithm="sha256",
                value="b9c29a161230ee03d3ccf545097fccd9b87a5264228c5d348202e0f0c28f9010",
            ),
        ),
    )

    completed_package = complete_package(package)
    assert completed_package.health_metadata == expected_health_metadata


@mocks(
    mocks=[
        Mock(
            module=complete,
            target="get_pub_package",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_complete_package_no_package() -> None:
    package = Package(
        name="http",
        version="1.2.2",
        language=Language.DART,
        licenses=[],
        locations=[],
        type=PackageType.DartPubPkg,
        p_url="pkg:dart/http@1.2.2",
    )

    completed_package = complete_package(package)
    assert completed_package.health_metadata is None
