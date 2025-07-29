from pathlib import Path

from labels.parsers.cataloger.java.archive_filename import ArchiveFilename
from labels.parsers.cataloger.java.model import JavaManifest
from labels.parsers.cataloger.java.parse_java_manifest import (
    _field_value_from_manifest,
    extract_name_from_apache_maven_bundle_plugin,
    extract_name_from_archive_filename,
    is_valid_java_identifier,
    parse_java_manifest,
    select_name,
    select_version,
)
from labels.testing.utils.helpers import get_test_data_path
from labels.testing.utils.pytest_marks import parametrize_sync


@parametrize_sync(
    args=["test_data", "expected"],
    cases=[
        [
            "dependencies/java/manifest/small",
            JavaManifest(main={"Manifest-Version": "1.0"}, sections=None),
        ],
        [
            "dependencies/java/manifest/standard-info",
            JavaManifest(
                main={
                    "Manifest-Version": "1.0",
                    "Name": "the-best-name",
                    "Specification-Title": "the-spec-title",
                    "Specification-Vendor": "the-spec-vendor",
                    "Specification-Version": "the-spec-version",
                    "Implementation-Title": "the-impl-title",
                    "Implementation-Vendor": "the-impl-vendor",
                    "Implementation-Version": "the-impl-version",
                },
                sections=None,
            ),
        ],
        [
            "dependencies/java/manifest/extra-info",
            JavaManifest(
                main={
                    "Manifest-Version": "1.0",
                    "Archiver-Version": "Plexus Archiver",
                    "Created-By": "Apache Maven 3.6.3",
                },
                sections=[
                    {"Name": "thing-1", "Built-By": "?"},
                    {"Build-Jdk": "14.0.1", "Main-Class": "hello.HelloWorld"},
                ],
            ),
        ],
        [
            "dependencies/java/manifest/extra-empty-lines",
            JavaManifest(
                main={
                    "Manifest-Version": "1.0",
                    "Archiver-Version": "Plexus Archiver",
                    "Created-By": "Apache Maven 3.6.3",
                },
                sections=[
                    {"Name": "thing-1", "Built-By": "?"},
                    {"Name": "thing-2", "Built-By": "someone!"},
                    {"Other": "things"},
                    {"Last": "item"},
                ],
            ),
        ],
        [
            "dependencies/java/manifest/continuation",
            JavaManifest(
                main={
                    "Manifest-Version": "1.0",
                    "Plugin-ScmUrl": ("https://github.com/jenkinsci/plugin-pom/example-jenkins"),
                },
                sections=None,
            ),
        ],
        [
            "dependencies/java/manifest/version-with-date",
            JavaManifest(
                main={
                    "Manifest-Version": "1.0",
                    "Implementation-Version": "1.3 2244 October 5 2005",
                },
                sections=None,
            ),
        ],
        [
            "dependencies/java/manifest/leading-space",
            JavaManifest(
                main={
                    "Key-keykeykey": "initialconfig:com",
                    "should": "parse",
                },
                sections=None,
            ),
        ],
    ],
)
def test_parse_java_manifest(
    test_data: str,
    expected: JavaManifest,
) -> None:
    test_data_path = get_test_data_path(test_data)
    with Path(test_data_path).open(encoding="utf-8") as reader:
        manifest = parse_java_manifest(reader.read())
        assert manifest == expected


@parametrize_sync(
    args=["field", "expected"],
    cases=[
        ["Field1", "value1"],
        ["Field2", "value2"],
        ["Field3", "value3"],
        ["NonExistent", ""],
        ["Field4", ""],
    ],
)
def test_field_value_from_manifest(
    field: str,
    expected: str,
) -> None:
    manifest = JavaManifest(
        main={"Field1": "value1"},
        sections=[
            {"Field2": "value2"},
            {"Field3": "value3"},
        ],
    )
    assert _field_value_from_manifest(manifest, field) == expected


@parametrize_sync(
    args=["created_by", "symbolic_name", "vendor_id", "expected"],
    cases=[
        ["Other Plugin", "", "", ""],
        ["Apache Maven Bundle Plugin", "", "", ""],
        ["Apache Maven Bundle Plugin", "com.example.test", "com.example.test", ""],
        ["Apache Maven Bundle Plugin", "com.example.test", "com.example", "test"],
        ["Apache Maven Bundle Plugin", "test", "com.example", "test"],
    ],
)
def test_extract_name_from_apache_maven_bundle_plugin(
    created_by: str,
    symbolic_name: str,
    vendor_id: str,
    expected: str,
) -> None:
    manifest = JavaManifest(
        main={
            "Created-By": created_by,
            "Bundle-SymbolicName": symbolic_name,
            "Implementation-Vendor-Id": vendor_id,
        },
        sections=None,
    )
    assert extract_name_from_apache_maven_bundle_plugin(manifest) == expected


@parametrize_sync(
    args=["field", "expected"],
    cases=[
        ["", False],
        ["validIdentifier", True],
        ["123invalid", False],
        ["_valid", True],
        ["valid123", True],
        ["valid_123", True],
        ["invalid space", False],
        ["invalid-dash", False],
        ["invalid.dot", False],
    ],
)
def test_is_valid_java_identifier(
    field: str,
    expected: bool,  # noqa: FBT001
) -> None:
    assert is_valid_java_identifier(field) == expected


def test_extract_name_from_archive_filename() -> None:
    cases = [
        ("org.eclipse.test", "org.eclipse.test"),
        ("com.example.test", "test"),
        ("invalid-identifier.test", "invalid-identifier.test"),
    ]

    for name, expected in cases:
        archive = ArchiveFilename(name=name, raw=name, version="1.0.0")
        assert extract_name_from_archive_filename(archive) == expected


@parametrize_sync(
    args=["manifest", "filename", "version", "expected"],
    cases=[
        [
            JavaManifest(
                main={"Implementation-Version": "1.0.0"},
                sections=None,
            ),
            "test.jar",
            "",
            "1.0.0",
        ],
        [
            JavaManifest(
                main={"Specification-Version": "2.0.0"},
                sections=None,
            ),
            "test.jar",
            "",
            "2.0.0",
        ],
        [
            JavaManifest(
                main={"Plugin-Version": "3.0.0"},
                sections=None,
            ),
            "test.jar",
            "",
            "3.0.0",
        ],
        [
            JavaManifest(
                main={"Bundle-Version": "4.0.0"},
                sections=None,
            ),
            "test.jar",
            "",
            "4.0.0",
        ],
        [
            JavaManifest(
                main={},
                sections=None,
            ),
            "test-1.0.0.jar",
            "1.0.0",
            "1.0.0",
        ],
        [
            None,
            "test-1.0.0.jar",
            "1.0.0",
            "1.0.0",
        ],
        [
            None,
            "test.jar",
            "",
            "",
        ],
    ],
)
def test_select_version(
    manifest: JavaManifest | None,
    filename: str,
    version: str,
    expected: str,
) -> None:
    archive = ArchiveFilename(name=filename, raw=filename, version=version)
    assert select_version(manifest, archive) == expected


@parametrize_sync(
    args=["manifest", "filename", "expected"],
    cases=[
        [
            JavaManifest(
                main={"Name": "test-name"},
                sections=None,
            ),
            "",
            "test-name",
        ],
        [
            JavaManifest(
                main={"Bundle-Name": "bundle-name"},
                sections=None,
            ),
            "",
            "bundle-name",
        ],
        [
            JavaManifest(
                main={"Short-Name": "short-name"},
                sections=None,
            ),
            "",
            "short-name",
        ],
        [
            JavaManifest(
                main={"Extension-Name": "extension-name"},
                sections=None,
            ),
            "",
            "extension-name",
        ],
        [
            JavaManifest(
                main={"Implementation-Title": "impl-title"},
                sections=None,
            ),
            "",
            "impl-title",
        ],
        [
            None,
            "",
            "",
        ],
        [
            JavaManifest(
                main={
                    "Created-By": "Apache Maven Bundle Plugin",
                    "Bundle-SymbolicName": "com.example.test",
                    "Implementation-Vendor-Id": "com.example",
                },
                sections=None,
            ),
            "test.jar",
            "test",
        ],
    ],
)
def test_select_name_with_empty_filename(
    manifest: JavaManifest | None,
    filename: str,
    expected: str,
) -> None:
    archive = ArchiveFilename(name=filename, raw=filename, version="")
    assert select_name(manifest, archive) == expected
