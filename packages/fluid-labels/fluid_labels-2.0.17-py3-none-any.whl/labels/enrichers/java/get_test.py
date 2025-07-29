import pytest
import requests

import labels.enrichers.java.get
from labels.enrichers.java.get import (
    AuthorsLicenses,
    MavenPackageInfo,
    MavenSearchDocResponse,
    build_maven_search_url,
    build_maven_urls,
    build_metadata_url,
    extract_authors_licenses,
    get_authors_licenses,
    get_latest_version_info,
    get_maven_metadata,
    get_maven_package_info,
    parse_maven_search_response,
    parse_metadata_xml,
    parse_pom_xml,
    search_maven_package,
)
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.fake_response import MockResponse


def test_build_maven_search_url() -> None:
    base_url, params = build_maven_search_url("test-artifact", "1.0.0")
    assert base_url == "https://search.maven.org/solrsearch/select"
    assert params == {"q": "a:test-artifact AND v:1.0.0", "rows": 5, "wt": "json"}

    base_url, params = build_maven_search_url("test-artifact", None)
    assert base_url == "https://search.maven.org/solrsearch/select"
    assert params == {"q": "a:test-artifact", "rows": 5, "wt": "json"}


def test_build_maven_urls() -> None:
    pom_url, jar_url, hash_url = build_maven_urls("org.test", "test-artifact", "1.0.0")
    assert (
        pom_url
        == "https://repo1.maven.org/maven2/org/test/test-artifact/1.0.0/test-artifact-1.0.0.pom"
    )
    assert (
        jar_url
        == "https://repo1.maven.org/maven2/org/test/test-artifact/1.0.0/test-artifact-1.0.0.jar"
    )
    assert (
        hash_url
        == "https://repo1.maven.org/maven2/org/test/test-artifact/1.0.0/test-artifact-1.0.0.jar.sha1"
    )


def test_parse_maven_search_response() -> None:
    docs = [
        {
            "id": "test-id",
            "g": "org.test",
            "a": "test-artifact",
            "v": "1.0.0",
            "p": "jar",
            "timestamp": 1609459200000,
            "ec": ["test-classifier"],
            "tags": ["test-tag"],
        },
    ]
    result = parse_maven_search_response(docs, "test-artifact", "1.0.0")
    assert isinstance(result, MavenSearchDocResponse)
    assert result.id_ == "test-id"
    assert result.group == "org.test"
    assert result.artifact == "test-artifact"
    assert result.version == "1.0.0"
    assert result.timestamp == 1609459200
    assert result.packaging == "jar"
    assert result.extra_classifiers == ["test-classifier"]
    assert result.tags == ["test-tag"]


@mocks(
    mocks=[
        Mock(
            module=requests,
            target="get",
            target_type="sync",
            expected=MockResponse(404, {}),
        ),
    ],
)
async def test_search_maven_package_not_found() -> None:
    result = search_maven_package("nonexistent", "1.0.0")
    assert result is None


def test_extract_authors_licenses() -> None:
    pom_content = """<?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0">
        <developers>
            <developer>
                <name>Test Author</name>
            </developer>
        </developers>
        <licenses>
            <license>
                <name>MIT</name>
            </license>
        </licenses>
    </project>
    """
    pom_xml = parse_pom_xml(pom_content)
    result = extract_authors_licenses(pom_xml)
    assert isinstance(result, AuthorsLicenses)
    assert result.authors == ["Test Author"]
    assert result.licenses == ["MIT"]


@mocks(
    mocks=[
        Mock(
            module=requests,
            target="get",
            target_type="sync",
            expected=MockResponse(404, {}),
        ),
    ],
)
async def test_get_maven_package_info_not_found() -> None:
    result = get_maven_package_info("org.test", "test-artifact", "1.0.0")
    assert result is None


def test_maven_search_response_error(caplog: pytest.LogCaptureFixture) -> None:
    docs = [
        {
            "unknown_field": "test-value",
        },
    ]
    result = parse_maven_search_response(docs, "test-artifact", "1.0.0")
    assert "Error parsing Maven search response" in caplog.text
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.java.get,
            target="make_get",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_search_maven_package_no_package() -> None:
    result = search_maven_package("nonexistent-artifact", "1.0.0")
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.java.get,
            target="make_get",
            target_type="sync",
            expected="""<?xml version="1.0" encoding="UTF-8"?>
                <project xmlns="http://maven.apache.org/POM/4.0.0">
                    <developers>
                        <developer>
                            <name>Test Developer</name>
                        </developer>
                    </developers>
                    <licenses>
                        <license>
                            <name>Apache License 2.0</name>
                        </license>
                    </licenses>
                </project>
            """,
        ),
    ],
)
async def test_get_authors_licenses_success() -> None:
    result = get_authors_licenses("org.test", "test-artifact", "1.0.0")
    assert isinstance(result, AuthorsLicenses)
    assert result.authors == ["Test Developer"]
    assert result.licenses == ["Apache License 2.0"]


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.java.get,
            target="make_get",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_authors_licenses_not_found() -> None:
    result = get_authors_licenses("org.test", "nonexistent", "1.0.0")
    assert result is None


def test_parse_metadata_xml_success() -> None:
    metadata_content = """<?xml version="1.0" encoding="UTF-8"?>
    <metadata>
        <versioning>
            <release>1.0.0</release>
            <lastUpdated>20240101120000</lastUpdated>
        </versioning>
    </metadata>
    """
    version, release_date = parse_metadata_xml(metadata_content)
    assert version == "1.0.0"
    assert release_date == 1704110400  # 2024-01-01 12:00:00 UTC


def test_parse_metadata_xml_incomplete() -> None:
    metadata_content = """<?xml version="1.0" encoding="UTF-8"?>
    <metadata>
        <versioning>
        </versioning>
    </metadata>
    """
    version, release_date = parse_metadata_xml(metadata_content)
    assert version is None
    assert release_date is None


def test_build_metadata_url() -> None:
    url = build_metadata_url("org.test", "test-artifact")
    assert url == "https://repo1.maven.org/maven2/org/test/test-artifact/maven-metadata.xml"


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.java.get,
            target="make_get",
            target_type="sync",
            expected="""<?xml version="1.0" encoding="UTF-8"?>
    <metadata>
        <versioning>
            <release>2.0.0</release>
            <lastUpdated>20240101120000</lastUpdated>
        </versioning>
    </metadata>""",
        ),
    ],
)
async def test_get_maven_metadata_success() -> None:
    version, release_date = get_maven_metadata("org.test", "test-artifact")
    assert version == "2.0.0"
    assert release_date == 1704110400  # 2024-01-01 12:00:00 UTC


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.java.get,
            target="make_get",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_maven_metadata_not_found() -> None:
    version, release_date = get_maven_metadata("org.test", "nonexistent")
    assert version is None
    assert release_date is None


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.java.get,
            target="get_maven_metadata",
            target_type="sync",
            expected=("2.0.0", 1704110400),
        ),
        Mock(
            module=labels.enrichers.java.get,
            target="get_authors_licenses",
            target_type="sync",
            expected=AuthorsLicenses(
                authors=["Test Developer"],
                licenses=["Apache License 2.0"],
            ),
        ),
    ],
)
async def test_get_latest_version_info_success() -> None:
    result = get_latest_version_info("org.test", "test-artifact")
    assert isinstance(result, MavenPackageInfo)
    assert result.group_id == "org.test"
    assert result.artifact_id == "test-artifact"
    assert result.latest_version == "2.0.0"
    assert result.release_date == 1704110400  # 2024-01-01 12:00:00 UTC
    assert result.authors == ["Test Developer"]
    assert result.licenses == ["Apache License 2.0"]


@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.java.get,
            target="get_maven_metadata",
            target_type="sync",
            expected=(None, None),
        ),
    ],
)
async def test_get_latest_version_info_not_found() -> None:
    result = get_latest_version_info("org.test", "nonexistent")
    assert result is None


@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_get_maven_package_info_real() -> None:
    result = get_maven_package_info("org.springframework", "spring-core", "5.3.20")
    assert isinstance(result, MavenPackageInfo)
    assert result.group_id == "org.springframework"
    assert result.artifact_id == "spring-core"
    assert result.version == "5.3.20"


@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_search_maven_package_success() -> None:
    result = search_maven_package("spring-core", "5.3.20")
    assert isinstance(result, MavenSearchDocResponse)
    assert result.group == "org.springframework"
    assert result.artifact == "spring-core"
    assert result.version == "5.3.20"
    assert result.packaging == "jar"
    assert result.timestamp > 0
    assert ":" in result.id_


@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_get_maven_package_info_real_no_version() -> None:
    result = get_maven_package_info("org.springframework", "spring-core")
    assert isinstance(result, MavenPackageInfo)
    assert result.group_id == "org.springframework"
    assert result.artifact_id == "spring-core"
