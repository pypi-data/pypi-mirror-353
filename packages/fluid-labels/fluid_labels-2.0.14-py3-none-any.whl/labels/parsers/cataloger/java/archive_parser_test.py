import tempfile
from io import TextIOWrapper
from pathlib import Path
from unittest.mock import Mock, patch
from zipfile import ZipInfo

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from labels.model.file import Coordinates, Location, LocationReadCloser
from labels.model.package import Digest, Language, Package, PackageType
from labels.parsers.cataloger.java import archive_parser
from labels.parsers.cataloger.java.archive_filename import ArchiveFilename
from labels.parsers.cataloger.java.archive_parser import (
    ArchiveParser,
    artifact_id_matches_filename,
    get_digests_from_archive,
    new_java_archive_parser,
    new_package_from_maven_data,
    parse_java_archive,
    pom_project_by_parent,
    pom_properties_by_parent,
    save_archive_to_tmp,
)
from labels.parsers.cataloger.java.model import (
    JavaArchive,
    JavaManifest,
    JavaPomParent,
    JavaPomProject,
    JavaPomProperties,
)
from labels.parsers.cataloger.java.parse_java_manifest import (
    parse_java_manifest,
    select_licenses,
    select_name,
    select_version,
)
from labels.parsers.cataloger.java.parse_pom_xml import ParsedPomProject
from labels.testing.mocks import mocks
from labels.testing.utils.helpers import get_test_data_path
from labels.testing.utils.pytest_marks import parametrize_async, parametrize_sync


def test_parse_java_archive() -> None:
    test_data_path = get_test_data_path("dependencies/java/java-archive/commons-io-2.11.0.jar")

    expected_packages = [
        Package(
            name="commons-io",
            version="2.11.0",
            type=PackageType.JavaPkg,
            language=Language.JAVA,
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                    ),
                ),
            ],
            metadata=JavaArchive(
                virtual_path=test_data_path,
                manifest=JavaManifest(
                    main={
                        "Manifest-Version": "1.0",
                        "Implementation-Title": "Apache Commons IO",
                        "Bundle-Description": (
                            "The Apache Commons IO library contains utility cla"
                        ),
                        "Automatic-Module-Name": "org.apache.commons.io",
                        "Bundle-License": "https://www.apache.org/licenses/LICENSE-2.0.txt",
                        "Bundle-SymbolicName": "org.apache.commons.commons-io",
                        "Implementation-Version": "2.11.0",
                        "Specification-Vendor": "The Apache Software Foundation",
                        "Bnd-LastModified": "1625881350392",
                        "Bundle-ManifestVersion": "2",
                        "Specification-Title": "Apache Commons IO",
                        "Bundle-DocURL": "https://commons.apache.org/proper/commons-io/",
                        "Bundle-Vendor": "The Apache Software Foundation",
                        "Include-Resource": (
                            "META-INF/NOTICE.txt=NOTICE.txt,META-INF/LICENSE.txt="
                        ),
                        "Import-Package": (
                            "sun.misc;resolution:=optional,sun.nio.ch;resolution:=o"
                        ),
                        "Require-Capability": (
                            'osgi.ee;filter:="(&(osgi.ee=JavaSE)(version=1.8))"'
                        ),
                        "Tool": "Bnd-5.1.2.202007211702",
                        "Implementation-Vendor": "The Apache Software Foundation",
                        "Export-Package": (
                            'org.apache.commons.io;version="1.4.9999",org.apache.co'
                        ),
                        "Bundle-Name": "Apache Commons IO",
                        "Bundle-Version": "2.11.0",
                        "Build-Jdk-Spec": "1.8",
                        "Created-By": "Apache Maven Bundle Plugin",
                        "Specification-Version": "2.11",
                    },
                    sections=None,
                ),
                archive_digests=[
                    Digest(
                        algorithm="sha1",
                        value="a2503f302b11ebde7ebc3df41daebe0e4eea3689",
                    ),
                ],
            ),
            licenses=["https://www.apache.org/licenses/LICENSE-2.0.txt"],
            p_url="pkg:maven/commons-io/commons-io@2.11.0",
        ),
        Package(
            name="commons-io",
            version="2.11.0",
            type=PackageType.JavaPkg,
            language=Language.JAVA,
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                    ),
                ),
            ],
            metadata=JavaArchive(
                virtual_path=f"{test_data_path}:commons-io:commons-io",
                manifest=None,
                pom_properties=JavaPomProperties(
                    group_id="commons-io",
                    artifact_id="commons-io",
                    version="2.11.0",
                    path="META-INF/maven/commons-io/commons-io/pom.properties",
                ),
                parent=Package(
                    name="commons-io",
                    version="2.11.0",
                    type=PackageType.JavaPkg,
                    language=Language.JAVA,
                    locations=[
                        Location(
                            coordinates=Coordinates(
                                real_path=test_data_path,
                            ),
                        ),
                    ],
                    metadata=JavaArchive(
                        virtual_path=test_data_path,
                        manifest=JavaManifest(
                            main={
                                "Manifest-Version": "1.0",
                                "Implementation-Title": "Apache Commons IO",
                                "Bundle-Description": (
                                    "The Apache Commons IO library contains utility cla"
                                ),
                                "Automatic-Module-Name": "org.apache.commons.io",
                                "Bundle-License": "https://www.apache.org/licenses/LICENSE-2.0.txt",
                                "Bundle-SymbolicName": "org.apache.commons.commons-io",
                                "Implementation-Version": "2.11.0",
                                "Specification-Vendor": "The Apache Software Foundation",
                                "Bnd-LastModified": "1625881350392",
                                "Bundle-ManifestVersion": "2",
                                "Specification-Title": "Apache Commons IO",
                                "Bundle-DocURL": "https://commons.apache.org/proper/commons-io/",
                                "Bundle-Vendor": "The Apache Software Foundation",
                                "Include-Resource": (
                                    "META-INF/NOTICE.txt=NOTICE.txt,META-INF/LICENSE.txt="
                                ),
                                "Import-Package": (
                                    "sun.misc;resolution:=optional,sun.nio.ch;resolution:=o"
                                ),
                                "Require-Capability": (
                                    'osgi.ee;filter:="(&(osgi.ee=JavaSE)(version=1.8))"'
                                ),
                                "Tool": "Bnd-5.1.2.202007211702",
                                "Implementation-Vendor": "The Apache Software Foundation",
                                "Export-Package": (
                                    'org.apache.commons.io;version="1.4.9999",' "org.apache.co"
                                ),
                                "Bundle-Name": "Apache Commons IO",
                                "Bundle-Version": "2.11.0",
                                "Build-Jdk-Spec": "1.8",
                                "Created-By": "Apache Maven Bundle Plugin",
                                "Specification-Version": "2.11",
                            },
                            sections=None,
                        ),
                        archive_digests=[
                            Digest(
                                algorithm="sha1",
                                value="a2503f302b11ebde7ebc3df41daebe0e4eea3689",
                            ),
                        ],
                    ),
                    licenses=["https://www.apache.org/licenses/LICENSE-2.0.txt"],
                    p_url="pkg:maven/commons-io/commons-io@2.11.0",
                ),
            ),
            licenses=[],
            p_url="pkg:maven/commons-io/commons-io@2.11.0",
        ),
    ]

    with Path(test_data_path).open("rb") as binary:
        reader = TextIOWrapper(binary)
        packages, relationships = parse_java_archive(
            None,
            None,
            LocationReadCloser(
                location=Location(coordinates=Coordinates(real_path=test_data_path)),
                read_closer=reader,
            ),
        )

        assert packages == expected_packages
        assert not relationships


def test_new_package_from_maven_data_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    pom_properties = JavaPomProperties(
        group_id="test",
        artifact_id="test",
        version="1.0",
        path="META-INF/maven/test/test/pom.properties",
    )

    parent_pkg = Package(
        name="test",
        version="1.0",
        type=PackageType.JavaPkg,
        language=Language.JAVA,
        locations=[Location(coordinates=Coordinates(real_path="test.jar"))],
        metadata=JavaArchive(virtual_path="test.jar"),
        licenses=[],
        p_url="pkg:maven/test/test@1.0",
    )

    location = Location(coordinates=Coordinates(real_path="test.jar"))

    with patch("labels.model.package.Package.__init__") as mock_init:
        mock_init.side_effect = ValidationError.from_exception_data(
            title="",
            line_errors=[
                InitErrorDetails(
                    type="missing",
                    loc=("name",),
                    input=None,
                    ctx={},
                ),
            ],
        )

        result = new_package_from_maven_data(pom_properties, None, parent_pkg, location)
        assert result is None
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="contents_from_zip",
            target_type="sync",
            expected={
                "META-INF/MANIFEST.MF": """
                Manifest-Version: 1.0
                Implementation-Title: Test Package
                Implementation-Version: 1.0.0
                """.strip(),
            },
        ),
        Mock(
            module=archive_parser,
            target="get_digests_from_archive",
            target_type="sync",
            expected=[],
        ),
    ],
)
async def test_archive_parser_discover_main_package_validation_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    file_manifest: list[ZipInfo] = [ZipInfo("META-INF/MANIFEST.MF")]
    location = Location(coordinates=Coordinates(real_path="test.jar"))
    file_info = ArchiveFilename(raw="test.jar", name="test", version="1.0")

    parser = ArchiveParser(
        file_manifest=file_manifest,
        location=location,
        archive_path="test.jar",
        content_path="",
        file_info=file_info,
        detect_nested=False,
    )

    with patch("labels.model.package.Package.__init__") as mock_init:
        mock_init.side_effect = ValidationError.from_exception_data(
            title="",
            line_errors=[
                InitErrorDetails(
                    type="missing",
                    loc=("name",),
                    input=None,
                    ctx={},
                ),
            ],
        )

        result = parser.discover_main_package()
        assert result is None
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )


def test_archive_parser_discover_main_package_no_manifest() -> None:
    file_manifest: list[ZipInfo] = []
    location = Location(coordinates=Coordinates(real_path="test.jar"))
    file_info = ArchiveFilename(raw="test.jar", name="test", version="1.0")

    parser = ArchiveParser(
        file_manifest=file_manifest,
        location=location,
        archive_path=None,
        content_path="",
        file_info=file_info,
        detect_nested=False,
    )

    result = parser.discover_main_package()
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="contents_from_zip",
            target_type="sync",
            expected={
                "META-INF/MANIFEST.MF": "",
            },
        ),
        Mock(
            module=archive_parser,
            target="get_digests_from_archive",
            target_type="sync",
            expected=[],
        ),
    ],
)
async def test_archive_parser_discover_main_package_empty_manifest() -> None:
    file_manifest: list[ZipInfo] = [ZipInfo("META-INF/MANIFEST.MF")]
    location = Location(coordinates=Coordinates(real_path="test.jar"))
    file_info = ArchiveFilename(raw="test.jar", name="test", version="1.0")

    parser = ArchiveParser(
        file_manifest=file_manifest,
        location=location,
        archive_path="test.jar",
        content_path="",
        file_info=file_info,
        detect_nested=False,
    )

    result = parser.discover_main_package()
    assert result is not None
    assert result.name == "test"
    assert result.version == "1.0"


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="contents_from_zip",
            target_type="sync",
            expected={
                "META-INF/MANIFEST.MF": """
                Manifest-Version: 1.0
                Implementation-Title: Test Package
                Implementation-Version: 1.0.0
                Bundle-License: https://valid.license
                """.strip(),
            },
        ),
        Mock(
            module=archive_parser,
            target="get_digests_from_archive",
            target_type="sync",
            expected=[],
        ),
    ],
)
async def test_archive_parser_discover_main_package_valid_license() -> None:
    file_manifest: list[ZipInfo] = [ZipInfo("META-INF/MANIFEST.MF")]
    location = Location(coordinates=Coordinates(real_path="test.jar"))
    file_info = ArchiveFilename(raw="test.jar", name="test", version="1.0")

    parser = ArchiveParser(
        file_manifest=file_manifest,
        location=location,
        archive_path="test.jar",
        content_path="",
        file_info=file_info,
        detect_nested=False,
    )

    result = parser.discover_main_package()
    assert result is not None
    assert result.licenses == ["https://valid.license"]


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="contents_from_zip",
            target_type="sync",
            expected={
                "META-INF/MANIFEST.MF": """
                Manifest-Version: 1.0
                Implementation-Title: Test Package
                Implementation-Version: 1.0.0
                Bundle-License: invalid://license
                """.strip(),
            },
        ),
        Mock(
            module=archive_parser,
            target="get_digests_from_archive",
            target_type="sync",
            expected=[Digest(algorithm="sha1", value="test-digest")],
        ),
    ],
)
async def test_archive_parser_discover_main_package_invalid_license() -> None:
    file_manifest: list[ZipInfo] = [ZipInfo("META-INF/MANIFEST.MF")]
    location = Location(coordinates=Coordinates(real_path="test.jar"))
    file_info = ArchiveFilename(raw="test.jar", name="test", version="1.0")

    parser = ArchiveParser(
        file_manifest=file_manifest,
        location=location,
        archive_path="test.jar",
        content_path="",
        file_info=file_info,
        detect_nested=False,
    )

    result = parser.discover_main_package()
    assert result is not None
    assert result.licenses == ["invalid://license"]


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="contents_from_zip",
            target_type="sync",
            expected={},
        ),
    ],
)
async def test_discover_main_package_empty_contents() -> None:
    file_manifest: list[ZipInfo] = [
        ZipInfo("META-INF/MANIFEST.MF"),
    ]
    location = Location(coordinates=Coordinates(real_path="test.jar"))
    file_info = ArchiveFilename(raw="test.jar", name="test", version="1.0")

    parser = ArchiveParser(
        file_manifest=file_manifest,
        location=location,
        archive_path="test.jar",
        content_path="",
        file_info=file_info,
        detect_nested=False,
    )

    result = parser.discover_main_package()
    assert result is None


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="contents_from_zip",
            target_type="sync",
            expected={
                "META-INF/MANIFEST.MF": """
                Manifest-Version: 1.0
                Implementation-Title: Test Package
                Implementation-Version: 1.0.0
                """.strip(),
            },
        ),
        Mock(
            module=archive_parser,
            target="parse_java_manifest",
            target_type="sync",
            expected=JavaManifest(main={"Manifest-Version": "1.0"}),
        ),
        Mock(
            module=archive_parser,
            target="get_digests_from_archive",
            target_type="sync",
            expected=[],
        ),
        Mock(
            module=ArchiveParser,
            target="parse_licenses",
            target_type="sync",
            expected=([], None, None),
        ),
    ],
)
async def test_discover_main_package_no_name_version() -> None:
    file_manifest: list[ZipInfo] = [
        ZipInfo("META-INF/MANIFEST.MF"),
    ]
    location = Location(coordinates=Coordinates(real_path="test.jar"))
    file_info = ArchiveFilename(raw="test.jar", name="test", version="1.0")

    parser = ArchiveParser(
        file_manifest=file_manifest,
        location=location,
        archive_path="test.jar",
        content_path="",
        file_info=file_info,
        detect_nested=False,
    )

    result = parser.discover_main_package()
    assert result is None


@parametrize_sync(
    args=["artifact_id", "filename", "expected_match"],
    cases=[
        ["commons-io", "commons-io", True],
        ["commons-io", "commons-io-2.11.0", True],
        ["spring-boot-starter-web", "spring-boot", True],
        ["", "commons-io", False],
        ["commons-io", "", False],
        ["", "", False],
        ["commons-math", "commons-io", False],
        ["commons", "something-commons", False],
    ],
)
def test_artifact_id_matches_filename(
    artifact_id: str,
    filename: str,
    *,
    expected_match: bool,
) -> None:
    result = artifact_id_matches_filename(artifact_id, filename)
    assert result == expected_match


@parametrize_sync(
    args=["content", "expected_digests"],
    cases=[
        [
            b"test content",
            [
                Digest(
                    algorithm="sha1",
                    value="1eebdf4fdc9fc7bf283031b93f9aef3338de9052",
                ),
            ],
        ],
        [
            b"",
            [],
        ],
    ],
)
def test_new_digests_from_file_with_content_and_empty_bytes(
    content: bytes,
    expected_digests: list[Digest],
) -> None:
    with tempfile.NamedTemporaryFile(mode="wb") as tmp:
        tmp.write(content)
        tmp.flush()

        digests = get_digests_from_archive(tmp.name)
        assert digests == expected_digests


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="new_digests_from_file",
            target_type="sync",
            expected=[],
        ),
    ],
)
async def test_get_digests_from_empty_file_with_zero_size() -> None:
    with tempfile.NamedTemporaryFile() as tmp:
        digests = get_digests_from_archive(tmp.name)
        assert digests == []


@parametrize_async(
    args=["file_contents", "expected_properties"],
    cases=[
        [
            {
                "META-INF/maven/commons-io/commons-io/pom.properties": """
                groupId=commons-io
                artifactId=commons-io
                version=2.11.0
                """,
            },
            {
                "META-INF/maven/commons-io/commons-io": JavaPomProperties(
                    group_id="commons-io",
                    artifact_id="commons-io",
                    version="2.11.0",
                    path="META-INF/maven/commons-io/commons-io/pom.properties",
                ),
            },
        ],
        [
            {
                "META-INF/maven/empty/empty/pom.properties": "",
            },
            {},
        ],
        [
            {
                "META-INF/maven/invalid/invalid/pom.properties": "invalid content",
            },
            {},
        ],
        [
            {
                "META-INF/maven/incomplete/incomplete/pom.properties": """
                artifactId=incomplete
                """,
            },
            {},
        ],
    ],
)
async def test_pom_properties_by_parent(
    file_contents: dict[str, str],
    expected_properties: dict[str, JavaPomProperties],
) -> None:
    with patch("labels.parsers.cataloger.java.archive_parser.contents_from_zip") as mock_contents:
        mock_contents.return_value = file_contents
        extract_paths = ["META-INF/maven/*/*/pom.properties"]
        result = pom_properties_by_parent("test.jar", extract_paths)
        assert result == expected_properties


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="contents_from_zip",
            target_type="sync",
            expected={
                "META-INF/maven/empty/empty/pom.properties": "",
            },
        ),
    ],
)
async def test_pom_properties_by_parent_empty_content() -> None:
    result = pom_properties_by_parent("test.jar", ["META-INF/maven/empty/empty/pom.properties"])
    assert result == {}


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="contents_from_zip",
            target_type="sync",
            expected={
                "META-INF/maven/invalid/invalid/pom.properties": """
                artifactId=test
                """,
            },
        ),
    ],
)
async def test_pom_properties_by_parent_invalid_properties() -> None:
    result = pom_properties_by_parent(
        "test.jar",
        ["META-INF/maven/invalid/invalid/pom.properties"],
    )
    assert result == {}


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="contents_from_zip",
            target_type="sync",
            expected={
                "META-INF/maven/commons-io/commons-io": JavaPomProperties(
                    group_id="commons-io",
                    artifact_id="commons-io",
                    version="2.11.0",
                    path="META-INF/maven/commons-io/commons-io/pom.properties",
                ),
            },
        ),
        Mock(
            module=archive_parser,
            target="parse_pom_properties",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_pom_properties_by_parent_no_properties() -> None:
    extract_paths = ["META-INF/maven/*/*/pom.properties"]
    result = pom_properties_by_parent("test.jar", extract_paths)
    assert result == {}


@parametrize_sync(
    args=["file_contents", "expected_projects"],
    cases=[
        [
            {
                "META-INF/maven/commons-io/commons-io/pom.xml": """
                <project>
                    <artifactId>commons-io</artifactId>
                    <version>2.11.0</version>
                </project>
                """,
            },
            {
                "META-INF/maven/commons-io/commons-io": ParsedPomProject(
                    java_pom_project=JavaPomProject(
                        path="META-INF/maven/commons-io/commons-io/pom.xml",
                        group_id="",
                        artifact_id="commons-io",
                        version="2.11.0",
                        name="",
                        description="",
                        url="",
                    ),
                    licenses=[],
                ),
            },
        ],
        [
            {
                "META-INF/maven/child/module/pom.xml": """
                <project>
                    <artifactId>child-module</artifactId>
                    <parent>
                        <groupId>org.example</groupId>
                        <artifactId>parent</artifactId>
                        <version>1.0.0</version>
                    </parent>
                </project>
                """,
            },
            {
                "META-INF/maven/child/module": ParsedPomProject(
                    java_pom_project=JavaPomProject(
                        path="META-INF/maven/child/module/pom.xml",
                        group_id="",
                        artifact_id="child-module",
                        version="",
                        name="",
                        parent=JavaPomParent(
                            group_id="org.example",
                            artifact_id="parent",
                            version="1.0.0",
                        ),
                        description="",
                        url="",
                    ),
                    licenses=[],
                ),
            },
        ],
        [
            {
                "META-INF/maven/empty/empty/pom.xml": "",
            },
            {},
        ],
        [
            {
                "META-INF/maven/invalid/invalid/pom.xml": "invalid xml content",
            },
            {},
        ],
        [
            {
                "META-INF/maven/incomplete/incomplete/pom.xml": """
                <project>
                    <groupId>test</groupId>
                </project>
                """,
            },
            {},
        ],
        [
            {},
            {},
        ],
    ],
)
def test_pom_project_by_parent(
    file_contents: dict[str, str],
    expected_projects: dict[str, ParsedPomProject],
) -> None:
    with patch("labels.parsers.cataloger.java.archive_parser.contents_from_zip") as mock_contents:
        mock_contents.return_value = file_contents

        location = Location(coordinates=Coordinates(real_path="test.jar"))
        extract_paths = ["META-INF/maven/*/*/pom.xml"]
        result = pom_project_by_parent("test.jar", location, extract_paths)
        assert result == expected_projects


@parametrize_sync(
    args=["manifest_content", "filename_name", "expected_name", "expected_version"],
    cases=[
        [
            """
            Manifest-Version: 1.0
            Implementation-Title: Test Package
            Implementation-Version: 1.0.0
            """,
            "test-package",
            "test-package",
            "1.0.0",
        ],
        [
            """
            Manifest-Version: 1.0
            Bundle-SymbolicName: org.test.package
            Bundle-Version: 2.0.0
            """,
            "test-package",
            "test-package",
            "2.0.0",
        ],
        [
            """
            Manifest-Version: 1.0
            Specification-Title: Test Spec
            Specification-Version: 3.0.0
            """,
            "test-package",
            "test-package",
            "3.0.0",
        ],
        [
            """
            Manifest-Version: 1.0
            """,
            "",
            "",
            "",
        ],
    ],
)
def test_manifest_name_version_selection(
    manifest_content: str,
    filename_name: str,
    expected_name: str,
    expected_version: str,
) -> None:
    manifest = parse_java_manifest(manifest_content)
    filename_obj = ArchiveFilename(raw="test.jar", name=filename_name, version="")
    name = select_name(manifest, filename_obj)
    version = select_version(manifest, filename_obj)
    assert name == expected_name
    assert version == expected_version


@parametrize_sync(
    args=["manifest_content", "expected_licenses"],
    cases=[
        [
            """
            Manifest-Version: 1.0
            Bundle-License: https://license1.com,https://license2.com
            """,
            ["https://license1.com,https://license2.com"],
        ],
        [
            """
            Manifest-Version: 1.0
            Bundle-License: invalid://license
            """,
            ["invalid://license"],
        ],
        [
            """
            Manifest-Version: 1.0
            """,
            [],
        ],
    ],
)
def test_manifest_license_selection(
    manifest_content: str,
    expected_licenses: list[str],
) -> None:
    manifest = parse_java_manifest(manifest_content)
    licenses = select_licenses(manifest)
    assert licenses == expected_licenses


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="contents_from_zip",
            target_type="sync",
            expected={
                "META-INF/MANIFEST.MF": """
                Manifest-Version: 1.0
                Implementation-Title: Apache Commons IO
                Bundle-SymbolicName: org.apache.commons.commons-io
                Implementation-Version: 2.11.0
                """.strip(),
            },
        ),
        Mock(
            module=archive_parser,
            target="get_digests_from_archive",
            target_type="sync",
            expected=[Digest(algorithm="sha1", value="test-digest")],
        ),
    ],
)
async def test_archive_parser_parse() -> None:
    file_manifest = [
        ZipInfo("META-INF/MANIFEST.MF"),
        ZipInfo("META-INF/maven/commons-io/commons-io/pom.properties"),
        ZipInfo("META-INF/maven/commons-io/commons-io/pom.xml"),
    ]

    location = Location(coordinates=Coordinates(real_path="test.jar"))
    archive_path = "test.jar"
    file_info = ArchiveFilename(raw="commons-io-2.11.0.jar", name="commons-io", version="2.11.0")

    parser = ArchiveParser(
        file_manifest=file_manifest,
        location=location,
        archive_path=archive_path,
        content_path="",
        file_info=file_info,
        detect_nested=False,
    )

    packages, relationships = parser.parse()

    assert packages is not None

    assert len(packages) == 1
    assert relationships == []

    main_pkg = packages[0]
    assert main_pkg.name == "commons-io"
    assert main_pkg.version == "2.11.0"
    assert main_pkg.type == PackageType.JavaPkg
    assert main_pkg.language == Language.JAVA


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="contents_from_zip",
            target_type="sync",
            expected={},
        ),
    ],
)
async def test_parse_no_main_package() -> None:
    file_manifest: list[ZipInfo] = [
        ZipInfo("META-INF/MANIFEST.MF"),
    ]
    location = Location(coordinates=Coordinates(real_path="test.jar"))
    file_info = ArchiveFilename(raw="test.jar", name="test", version="1.0")

    parser = ArchiveParser(
        file_manifest=file_manifest,
        location=location,
        archive_path="test.jar",
        content_path="",
        file_info=file_info,
        detect_nested=False,
    )

    packages, relationships = parser.parse()
    assert packages is None
    assert relationships is None


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="contents_from_zip",
            target_type="sync",
            expected={
                "META-INF/MANIFEST.MF": "",
            },
        ),
        Mock(
            module=archive_parser,
            target="get_digests_from_archive",
            target_type="sync",
            expected=[],
        ),
    ],
)
async def test_parse_with_empty_manifest() -> None:
    file_manifest: list[ZipInfo] = [
        ZipInfo("META-INF/MANIFEST.MF"),
    ]
    location = Location(coordinates=Coordinates(real_path="test.jar"))
    file_info = ArchiveFilename(raw="test.jar", name="test", version="1.0")

    parser = ArchiveParser(
        file_manifest=file_manifest,
        location=location,
        archive_path="test.jar",
        content_path="",
        file_info=file_info,
        detect_nested=False,
    )

    packages, relationships = parser.parse()
    assert packages is not None
    assert len(packages) == 1

    package = packages[0]
    assert package.name == "test"
    assert package.version == "1.0"
    assert package.type == PackageType.JavaPkg
    assert package.language == Language.JAVA
    assert isinstance(package.metadata, JavaArchive)
    assert package.metadata.manifest == JavaManifest(main={})
    assert package.metadata.archive_digests == []
    assert relationships == []


@parametrize_sync(
    args=["pom_properties", "parent_pkg", "expected_package"],
    cases=[
        [
            JavaPomProperties(
                group_id="test",
                artifact_id="test",
                version="1.0",
                path="META-INF/maven/test/test/pom.properties",
            ),
            Package(
                name="test",
                version="1.0",
                type=PackageType.JavaPkg,
                language=Language.JAVA,
                locations=[Location(coordinates=Coordinates(real_path="test.jar"))],
                metadata=JavaArchive(virtual_path="test.jar"),
                licenses=[],
                p_url="pkg:maven/test/test@1.0",
            ),
            Package(
                name="test",
                version="1.0",
                type=PackageType.JavaPkg,
                language=Language.JAVA,
                locations=[Location(coordinates=Coordinates(real_path="test.jar"))],
                metadata=JavaArchive(
                    virtual_path="test.jar:test:test",
                    pom_properties=JavaPomProperties(
                        group_id="test",
                        artifact_id="test",
                        version="1.0",
                        path="META-INF/maven/test/test/pom.properties",
                    ),
                    parent=Package(
                        name="test",
                        version="1.0",
                        type=PackageType.JavaPkg,
                        language=Language.JAVA,
                        locations=[Location(coordinates=Coordinates(real_path="test.jar"))],
                        metadata=JavaArchive(virtual_path="test.jar"),
                        licenses=[],
                        p_url="pkg:maven/test/test@1.0",
                    ),
                ),
                licenses=[],
                p_url="pkg:maven/test/test@1.0",
            ),
        ],
        [
            JavaPomProperties(
                group_id="different",
                artifact_id="test",
                version="1.0",
                path="META-INF/maven/different/test/pom.properties",
            ),
            Package(
                name="test",
                version="1.0",
                type=PackageType.JavaPkg,
                language=Language.JAVA,
                locations=[Location(coordinates=Coordinates(real_path="test.jar"))],
                metadata=JavaArchive(virtual_path="test.jar"),
                licenses=[],
                p_url="pkg:maven/test/test@1.0",
            ),
            Package(
                name="test",
                version="1.0",
                type=PackageType.JavaPkg,
                language=Language.JAVA,
                locations=[Location(coordinates=Coordinates(real_path="test.jar"))],
                metadata=JavaArchive(
                    virtual_path="test.jar:different:test",
                    pom_properties=JavaPomProperties(
                        group_id="different",
                        artifact_id="test",
                        version="1.0",
                        path="META-INF/maven/different/test/pom.properties",
                    ),
                    parent=Package(
                        name="test",
                        version="1.0",
                        type=PackageType.JavaPkg,
                        language=Language.JAVA,
                        locations=[Location(coordinates=Coordinates(real_path="test.jar"))],
                        metadata=JavaArchive(virtual_path="test.jar"),
                        licenses=[],
                        p_url="pkg:maven/test/test@1.0",
                    ),
                ),
                licenses=[],
                p_url="pkg:maven/different/test@1.0",
            ),
        ],
        [
            JavaPomProperties(
                group_id="test",
                artifact_id="test",
                version="1.0",
                path="META-INF/maven/test/test/pom.properties",
            ),
            Package(
                name="test",
                version="1.0",
                type=PackageType.JavaPkg,
                language=Language.JAVA,
                locations=[Location(coordinates=Coordinates(real_path="test.jar"))],
                metadata=JavaArchive(
                    virtual_path="test.jar",
                    pom_properties=JavaPomProperties(
                        group_id="test",
                        artifact_id="test",
                        version="1.0",
                        path="META-INF/maven/test/test/pom.properties",
                    ),
                ),
                licenses=[],
                p_url="pkg:maven/test/test@1.0",
            ),
            Package(
                name="test",
                version="1.0",
                type=PackageType.JavaPkg,
                language=Language.JAVA,
                locations=[Location(coordinates=Coordinates(real_path="test.jar"))],
                metadata=JavaArchive(
                    virtual_path="test.jar",
                    pom_properties=JavaPomProperties(
                        group_id="test",
                        artifact_id="test",
                        version="1.0",
                        path="META-INF/maven/test/test/pom.properties",
                    ),
                    parent=Package(
                        name="test",
                        version="1.0",
                        type=PackageType.JavaPkg,
                        language=Language.JAVA,
                        locations=[Location(coordinates=Coordinates(real_path="test.jar"))],
                        metadata=JavaArchive(
                            virtual_path="test.jar",
                            pom_properties=JavaPomProperties(
                                group_id="test",
                                artifact_id="test",
                                version="1.0",
                                path="META-INF/maven/test/test/pom.properties",
                            ),
                        ),
                        licenses=[],
                        p_url="pkg:maven/test/test@1.0",
                    ),
                ),
                licenses=[],
                p_url="pkg:maven/test/test@1.0",
            ),
        ],
    ],
)
def test_new_package_from_maven_data(
    pom_properties: JavaPomProperties,
    parent_pkg: Package,
    expected_package: Package,
) -> None:
    location = Location(coordinates=Coordinates(real_path="test.jar"))
    result = new_package_from_maven_data(pom_properties, None, parent_pkg, location)
    assert result == expected_package


def test_new_package_from_maven_data_no_artifact_id_version() -> None:
    pom_properties = JavaPomProperties(
        group_id="test-group",
        artifact_id="",
        version="",
        path="META-INF/maven/test-group/test/pom.properties",
    )

    parent_pkg = Package(
        name="test",
        version="1.0",
        type=PackageType.JavaPkg,
        language=Language.JAVA,
        locations=[Location(coordinates=Coordinates(real_path="test.jar"))],
        metadata=JavaArchive(virtual_path="test.jar"),
        licenses=[],
        p_url="pkg:maven/test/test@1.0",
    )

    location = Location(coordinates=Coordinates(real_path="test.jar"))

    result = new_package_from_maven_data(pom_properties, None, parent_pkg, location)
    assert result is None


def test_archive_parser_discover_pkgs_from_all_maven_files_no_parent() -> None:
    parser = ArchiveParser(
        file_manifest=[],
        location=Location(coordinates=Coordinates(real_path="test.jar")),
        archive_path="test.jar",
        content_path="",
        file_info=ArchiveFilename(raw="test.jar", name="test", version="1.0"),
        detect_nested=False,
    )

    result = parser.discover_pkgs_from_all_maven_files(None)
    assert result == []


def test_archive_parser_discover_pkgs_from_all_maven_files_no_archive_path() -> None:
    parser = ArchiveParser(
        file_manifest=[],
        location=Location(coordinates=Coordinates(real_path="test.jar")),
        archive_path=None,
        content_path="",
        file_info=ArchiveFilename(raw="test.jar", name="test", version="1.0"),
        detect_nested=False,
    )

    parent_pkg = Package(
        name="test",
        version="1.0",
        type=PackageType.JavaPkg,
        language=Language.JAVA,
        locations=[Location(coordinates=Coordinates(real_path="test.jar"))],
        metadata=JavaArchive(virtual_path="test.jar"),
        licenses=[],
        p_url="pkg:maven/test/test@1.0",
    )

    result = parser.discover_pkgs_from_all_maven_files(parent_pkg)
    assert result == []


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="pom_properties_by_parent",
            target_type="sync",
            expected={
                "META-INF/maven/test/test": JavaPomProperties(
                    group_id="test",
                    artifact_id="test",
                    version="",
                    path="META-INF/maven/test/test/pom.properties",
                ),
            },
        ),
        Mock(
            module=archive_parser,
            target="pom_project_by_parent",
            target_type="sync",
            expected={},
        ),
        Mock(
            module=archive_parser,
            target="new_package_from_maven_data",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_discover_pkgs_from_all_maven_files_no_package() -> None:
    file_manifest: list[ZipInfo] = [
        ZipInfo("META-INF/maven/test/test/pom.properties"),
    ]
    location = Location(coordinates=Coordinates(real_path="test.jar"))
    file_info = ArchiveFilename(raw="test.jar", name="test", version="1.0")

    parent_pkg = Package(
        name="test",
        version="1.0",
        type=PackageType.JavaPkg,
        language=Language.JAVA,
        locations=[location],
        metadata=JavaArchive(virtual_path="test.jar"),
        licenses=[],
        p_url="pkg:maven/test/test@1.0",
    )

    parser = ArchiveParser(
        file_manifest=file_manifest,
        location=location,
        archive_path="test.jar",
        content_path="",
        file_info=file_info,
        detect_nested=False,
    )

    result = parser.discover_pkgs_from_all_maven_files(parent_pkg)
    assert result == []


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="contents_from_zip",
            target_type="sync",
            expected={
                "META-INF/LICENSE": "",
            },
        ),
    ],
)
async def test_parse_licenses_from_file_empty_licenses() -> None:
    file_manifest: list[ZipInfo] = [
        ZipInfo("META-INF/LICENSE"),
    ]
    location = Location(coordinates=Coordinates(real_path="test.jar"))
    file_info = ArchiveFilename(raw="test.jar", name="test", version="1.0")

    parser = ArchiveParser(
        file_manifest=file_manifest,
        location=location,
        archive_path="test.jar",
        content_path="",
        file_info=file_info,
        detect_nested=False,
    )

    manifest = JavaManifest(main={})
    licenses, name, version = parser.parse_licenses(manifest)

    assert licenses == []
    assert name == "test"
    assert version == "1.0"


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="contents_from_zip",
            target_type="sync",
            expected={
                "META-INF/LICENSE": """
                    MIT License

                    Copyright (c) 2024 Test Project

                    Permission is hereby granted, free of charge, to any person obtaining a
                    copy of this software and associated documentation files (the "Software"),
                    to deal in the Software without restriction, including without limitation
                    the rights to use, copy, modify, merge, publish, distribute, sublicense,
                    and/or sell copies of the Software, and to permit persons to whom the
                    Software is furnished to do so, subject to the following conditions:

                    The above copyright notice and this permission notice shall be included
                    in all copies or substantial portions of the Software.

                    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
                    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
                    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
                    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
                    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
                    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
                    DEALINGS IN THE SOFTWARE.
                    """,
            },
        ),
    ],
)
async def test_parse_license_from_file() -> None:
    file_manifest: list[ZipInfo] = [
        ZipInfo("META-INF/LICENSE"),
    ]
    location = Location(coordinates=Coordinates(real_path="test.jar"))
    file_info = ArchiveFilename(raw="test.jar", name="test", version="1.0")

    parser = ArchiveParser(
        file_manifest=file_manifest,
        location=location,
        archive_path="test.jar",
        content_path="",
        file_info=file_info,
        detect_nested=False,
    )

    manifest = JavaManifest(main={})
    licenses, name, version = parser.parse_licenses(manifest)
    assert licenses == ["MIT"]
    assert name == "test"
    assert version == "1.0"


@mocks(
    mocks=[
        Mock(
            module=archive_parser,
            target="save_archive_to_tmp",
            target_type="sync",
            expected=(None, None, lambda: None),
        ),
    ],
)
async def test_new_java_archive_parser_no_paths(caplog: pytest.LogCaptureFixture) -> None:
    with tempfile.NamedTemporaryFile(mode="w+b") as tmp:
        reader = LocationReadCloser(
            location=Location(coordinates=Coordinates(real_path=tmp.name)),
            read_closer=TextIOWrapper(tmp),
        )

        parser, cleanup_fn = new_java_archive_parser(reader, detect_nested=True)

        assert parser is None
        assert cleanup_fn is None
        assert "unable to read files from java archive" in caplog.text


def test_save_archive_to_tmp() -> None:
    with tempfile.NamedTemporaryFile(mode="w+b") as tmp:
        reader = TextIOWrapper(tmp)
        content_dir, archive_path, cleanup_fn = save_archive_to_tmp(tmp.name, reader)
        assert content_dir is not None
        assert archive_path is not None
        assert callable(cleanup_fn)
        cleanup_fn()


def test_parse_java_archive_no_parser() -> None:
    with tempfile.TemporaryFile() as tmp:
        reader = LocationReadCloser(
            location=Location(),
            read_closer=TextIOWrapper(tmp),
        )

        packages, relationships = parse_java_archive(None, None, reader)
        assert packages == []
        assert relationships == []


def test_extract_properties_and_projects_no_archive_path() -> None:
    file_info = ArchiveFilename(raw="test.jar", name="test", version="1.0")
    location = Location(coordinates=Coordinates(real_path="test.jar"))

    parser = ArchiveParser(
        file_manifest=[
            ZipInfo("META-INF/maven/test/test/pom.properties"),
            ZipInfo("META-INF/maven/test/test/pom.xml"),
        ],
        location=location,
        archive_path=None,
        content_path="",
        file_info=file_info,
        detect_nested=False,
    )

    properties, projects = parser.extract_properties_and_projects()

    assert properties == {}
    assert projects == {}


def test_extract_name_version_from_project() -> None:
    file_info = ArchiveFilename(raw="test.jar", name="test", version="1.0")
    location = Location(coordinates=Coordinates(real_path="test.jar"))
    parser = ArchiveParser(
        file_manifest=[],
        location=location,
        archive_path=None,
        content_path="",
        file_info=file_info,
        detect_nested=False,
    )

    properties = JavaPomProperties(
        group_id="test",
        artifact_id="",
        version="",
        path="test",
    )

    project = ParsedPomProject(
        java_pom_project=JavaPomProject(
            artifact_id="test-artifact",
            version="2.0",
            parent=None,
        ),
        licenses=[],
    )

    name, version = parser.extract_name_version(properties, project)
    assert name == "test-artifact"
    assert version == "2.0"


@parametrize_sync(
    args=["properties_dict", "projects_dict", "file_name"],
    cases=[
        [
            {
                "path/to/pom": JavaPomProperties(
                    group_id="test",
                    artifact_id="",
                    version="1.0",
                    path="test",
                ),
            },
            {
                "path/to/pom": ParsedPomProject(
                    java_pom_project=JavaPomProject(
                        artifact_id="test",
                        version="1.0",
                        parent=None,
                    ),
                    licenses=[],
                ),
            },
            "test",
        ],
        [
            {
                "path/to/pom": JavaPomProperties(
                    group_id="test",
                    artifact_id="different",
                    version="1.0",
                    path="test",
                ),
            },
            {
                "path/to/pom": ParsedPomProject(
                    java_pom_project=JavaPomProject(
                        artifact_id="different",
                        version="1.0",
                        parent=None,
                    ),
                    licenses=[],
                ),
            },
            "test",
        ],
        [
            {
                "path/to/pom": JavaPomProperties(
                    group_id="test",
                    artifact_id="test",
                    version="1.0",
                    path="test",
                ),
            },
            {
                "different/path": ParsedPomProject(
                    java_pom_project=JavaPomProject(
                        artifact_id="test",
                        version="1.0",
                        parent=None,
                    ),
                    licenses=[],
                ),
            },
            "test",
        ],
    ],
)
def test_find_relevant_objects_no_match(
    properties_dict: dict[str, JavaPomProperties],
    projects_dict: dict[str, ParsedPomProject],
    file_name: str,
) -> None:
    file_info = ArchiveFilename(raw=f"{file_name}.jar", name=file_name, version="1.0")
    location = Location(coordinates=Coordinates(real_path="test.jar"))
    parser = ArchiveParser(
        file_manifest=[],
        location=location,
        archive_path=None,
        content_path="",
        file_info=file_info,
        detect_nested=False,
    )

    properties_obj, project_obj = parser.find_relevant_objects(properties_dict, projects_dict)
    assert properties_obj is None
    assert project_obj is None
