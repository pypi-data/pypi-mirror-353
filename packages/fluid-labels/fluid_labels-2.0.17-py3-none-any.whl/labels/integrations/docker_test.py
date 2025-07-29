import shutil
import subprocess
import tempfile
from subprocess import CompletedProcess
from unittest.mock import MagicMock

import labels.integrations.docker
from labels.integrations.docker import (
    _build_copy_auth_args,
    _build_inspect_auth_args,
    _format_image_ref,
    _get_skopeo_path,
    copy_image,
    extract_docker_image,
    get_docker_image,
    get_image_context,
)
from labels.model.sources import ImageContext, ImageMetadata, LayerData
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.pytest_marks import parametrize_sync
from labels.testing.utils.pytest_methods import raises
from labels.utils.exceptions import (
    DockerImageNotFoundError,
    InvalidImageReferenceError,
    SkopeoNotFoundError,
)

IMAGE_MANIFEST = {
    "schemaVersion": 2,
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "config": {
        "mediaType": "application/vnd.oci.image.config.v1+json",
        "digest": "sha256:8d591b0b7dea080ea3be9e12ae563eebf9869168ffced1cb25",
        "size": 597,
    },
    "layers": [
        {
            "mediaType": "application/vnd.oci.image.layer.v1.tar",
            "digest": "sha256:a16e98724c05975ee8c40d8fe389c3481373d34ab20a1c",
            "size": 8461312,
        },
    ],
    "annotations": {
        "com.docker.official-images.bashbrew.arch": "arm64v8",
        "org.opencontainers.image.base.name": "scratch",
        "org.opencontainers.image.created": "2025-02-14T03:28:36Z",
    },
    "config_full": {
        "architecture": "arm64",
        "config": {
            "Env": [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            ],
            "Cmd": ["/bin/sh"],
            "WorkingDir": "/",
        },
        "created": "2025-02-14T03:28:36Z",
        "history": [
            {
                "created": "2025-02-14T03:28:36Z",
                "created_by": 'CMD ["/bin/sh"]',
                "comment": "buildkit.dockerfile.v0",
                "empty_layer": True,
            },
        ],
        "os": "linux",
        "rootfs": {
            "type": "layers",
            "diff_ids": [
                "sha256:a16e98724c05975ee8c40d8fe389c3481373d34ab20a1c",
            ],
        },
        "variant": "v8",
    },
}

IMAGE_METADATA = ImageMetadata(
    name="docker.io/library/alpine",
    digest="sha256:a8560b36e8b8210634f77d9f7f9efd7ffa463e380b75e2e74aff4511df3ef88c",
    repotags=["2.6", "2.7"],
    created="2025-02-14T03:28:36Z",
    dockerversion="",
    labels=None,
    architecture="arm64",
    os="linux",
    layers=[
        "sha256:6e771e15690e2fabf2332d3a3b744495411d6e0b00b2aea64419b58b0066cf81",
    ],
    layersdata=[
        LayerData(
            mimetype="application/vnd.oci.image.layer.v1.tar+gzip",
            digest="sha256:6e771e15690e2fabf2332d3a3b744495411d6e0b00b2aea64419b58b0066cf81",
            size=3993029,
            annotations=None,
        ),
    ],
    env=["PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"],
    image_ref="alpine",
)


@mocks(
    mocks=[
        Mock(
            module=subprocess,
            target="run",
            target_type="sync",
            expected=CompletedProcess(
                args=[
                    "bin/skopeo",
                    "inspect",
                    "--tls-verify=false",
                    "--override-os",
                    "linux",
                    "docker://alpine",
                ],
                returncode=0,
                stdout=b"""{
    "Name": "docker.io/library/alpine",
    "Digest": "sha256:a8560b36e8b8210634f77d9f7f9efd7ffa463e380b75e2e74aff4511df3ef88c",
    "RepoTags": [
        "2.6",
        "2.7"
    ],
    "Created": "2025-02-14T03:28:36Z",
    "DockerVersion": "",
    "Labels": null,
    "Architecture": "arm64",
    "Os": "linux",
    "Layers": [
        "sha256:6e771e15690e2fabf2332d3a3b744495411d6e0b00b2aea64419b58b0066cf81"
    ],
    "LayersData": [
        {
            "MIMEType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "Digest": "sha256:6e771e15690e2fabf2332d3a3b744495411d6e0b00b2aea64419b58b0066cf81",
            "Size": 3993029,
            "Annotations": null
        }
    ],
    "Env": [
        "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    ]
}""",
            ),
        ),
    ],
)
async def test_get_docker_image() -> None:
    image_ref = "alpine"
    username = "username"
    password = "password"  # noqa: S105
    daemon = False

    result = get_docker_image(
        image_ref=image_ref,
        username=username,
        password=password,
        daemon=daemon,
    )

    assert result == IMAGE_METADATA


@mocks(
    mocks=[
        Mock(
            module=shutil,
            target="which",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_get_docker_image_skopeo_not_found() -> None:
    with raises(SkopeoNotFoundError):
        _get_skopeo_path()


@parametrize_sync(
    args=["image_ref", "daemon", "expected"],
    cases=[
        ["alpine", False, "docker://alpine"],
        ["alpine", True, "docker-daemon:alpine"],
        ["alpine:latest", False, "docker://alpine:latest"],
        ["alpine:3.14", True, "docker-daemon:alpine:3.14"],
        ["docker.io/alpine", False, "docker://docker.io/alpine"],
        ["registry.example.com:5000/alpine", False, "docker://registry.example.com:5000/alpine"],
        ["docker.io/library/alpine", False, "docker://docker.io/library/alpine"],
        ["docker.io/org/team/alpine", False, "docker://docker.io/org/team/alpine"],
        [
            "alpine@sha256:1234567890123456789012345678901234567890123456789012345678901234",
            False,
            "docker://alpine@sha256:1234567890123456789012345678901234567890123456789012345678901234",
        ],
        ["example.com/my-app.api:1.0.3", False, "docker://example.com/my-app.api:1.0.3"],
        ["docker://alpine", False, "docker://alpine"],
        ["docker-daemon:alpine", False, "docker-daemon:alpine"],
        ["docker://alpine", True, "docker://alpine"],
        ["docker-daemon:alpine", True, "docker-daemon:alpine"],
    ],
)
def test_format_image_ref(image_ref: str, daemon: bool, expected: str) -> None:  # noqa: FBT001
    assert _format_image_ref(image_ref, daemon=daemon) == expected


def test_format_image_ref_invalid() -> None:
    invalid_refs = [
        "alpine image",
        "alpine:tag:another",
        "alpine@sha256:invalid",
        "alpine@md5:1234",
    ]

    for ref in invalid_refs:
        with raises(InvalidImageReferenceError):
            _format_image_ref(ref)


@mocks(
    mocks=[
        Mock(
            module=shutil,
            target="which",
            target_type="sync",
            expected="/usr/bin/skopeo",
        ),
        Mock(
            module=labels.integrations.docker,
            target="_format_image_ref",
            target_type="sync",
            expected=None,
        ),
        Mock(
            module=labels.integrations.docker,
            target="_execute_command",
            target_type="sync",
            expected=False,
        ),
    ],
)
async def test_copy_image_invalid_image_ref() -> None:
    result = copy_image(image_ref="invalid!reference", dest_path="./")
    assert result is False


@parametrize_sync(
    args=["username", "password", "token", "aws_creds", "expected"],
    cases=[
        [
            "user1",
            "pass123",
            None,
            None,
            ["./", "image_ref", "--username", "user1", "--password", "pass123"],
        ],
        [None, None, "token123", None, ["./", "image_ref", "--registry-token=token123"]],
        [None, None, None, "aws:creds", ["./", "image_ref", "--creds=aws:creds"]],
        [None, None, None, None, ["./", "image_ref"]],
        [
            "user1",
            "pass123",
            "token123",
            "aws:creds",
            ["./", "image_ref", "--username", "user1", "--password", "pass123"],
        ],
        [
            None,
            None,
            "token123",
            "aws:creds",
            ["./", "image_ref", "--registry-token=token123"],
        ],
        ["user1", None, None, None, ["./", "image_ref"]],
        [None, "pass123", None, None, ["./", "image_ref"]],
    ],
)
def test_build_inspect_auth_args(
    username: str | None,
    password: str | None,
    token: str | None,
    aws_creds: str | None,
    expected: list[str],
) -> None:
    command_args = ["./", "image_ref"]

    result = _build_inspect_auth_args(
        unauthenticated_args=command_args,
        username=username,
        password=password,
        token=token,
        aws_creds=aws_creds,
    )

    assert result == expected


@parametrize_sync(
    args=["username", "password", "token", "aws_creds", "expected"],
    cases=[
        [
            "user1",
            "pass123",
            None,
            None,
            ["./", "image_ref", "--src-username", "user1", "--src-password", "pass123"],
        ],
        [None, None, "token123", None, ["./", "image_ref", "--src-registry-token", "token123"]],
        [None, None, None, "aws:creds", ["./", "image_ref", "--src-creds=aws:creds"]],
        [None, None, None, None, ["./", "image_ref"]],
        [
            "user1",
            "pass123",
            "token123",
            "aws:creds",
            ["./", "image_ref", "--src-username", "user1", "--src-password", "pass123"],
        ],
        [
            None,
            None,
            "token123",
            "aws:creds",
            ["./", "image_ref", "--src-registry-token", "token123"],
        ],
        ["user1", None, None, None, ["./", "image_ref"]],
        [None, "pass123", None, None, ["./", "image_ref"]],
    ],
)
def test_build_copy_auth_args(
    username: str | None,
    password: str | None,
    token: str | None,
    aws_creds: str | None,
    expected: list[str],
) -> None:
    command_args = ["./", "image_ref"]

    result = _build_copy_auth_args(
        unauthenticated_args=command_args,
        username=username,
        password=password,
        token=token,
        aws_creds=aws_creds,
    )

    assert result == expected


@mocks(
    mocks=[
        Mock(
            module=tempfile,
            target="mkdtemp",
            target_type="sync",
            expected="/tmp/mock-temp-dir",  # noqa: S108
        ),
        Mock(
            module=labels.integrations.docker,
            target="extract_docker_image",
            target_type="sync",
            expected=("/tmp/mock-temp-dir", IMAGE_MANIFEST),  # noqa: S108
        ),
    ],
)
async def test_get_image_context() -> None:
    mock_layers = [
        LayerData(
            mimetype="application/vnd.docker.image.rootfs.diff.tar.gzip",
            digest="sha256:1234567890abcdef",
            size=1000,
            annotations=None,
        ),
        LayerData(
            mimetype="application/vnd.docker.image.rootfs.diff.tar.gzip",
            digest="sha256:abcdef1234567890",
            size=2000,
            annotations=None,
        ),
    ]

    mock_image = ImageMetadata(
        name="test/image:latest",
        digest="sha256:8d591b0b7dea080ea3be9e12ae563eebf9869168ffced1cb25",
        repotags=["test/image:latest"],
        created="2023-01-01T00:00:00Z",
        dockerversion="20.10.0",
        labels={},
        architecture="arm64",
        os="linux",
        layers=["sha256:a16e98724c05975ee8c40d8fe389c3481373d34ab20a1c"],
        layersdata=mock_layers,
        env=["PATH=/usr/local/bin"],
        image_ref="docker://test/image:latest",
    )

    result = get_image_context(
        image=mock_image,
        username="test_user",
        password="test_pass",  # noqa: S106
    )

    assert isinstance(result, ImageContext)
    assert result.id == mock_image.digest
    assert result.name == mock_image.name
    assert result.publisher == ""
    assert result.arch == mock_image.architecture
    assert result.size == "3000"
    assert result.full_extraction_dir == "/tmp/mock-temp-dir"  # noqa: S108
    assert result.layers_dir == "/tmp/mock-temp-dir"  # noqa: S108
    assert result.manifest == IMAGE_MANIFEST
    assert result.image_ref == mock_image.image_ref


@mocks(
    mocks=[
        Mock(
            module=tempfile,
            target="mkdtemp",
            target_type="sync",
            expected="/fake/tempdir",
        ),
        Mock(
            module=labels.integrations.docker,
            target="_format_image_ref",
            target_type="sync",
            expected="formatted/image:tag",
        ),
        Mock(
            module=labels.integrations.docker,
            target="copy_image",
            target_type="sync",
            expected=None,
        ),
        Mock(
            module=labels.integrations.docker,
            target="_load_manifest",
            target_type="sync",
            expected=IMAGE_MANIFEST,
        ),
        Mock(
            module=labels.integrations.docker,
            target="_load_config",
            target_type="sync",
            expected={"config_key": "config_value"},
        ),
        Mock(
            module=labels.integrations.docker,
            target="_extract_layer",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_extract_docker_image() -> None:
    image = IMAGE_METADATA
    output_dir = "/fake/output"

    layers_dir, manifest = extract_docker_image(image, output_dir)

    assert layers_dir == "/fake/tempdir"
    assert manifest["config_full"] == {"config_key": "config_value"}


@mocks(
    mocks=[
        Mock(
            module=shutil,
            target="which",
            target_type="sync",
            expected="/usr/bin/skopeo",
        ),
        Mock(
            module=subprocess,
            target="run",
            target_type="function",
            expected=MagicMock(
                side_effect=subprocess.CalledProcessError(
                    returncode=1,
                    cmd=[
                        "skopeo",
                        "inspect",
                        "--tls-verify=false",
                        "--override-os",
                        "linux",
                        "docker://nonexistent-image",
                    ],
                    stderr="Error: docker.io/nonexistent-image: manifest unknown: manifest unknown",
                ),
            ),
        ),
    ],
)
async def test_get_docker_image_not_found() -> None:
    image_ref = "nonexistent-image"

    with raises(DockerImageNotFoundError):
        get_docker_image(image_ref=image_ref)
