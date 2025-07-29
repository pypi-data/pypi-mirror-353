import base64
from typing import Any

from labels.enrichers.javascript import complete
from labels.enrichers.javascript.complete import complete_package
from labels.model.package import Artifact, Digest, HealthMetadata, Language, Package, PackageType
from labels.testing.mocks import Mock, mocks


def get_base_package() -> Package:
    return Package(
        name="classnames",
        version="2.5.0",
        language=Language.JAVASCRIPT,
        licenses=[],
        locations=[],
        type=PackageType.NpmPkg,
        p_url="pkg:npm/classnames@2.5.0",
        health_metadata=None,
    )


MOCK_RESPONSE: dict[str, Any] = {
    "_id": "classnames",
    "_rev": "285-2c17bc1dc1da8ef8a1e04f65e4515b01",
    "name": "classnames",
    "dist-tags": {
        "latest": "2.5.1",
    },
    "versions": {
        "2.5.0": {
            "name": "classnames",
            "version": "2.5.0",
            "keywords": [
                "react",
                "css",
                "classes",
                "classname",
                "classnames",
                "util",
                "utility",
            ],
            "author": {
                "name": "Jed Watson",
            },
            "license": "MIT",
            "_id": "classnames@2.5.0",
            "maintainers": [
                {
                    "name": "jedwatson",
                    "email": "jed.watson@me.com",
                },
                {
                    "name": "dcousens",
                    "email": "npm2023@dcousens.com",
                },
            ],
            "homepage": "https://github.com/JedWatson/classnames#readme",
            "bugs": {
                "url": "https://github.com/JedWatson/classnames/issues",
            },
            "tsd": {
                "directory": "./tests",
            },
            "dist": {
                "shasum": "9304d63d8d7135989e33e1ffb0bcc65178f92c2a",
                "tarball": "https://registry.npmjs.org/classnames/-/classnames-2.5.0.tgz",
                "fileCount": 10,
                "integrity": "sha512-FQuRlyKinxrb5gwJlfVASbSrDlikDJ07426TrfPsdGLvtochowmkbnSFdQG"
                "J2aoXrSetq5KqGV9emvWpy+91xA==",
                "signatures": [
                    {
                        "sig": "MEYCIQDZc+DCdVuxY9A1dargq05oXyMhXj+tWbsgZLCQ1qov5AIhAOuQt6wVIRob3"
                        "LtwJ80dBC0klSAKKGC9Oqsj2Nr4O87y",
                        "keyid": "SHA256:jl3bwswu80PjjokCgh0o2w5c2U4LhQAE57gj9cz1kzA",
                    },
                ],
                "unpackedSize": 22969,
            },
            "main": "./index.js",
            "type": "commonjs",
            "types": "./index.d.ts",
            "exports": {
                ".": {
                    "types": "./index.d.ts",
                    "default": "./index.js",
                },
                "./bind": {
                    "types": "./bind.d.ts",
                    "default": "./bind.js",
                },
                "./dedupe": {
                    "types": "./dedupe.d.ts",
                    "default": "./dedupe.js",
                },
                "./bind.js": {
                    "types": "./bind.d.ts",
                    "default": "./bind.js",
                },
                "./index.js": {
                    "types": "./index.d.ts",
                    "default": "./index.js",
                },
                "./dedupe.js": {
                    "types": "./dedupe.d.ts",
                    "default": "./dedupe.js",
                },
                "./package.json": "./package.json",
            },
            "gitHead": "28ea73f9174bfa71675e954d01e6a1ac7baa6fe6",
            "scripts": {
                "test": "node --test ./tests/*.mjs",
                "check-types": "tsd",
            },
            "_npmUser": {
                "name": "jedwatson",
                "email": "jed.watson@me.com",
            },
            "repository": {
                "url": "git+https://github.com/JedWatson/classnames.git",
                "type": "git",
            },
            "workspaces": [
                "benchmarks",
            ],
            "_npmVersion": "10.2.3",
            "description": "A simple utility for conditionally joining classNames together",
            "directories": {},
            "_nodeVersion": "20.10.0",
            "_hasShrinkwrap": False,
            "_npmOperationalInternal": {
                "tmp": "tmp/classnames_2.5.0_1703723174344_0.35997533707318863",
                "host": "s3://npm-registry-packages",
            },
        },
        "2.5.1": {
            "name": "classnames",
            "version": "2.5.1",
            "keywords": [
                "react",
                "css",
                "classes",
                "classname",
                "classnames",
                "util",
                "utility",
            ],
            "author": {
                "name": "Jed Watson",
            },
            "license": "MIT",
            "_id": "classnames@2.5.1",
            "maintainers": [
                {
                    "name": "jedwatson",
                    "email": "jed.watson@me.com",
                },
                {
                    "name": "dcousens",
                    "email": "npm2023@dcousens.com",
                },
            ],
            "homepage": "https://github.com/JedWatson/classnames#readme",
            "bugs": {
                "url": "https://github.com/JedWatson/classnames/issues",
            },
            "tsd": {
                "directory": "./tests",
            },
            "dist": {
                "shasum": "ba774c614be0f016da105c858e7159eae8e7687b",
                "tarball": "https://registry.npmjs.org/classnames/-/classnames-2.5.1.tgz",
                "fileCount": 10,
                "integrity": "sha512-saHYOzhIQs6wy2sVxTM6bUDsQO4F50V9RQ22qBpEdCW+I+/Wmke2HOl6lS6dT"
                "pdxVhb88/I6+Hs+438c3lfUow==",
                "signatures": [
                    {
                        "sig": "MEQCIG8J+lnY7NItMCduLVO9E7PwV7n0XIRZroPEqdK8hahtAiBsUp3F4ew/srWgWI"
                        "bkxaaGIX2nPtyDtccTOSD8BuOgQQ==",
                        "keyid": "SHA256:jl3bwswu80PjjokCgh0o2w5c2U4LhQAE57gj9cz1kzA",
                    },
                ],
                "attestations": {
                    "url": "https://registry.npmjs.org/-/npm/v1/attestations/classnames@2.5.1",
                    "provenance": {
                        "predicateType": "https://slsa.dev/provenance/v1",
                    },
                },
                "unpackedSize": 23581,
            },
            "main": "./index.js",
            "type": "commonjs",
            "types": "./index.d.ts",
            "exports": {
                ".": {
                    "types": "./index.d.ts",
                    "default": "./index.js",
                },
                "./bind": {
                    "types": "./bind.d.ts",
                    "default": "./bind.js",
                },
                "./dedupe": {
                    "types": "./dedupe.d.ts",
                    "default": "./dedupe.js",
                },
                "./bind.js": {
                    "types": "./bind.d.ts",
                    "default": "./bind.js",
                },
                "./index.js": {
                    "types": "./index.d.ts",
                    "default": "./index.js",
                },
                "./dedupe.js": {
                    "types": "./dedupe.d.ts",
                    "default": "./dedupe.js",
                },
                "./package.json": "./package.json",
            },
            "gitHead": "2e3683264bab067d13938b5eb03a96391a089cb4",
            "scripts": {
                "test": "node --test ./tests/*.mjs",
                "bench": "node ./benchmarks/run.js",
                "check-types": "tsd",
                "bench-browser": "rollup --plugin commonjs,json,node-resolve "
                "./benchmarks/runInBrowser.js --file ./benchmarks/runInBrowser.bundle.js "
                "&& http-server -c-1 ./benchmarks",
            },
            "_npmUser": {
                "name": "jedwatson",
                "email": "jed.watson@me.com",
            },
            "repository": {
                "url": "git+https://github.com/JedWatson/classnames.git",
                "type": "git",
            },
            "_npmVersion": "10.2.3",
            "description": "A simple utility for conditionally joining classNames together",
            "directories": {},
            "_nodeVersion": "20.10.0",
            "_hasShrinkwrap": False,
            "_npmOperationalInternal": {
                "tmp": "tmp/classnames_2.5.1_1703865315824_0.6232018190232824",
                "host": "s3://npm-registry-packages",
            },
        },
    },
    "time": {
        "created": "2014-11-05T01:18:18.680Z",
        "modified": "2024-12-13T19:05:50.587Z",
        "2.5.0": "2023-12-28T00:26:14.489Z",
        "2.5.1": "2023-12-29T15:55:16.013Z",
    },
    "bugs": {
        "url": "https://github.com/JedWatson/classnames/issues",
    },
    "author": {
        "name": "Jed Watson",
    },
    "license": "MIT",
    "homepage": "https://github.com/JedWatson/classnames#readme",
    "keywords": [
        "react",
        "css",
        "classes",
        "classname",
        "classnames",
        "util",
        "utility",
    ],
    "repository": {
        "url": "git+https://github.com/JedWatson/classnames.git",
        "type": "git",
    },
    "description": "A simple utility for conditionally joining classNames together",
    "maintainers": [
        {
            "name": "jedwatson",
            "email": "jed.watson@me.com",
        },
        {
            "name": "dcousens",
            "email": "npm2023@dcousens.com",
        },
    ],
    "readme": "# Classnames",
    "readmeFilename": "README.md",
    "users": {
        "285858315": True,
        "alu": True,
        "ash": True,
        "boto": True,
    },
}


@mocks(
    mocks=[
        Mock(
            module=complete,
            target="get_npm_package",
            target_type="sync",
            expected=MOCK_RESPONSE,
        ),
    ],
)
async def test_complete_package() -> None:
    expected_health_metadata = HealthMetadata(
        latest_version="2.5.1",
        latest_version_created_at="2023-12-29T15:55:16.013Z",
        authors="Jed Watson",
        artifact=Artifact(
            url="https://registry.npmjs.org/classnames/-/classnames-2.5.0.tgz",
            integrity=Digest(
                algorithm="sha512",
                value=base64.b64decode(
                    MOCK_RESPONSE["versions"]["2.5.0"]["dist"]["integrity"].split("-")[1],
                ).hex(),
            ),
        ),
    )

    completed_package = complete_package(get_base_package())
    assert completed_package.health_metadata == expected_health_metadata
    assert completed_package.licenses == ["MIT"]


@mocks(
    mocks=[
        Mock(
            module=complete,
            target="get_npm_package",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_complete_package_no_pypi_response() -> None:
    base_package = get_base_package()
    completed_package = complete_package(base_package)
    assert completed_package == base_package
    assert completed_package.health_metadata is None
    assert completed_package.licenses == []


@mocks(
    mocks=[
        Mock(
            module=complete,
            target="get_npm_package",
            target_type="sync",
            expected={
                "author": {
                    "email": "test@example.com",
                },
                "versions": {},
            },
        ),
    ],
)
async def test_complete_package_with_bad_author_dict() -> None:
    completed_package = complete_package(get_base_package())
    assert completed_package.health_metadata
    assert completed_package.health_metadata.authors is None


@mocks(
    mocks=[
        Mock(
            module=complete,
            target="get_npm_package",
            target_type="sync",
            expected={
                "author": {
                    "name": "Test Author",
                    "email": "test@example.com",
                },
                "versions": {},
            },
        ),
    ],
)
async def test_complete_package_with_author_dict() -> None:
    completed_package = complete_package(get_base_package())
    assert completed_package.health_metadata
    assert completed_package.health_metadata.authors == "Test Author <test@example.com>"


@mocks(
    mocks=[
        Mock(
            module=complete,
            target="get_npm_package",
            target_type="sync",
            expected={
                "author": "Test Author",
                "versions": {},
            },
        ),
    ],
)
async def test_complete_package_with_author_string() -> None:
    completed_package = complete_package(get_base_package())
    assert completed_package.health_metadata
    assert completed_package.health_metadata.authors == "Test Author"


@mocks(
    mocks=[
        Mock(
            module=complete,
            target="get_npm_package",
            target_type="sync",
            expected={"versions": {}},
        ),
    ],
)
async def test_complete_package_without_dist_tags() -> None:
    completed_package = complete_package(get_base_package())
    assert completed_package.health_metadata
    assert completed_package.health_metadata.latest_version is None
    assert completed_package.health_metadata.latest_version_created_at is None


@mocks(
    mocks=[
        Mock(
            module=complete,
            target="get_npm_package",
            target_type="sync",
            expected={
                "versions": {
                    "2.5.0": {
                        "dist": {
                            "tarball": "https://example.com/package.tgz",
                        },
                    },
                },
            },
        ),
    ],
)
async def test_complete_package_without_integrity() -> None:
    completed_package = complete_package(get_base_package())
    assert completed_package.health_metadata
    assert completed_package.health_metadata.artifact is None


@mocks(
    mocks=[
        Mock(
            module=complete,
            target="get_npm_package",
            target_type="sync",
            expected={
                "versions": {
                    "2.5.0": {
                        "dist": {
                            "tarball": "https://registry.npmjs.org/classnames/-/classnames-2.5.0.tgz",
                            "integrity": "sha1-7d4c3c2c1b0a9d8e7f6c5b4a3d2c1b0a9d8e7f6c",
                        },
                    },
                },
            },
        ),
    ],
)
async def test_complete_package_with_non_sha512_integrity() -> None:
    completed_package = complete_package(get_base_package())
    assert completed_package.health_metadata
    assert completed_package.health_metadata.artifact is not None
    assert completed_package.health_metadata.artifact.integrity
    assert completed_package.health_metadata.artifact.integrity.algorithm == "sha1"
    assert (
        completed_package.health_metadata.artifact.integrity.value
        == "7d4c3c2c1b0a9d8e7f6c5b4a3d2c1b0a9d8e7f6c"
    )


@mocks(
    mocks=[
        Mock(
            module=complete,
            target="get_npm_package",
            target_type="sync",
            expected={
                "license": {
                    "type": "MIT",
                },
                "versions": {},
            },
        ),
    ],
)
async def test_complete_package_with_dict_license() -> None:
    completed_package = complete_package(get_base_package())
    assert completed_package.licenses == ["MIT"]


@mocks(
    mocks=[
        Mock(
            module=complete,
            target="get_npm_package",
            target_type="sync",
            expected={
                "license": [
                    "MIT",
                    "Apache-2.0",
                ],
                "versions": {},
            },
        ),
    ],
)
async def test_complete_package_with_list_license() -> None:
    completed_package = complete_package(get_base_package())
    assert completed_package.licenses == ["Apache-2.0", "MIT"]


@mocks(
    mocks=[
        Mock(
            module=complete,
            target="get_npm_package",
            target_type="sync",
            expected={
                "license": [
                    {"url": "https://example.com/license", "type": "MIT"},
                    "MIT",
                ],
                "versions": {},
            },
        ),
    ],
)
async def test_complete_package_with_invalid_license_dict() -> None:
    completed_package = complete_package(get_base_package())
    assert completed_package.licenses == ["MIT"]
