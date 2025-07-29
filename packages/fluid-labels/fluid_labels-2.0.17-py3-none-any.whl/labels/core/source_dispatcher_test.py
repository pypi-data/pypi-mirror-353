import os
from unittest.mock import MagicMock

import labels.core.source_dispatcher
from labels.core.source_dispatcher import (
    _handle_directory,
    _handle_docker,
    _handle_ecr,
    resolve_sbom_source,
)
from labels.model.core import OutputFormat, SbomConfig, SourceType
from labels.model.sources import AwsCredentials, ImageContext, ImageMetadata, LayerData
from labels.resolvers.container_image import ContainerImage
from labels.resolvers.directory import Directory
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.pytest_marks import parametrize_sync
from labels.testing.utils.pytest_methods import raises
from labels.utils.exceptions import (
    AwsExternalIdNotDefinedError,
    AwsRoleNotDefinedError,
    UnexpectedSBOMSourceError,
)

IMAGE_METADATA = ImageMetadata(
    name="python",
    digest="sha256:a123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    repotags=["python:3.10", "python:latest"],
    created="2023-01-01T00:00:00Z",
    dockerversion="20.10.12",
    labels={"maintainer": "Python Software Foundation", "version": "3.10"},
    architecture="amd64",
    os="linux",
    layers=[
        "sha256:layer1hash123456789abcdef",
        "sha256:layer2hash123456789abcdef",
    ],
    layersdata=[
        LayerData(
            digest="sha256:layer1hash123456789abcdef",
            size=10000000,
            mimetype="application/vnd.docker.image.rootfs.diff.tar.gzip",
            annotations={
                "org.opencontainers.image.ref.name": "python:3.10",
                "org.opencontainers.image.created": "2023-01-01T00:00:00Z",
            },
        ),
        LayerData(
            digest="sha256:layer2hash123456789abcdef",
            size=5000000,
            mimetype="application/vnd.docker.image.rootfs.diff.tar.gzip",
            annotations={
                "org.opencontainers.image.ref.name": "python:latest",
                "org.opencontainers.image.created": "2023-01-01T00:00:00Z",
            },
        ),
    ],
    env=["PATH=/usr/local/bin", "PYTHON_VERSION=3.10"],
    image_ref="docker.io/library/python:3.10",
)

IMAGE_CONTEXT = ImageContext(
    id="sha256:mocked_id",
    name="dummy-name",
    publisher="",
    arch="x86",
    size="1000",
    full_extraction_dir="temp_dir",
    layers_dir="layers_dir",
    manifest={"manifest": "mocked_manifest"},  # type: ignore[misc]
    image_ref="dummy_image",
)


@parametrize_sync(
    args=["source_path", "exclude"],
    cases=[
        ["./", ()],
        ["./", ("node_modules", "dist")],
    ],
)
def test_handle_directory(source_path: str, exclude: tuple[str, ...]) -> None:
    sbom_config = SbomConfig(
        source_type=SourceType.DIRECTORY,
        source=source_path,
        exclude=exclude,
        execution_id=None,
        output_format=OutputFormat.FLUID_JSON,
        output="test_output",
        docker_user=None,
        docker_password=None,
        aws_external_id=None,
        aws_role=None,
        debug=False,
    )

    result = _handle_directory(sbom_config)

    assert isinstance(result, Directory)
    assert result.root == os.path.realpath(source_path)
    assert result.exclude == exclude


@mocks(
    mocks=[
        Mock(
            module=labels.core.source_dispatcher,
            target="get_docker_image",
            target_type="sync",
            expected=IMAGE_METADATA,
        ),
        Mock(
            module=labels.core.source_dispatcher,
            target="get_image_context",
            target_type="sync",
            expected=IMAGE_CONTEXT,
        ),
    ],
)
async def test_handle_docker_returns_container_image() -> None:
    sbom_config = SbomConfig(
        source_type=SourceType.DOCKER,
        source="python:3.10",
        exclude=(),
        execution_id=None,
        output_format=OutputFormat.FLUID_JSON,
        output="output_file",
        docker_user="user",
        docker_password="pass",  # noqa: S106
        aws_external_id=None,
        aws_role=None,
        debug=False,
    )

    result = _handle_docker(sbom_config=sbom_config, is_daemon=True)

    assert isinstance(result, ContainerImage)
    assert result.img == IMAGE_METADATA
    assert result.context == IMAGE_CONTEXT


@mocks(
    mocks=[
        Mock(
            module=labels.core.source_dispatcher,
            target="_get_async_ecr_connection",
            target_type="sync",
            expected=("dummy_token", IMAGE_METADATA),
        ),
        Mock(
            module=labels.core.source_dispatcher,
            target="get_image_context",
            target_type="sync",
            expected=IMAGE_CONTEXT,
        ),
    ],
)
async def test_handle_ecr_returns_container_image() -> None:
    sbom_config = SbomConfig(
        source_type=SourceType.ECR,
        source="123456789012.dkr.ecr.us-east-1.amazonaws.com/my-repo:latest",
        exclude=(),
        execution_id=None,
        output_format=OutputFormat.FLUID_JSON,
        output="output_file",
        docker_user=None,
        docker_password=None,
        aws_external_id="external-id",
        aws_role="arn:aws:iam::123456789012:role/my-role",
        debug=False,
    )

    result = _handle_ecr(sbom_config=sbom_config)

    assert isinstance(result, ContainerImage)
    assert result.img == IMAGE_METADATA
    assert result.context == IMAGE_CONTEXT


async def test_handle_ecr_raises_error_when_aws_role_not_defined() -> None:
    sbom_config = SbomConfig(
        source_type=SourceType.ECR,
        source="123456789012.dkr.ecr.us-east-1.amazonaws.com/my-repo:latest",
        exclude=(),
        execution_id=None,
        output_format=OutputFormat.FLUID_JSON,
        output="output_file",
        docker_user=None,
        docker_password=None,
        aws_external_id="external-id",
        aws_role=None,
        debug=False,
    )

    with raises(AwsRoleNotDefinedError):
        _handle_ecr(sbom_config=sbom_config)


async def test_handle_ecr_raises_error_when_aws_exteranl_id_not_defined() -> None:
    sbom_config = SbomConfig(
        source_type=SourceType.ECR,
        source="123456789012.dkr.ecr.us-east-1.amazonaws.com/my-repo:latest",
        exclude=(),
        execution_id=None,
        output_format=OutputFormat.FLUID_JSON,
        output="output_file",
        docker_user=None,
        docker_password=None,
        aws_external_id=None,
        aws_role="role",
        debug=False,
    )

    with raises(AwsExternalIdNotDefinedError):
        _handle_ecr(sbom_config=sbom_config)


@mocks(
    mocks=[
        Mock(
            module=labels.core.source_dispatcher,
            target="_handle_directory",
            target_type="sync",
            expected=Directory(root="./"),
        ),
    ],
)
async def test_resolve_sbom_source_for_directory() -> None:
    sbom_config = SbomConfig(
        source_type=SourceType.DIRECTORY,
        source="./",
        exclude=(),
        execution_id=None,
        output_format=OutputFormat.FLUID_JSON,
        output="output_file",
        docker_user=None,
        docker_password=None,
        aws_external_id=None,
        aws_role=None,
        debug=False,
    )

    result = resolve_sbom_source(sbom_config)
    assert isinstance(result, Directory)


@mocks(
    mocks=[
        Mock(
            module=labels.core.source_dispatcher,
            target="_handle_docker",
            target_type="sync",
            expected=ContainerImage(img=IMAGE_METADATA, context=IMAGE_CONTEXT),
        ),
    ],
)
async def test_resolve_sbom_source_for_docker() -> None:
    sbom_config = SbomConfig(
        source_type=SourceType.DOCKER,
        source="python:3.10",
        exclude=(),
        execution_id=None,
        output_format=OutputFormat.FLUID_JSON,
        output="output_file",
        docker_user=None,
        docker_password=None,
        aws_external_id=None,
        aws_role=None,
        debug=False,
    )

    result = resolve_sbom_source(sbom_config)

    assert isinstance(result, ContainerImage)


@mocks(
    mocks=[
        Mock(
            module=labels.core.source_dispatcher,
            target="_handle_ecr",
            target_type="sync",
            expected=ContainerImage(img=IMAGE_METADATA, context=IMAGE_CONTEXT),
        ),
    ],
)
async def test_resolve_sbom_source_for_ecr() -> None:
    sbom_config = SbomConfig(
        source_type=SourceType.ECR,
        source="./",
        exclude=(),
        execution_id=None,
        output_format=OutputFormat.FLUID_JSON,
        output="output_file",
        docker_user=None,
        docker_password=None,
        aws_external_id=None,
        aws_role=None,
        debug=False,
    )

    result = resolve_sbom_source(sbom_config)
    assert isinstance(result, Directory)


@mocks(
    mocks=[
        Mock(
            module=labels.core.source_dispatcher,
            target="_handle_docker",
            target_type="sync",
            expected=ContainerImage(img=IMAGE_METADATA, context=IMAGE_CONTEXT),
        ),
    ],
)
async def test_resolve_sbom_source_for_docker_daemon() -> None:
    sbom_config = SbomConfig(
        source_type=SourceType.DOCKER_DAEMON,
        source="python:3.10",
        exclude=(),
        execution_id=None,
        output_format=OutputFormat.FLUID_JSON,
        output="output_file",
        docker_user=None,
        docker_password=None,
        aws_external_id=None,
        aws_role=None,
        debug=False,
    )

    result = resolve_sbom_source(sbom_config)

    assert isinstance(result, ContainerImage)


@mocks(
    mocks=[
        Mock(
            module=labels.core.source_dispatcher,
            target="handle_ecr_with_credentials",
            target_type="sync",
            expected=ContainerImage(img=IMAGE_METADATA, context=IMAGE_CONTEXT),
        ),
    ],
)
async def test_resolve_sbom_source_for_ecr_with_credentials() -> None:
    sbom_config = SbomConfig(
        source_type=SourceType.ECR_WITH_CREDENTIALS,
        source="python:3.10",
        exclude=(),
        execution_id=None,
        output_format=OutputFormat.FLUID_JSON,
        output="output_file",
        docker_user=None,
        docker_password=None,
        aws_external_id=None,
        aws_role=None,
        aws_credentials=AwsCredentials(
            access_key_id="fake-access-key-id",
            secret_access_key="fake-secret-access-key",  # noqa: S106
            session_token=None,
        ),
        debug=False,
    )

    result = resolve_sbom_source(sbom_config)

    assert isinstance(result, ContainerImage)


async def test_resolve_sbom_source_raises_on_invalid_type() -> None:
    mock_config = MagicMock(spec=SbomConfig)
    mock_config.source_type = "INVALID_TYPE"

    with raises(UnexpectedSBOMSourceError):
        resolve_sbom_source(mock_config)
