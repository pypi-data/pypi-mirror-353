import re

from labels.model.package import PackageType
from labels.parsers.cataloger.java.archive_filename import (
    get_subexp,
    name_and_version_pattern,
    parse_filename,
)
from labels.testing.utils.pytest_marks import parametrize_sync


@parametrize_sync(
    args=["matches", "subexp_name", "expected"],
    cases=[
        [None, "name", ""],
        [name_and_version_pattern.search("test-1.0.0"), "name", "test"],
        [name_and_version_pattern.search("test-1.0.0"), "version", "1.0.0"],
        [name_and_version_pattern.search("test"), "version", ""],
    ],
)
def test_get_subexp(
    matches: re.Match[str] | None,
    subexp_name: str,
    expected: str,
) -> None:
    result = get_subexp(matches, subexp_name)
    assert result == expected


@parametrize_sync(
    args=["filename", "version", "extension", "name", "type_"],
    cases=[
        [
            "Type-maven-4.3.2.blerg",
            "4.3.2",
            "blerg",
            "Type-maven",
            PackageType.UnknownPkg,
        ],
        [
            "Type-maven.4.3.2.blerg",
            "4.3.2",
            "blerg",
            "Type-maven",
            PackageType.UnknownPkg,
        ],
        [
            "Type-maven_4.3.2.blerg",
            "4.3.2",
            "blerg",
            "Type-maven",
            PackageType.UnknownPkg,
        ],
        [
            "Type-maven-4.3.2.jar",
            "4.3.2",
            "jar",
            "Type-maven",
            PackageType.JavaPkg,
        ],
        [
            "Type-extra-field-maven-4.3.2.war",
            "4.3.2",
            "war",
            "Type-extra-field-maven",
            PackageType.JavaPkg,
        ],
        [
            "liferay-package.lpkg",
            "",
            "lpkg",
            "liferay-package",
            PackageType.JavaPkg,
        ],
        [
            "Type-extra-field-maven-4.3.2-rc1.ear",
            "4.3.2-rc1",
            "ear",
            "Type-extra-field-maven",
            PackageType.JavaPkg,
        ],
        [
            "Type-extra-field-maven-4.3.2-rc1.par",
            "4.3.2-rc1",
            "par",
            "Type-extra-field-maven",
            PackageType.JavaPkg,
        ],
        [
            "Type-extra-field-maven-4.3.2-rc1.sar",
            "4.3.2-rc1",
            "sar",
            "Type-extra-field-maven",
            PackageType.JavaPkg,
        ],
        [
            "Type-extra-field-maven-4.3.2-rc1.nar",
            "4.3.2-rc1",
            "nar",
            "Type-extra-field-maven",
            PackageType.JavaPkg,
        ],
        [
            "/some/path/Type-extra-field-maven-4.3.2-rc1.jpi",
            "4.3.2-rc1",
            "jpi",
            "Type-extra-field-maven",
            PackageType.JenkinsPluginPkg,
        ],
        [
            ("/some/path-with-version-5.4.3/Type-extra-field-maven-4.3.2-rc1.hpi"),
            "4.3.2-rc1",
            "hpi",
            "Type-extra-field-maven",
            PackageType.JenkinsPluginPkg,
        ],
        [
            ("/some/path-with-version-5.4.3/wagon-webdav-1.0.2-beta-2.2.3a-hudson.jar"),
            "1.0.2-beta-2.2.3a-hudson",
            "jar",
            "wagon-webdav",
            PackageType.JavaPkg,
        ],
        [
            ("/some/path-with-version-5.4.3/wagon-webdav-1.0.2-beta-2.2.3-hudson.jar"),
            "1.0.2-beta-2.2.3-hudson",
            "jar",
            "wagon-webdav",
            PackageType.JavaPkg,
        ],
        [
            "/some/path-with-version-5.4.3/windows-remote-command-1.0.jar",
            "1.0",
            "jar",
            "windows-remote-command",
            PackageType.JavaPkg,
        ],
        [
            ("/some/path-with-version-5.4.3/wagon-http-lightweight-1.0.5-beta-2.jar"),
            "1.0.5-beta-2",
            "jar",
            "wagon-http-lightweight",
            PackageType.JavaPkg,
        ],
        [
            "/hudson.war:WEB-INF/lib/commons-jelly-1.1-hudson-20100305.jar",
            "1.1-hudson-20100305",
            "jar",
            "commons-jelly",
            PackageType.JavaPkg,
        ],
        [
            "/hudson.war:WEB-INF/lib/jtidy-4aug2000r7-dev-hudson-1.jar",
            "4aug2000r7-dev-hudson-1",
            "jar",
            "jtidy",
            PackageType.JavaPkg,
        ],
        [
            "/hudson.war:WEB-INF/lib/trilead-ssh2-build212-hudson-5.jar",
            "build212-hudson-5",
            "jar",
            "trilead-ssh2",
            PackageType.JavaPkg,
        ],
        [
            "/hudson.war:WEB-INF/lib/guava-r06.jar",
            "r06",
            "jar",
            "guava",
            PackageType.JavaPkg,
        ],
        [
            "BOOT-INF/lib/spring-data-r2dbc-1.1.0.RELEASE.jar",
            "1.1.0.RELEASE",
            "jar",
            "spring-data-r2dbc",
            PackageType.JavaPkg,
        ],
        [
            "jboss-saaj-api_1.4_spec-1.0.2.Final.jar",
            "1.0.2.Final",
            "jar",
            "jboss-saaj-api_1.4_spec",
            PackageType.JavaPkg,
        ],
        [
            "/usr/share/java/gradle/lib/gradle-build-cache-8.1.1.jar",
            "8.1.1",
            "jar",
            "gradle-build-cache",
            PackageType.JavaPkg,
        ],
    ],
)
def test_parse_filename(
    filename: str,
    version: str,
    extension: str,
    name: str,
    type_: PackageType,
) -> None:
    item = parse_filename(filename)
    assert item.version == version
    assert item.extension() == extension
    assert item.name == name
    assert item.pkg_type() == type_
