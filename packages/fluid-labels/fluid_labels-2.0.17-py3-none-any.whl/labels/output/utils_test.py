import uuid
from pathlib import Path
from unittest.mock import patch

from labels.model.core import OutputFormat, SbomConfig, SourceType
from labels.model.package import HealthMetadata
from labels.model.sources import ImageContext, ImageMetadata
from labels.output.utils import (
    get_author_info,
    get_document_namespace,
    get_relative_path,
    is_valid_email,
    sanitize_name,
    set_namespace_version,
)
from labels.resolvers.container_image import ContainerImage
from labels.resolvers.directory import Directory
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.pytest_marks import parametrize_sync


@parametrize_sync(
    args=["email", "expected"],
    cases=[
        ["test@example.com", True],
        ["user.name@domain.co.uk", True],
        ["invalid.email", False],
        ["@domain.com", False],
        ["user@.com", False],
        ["", False],
    ],
)
def test_is_valid_email(*, email: str, expected: bool) -> None:
    assert is_valid_email(email) == expected


@parametrize_sync(
    args=["authors_string", "expected"],
    cases=[
        [
            "John Doe <john@example.com>, Jane Smith <jane@example.com>",
            [("John Doe", "john@example.com"), ("Jane Smith", "jane@example.com")],
        ],
        [
            "John Doe <invalid.email>, Jane Smith",
            [("John Doe", None), ("Jane Smith", None)],
        ],
        ["Single Author", [("Single Author", None)]],
    ],
)
def test_get_author_info(
    *,
    authors_string: str,
    expected: list[tuple[str | None, str | None]],
) -> None:
    metadata = HealthMetadata(authors=authors_string)
    assert get_author_info(metadata) == expected


@parametrize_sync(
    args=["text", "expected"],
    cases=[
        ["simple-name", "simple-name"],
        ["complex@name#with$symbols", "complex-name-with-symbols"],
        ["version.1.0", "version.1.0"],
        ["space test", "space-test"],
    ],
)
def test_sanitize_name(*, text: str, expected: str) -> None:
    assert sanitize_name(text) == expected


@mocks(
    mocks=[
        Mock(
            module=uuid,
            target="uuid4",
            target_type="function",
            expected=lambda: "12345678-1234-5678-1234-567812345678",
        ),
    ],
)
async def test_get_document_namespace() -> None:
    with (
        patch.object(Path, "is_file", return_value=True),
        patch.object(
            Path,
            "is_dir",
            return_value=False,
        ),
    ):
        namespace = get_document_namespace("test.txt")
        assert (
            namespace
            == "https://fluidattacks.com/file/test.txt-12345678-1234-5678-1234-567812345678"
        )

    with (
        patch.object(Path, "is_file", return_value=False),
        patch.object(
            Path,
            "is_dir",
            return_value=True,
        ),
    ):
        namespace = get_document_namespace("test_dir")
        assert (
            namespace
            == "https://fluidattacks.com/dir/test_dir-12345678-1234-5678-1234-567812345678"
        )

    with (
        patch.object(Path, "is_file", return_value=False),
        patch.object(
            Path,
            "is_dir",
            return_value=False,
        ),
    ):
        namespace = get_document_namespace(".")
        assert (
            namespace
            == "https://fluidattacks.com/unknown-source-type/12345678-1234-5678-1234-567812345678"
        )


def test_get_relative_path() -> None:
    current_dir = Path.cwd()
    test_path = current_dir / "test" / "path"

    assert get_relative_path(str(test_path)) == "test/path"

    absolute_path = "/completely/different/path"
    assert get_relative_path(absolute_path) == absolute_path


def test_set_namespace_version() -> None:
    config = SbomConfig(
        source_type=SourceType.DIRECTORY,
        source="/test/path",
        execution_id="test-id",
        output_format=OutputFormat.CYCLONEDX_JSON,
        output="output.json",
        exclude=(),
        debug=False,
    )
    directory_resolver = Directory(root="/test/path", exclude=())
    namespace, version = set_namespace_version(config, directory_resolver)
    assert namespace == "/test/path"
    assert version is None

    config = SbomConfig(
        source_type=SourceType.DOCKER,
        source="test-image:latest",
        execution_id="test-id",
        output_format=OutputFormat.CYCLONEDX_JSON,
        output="output.json",
        exclude=(),
        debug=False,
    )
    img_metadata = ImageMetadata(
        name="python",
        digest="sha256:abc123",
        repotags=["test-image:latest"],
        created="2023-01-01T00:00:00Z",
        dockerversion="20.10.12",
        architecture="amd64",
        os="linux",
        layers=[],
        layersdata=[],
        image_ref="test-image:latest",
        labels={},
        env=[],
    )
    container_resolver = ContainerImage(
        img=img_metadata,
        context=ImageContext(
            id=img_metadata.digest,
            name=img_metadata.name,
            publisher="",
            arch=img_metadata.architecture,
            size="0",
            full_extraction_dir="temp_dir",
            layers_dir="temp_dir/layers",
            manifest={},
            image_ref=img_metadata.image_ref,
        ),
    )
    namespace, version = set_namespace_version(config, container_resolver)
    assert namespace == "test-image:latest"
    assert version == "sha256:abc123"
