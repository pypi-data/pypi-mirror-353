import base64
from unittest.mock import AsyncMock, MagicMock

import aioboto3
import botocore

import labels.integrations.ecr
from labels.integrations.ecr import ecr_connection, get_credentials, get_token
from labels.model.sources import AwsCredentials, AwsRole, ImageMetadata, LayerData
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.pytest_methods import raises
from labels.utils.exceptions import AwsCredentialsNotFoundError

IMAGE_METADATA = ImageMetadata(
    name="python",
    digest="sha256:a123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    repotags=["python:3.10", "python:latest"],
    created="2023-01-01T00:00:00Z",
    dockerversion="20.10.12",
    labels={"maintainer": "Python Software Foundation", "version": "3.10"},
    architecture="amd64",
    os="linux",
    layers=["sha256:layer1hash123456789abcdef"],
    layersdata=[
        LayerData(
            digest="sha256:layer1hash123456789abcdef",
            size=10000000,
            mimetype="application/vnd.docker.image.rootfs.diff.tar.gzip",
            annotations={"org.opencontainers.image.ref.name": "python:3.10"},
        ),
    ],
    env=["PATH=/usr/local/bin", "PYTHON_VERSION=3.10"],
    image_ref="123456789012.dkr.ecr.us-east-1.amazonaws.com/my-repo:latest",
)


def make_mock_session() -> AsyncMock:
    mock_sts_client = AsyncMock()
    mock_sts_client.assume_role.return_value = {
        "Credentials": {
            "AccessKeyId": "test-access-key",
            "SecretAccessKey": "test-secret-key",
            "SessionToken": "test-session-token",
        },
    }

    mock_client_cm = MagicMock()
    mock_client_cm.__aenter__ = AsyncMock(return_value=mock_sts_client)
    mock_client_cm.__aexit__ = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.client.return_value = mock_client_cm

    return mock_session


def make_mock_session_with_exception() -> AsyncMock:
    mock_sts_client = AsyncMock()
    mock_sts_client.assume_role.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
        "AssumeRole",
    )

    mock_client_cm = MagicMock()
    mock_client_cm.__aenter__ = AsyncMock(return_value=mock_sts_client)
    mock_client_cm.__aexit__ = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.client.return_value = mock_client_cm

    return mock_session


@mocks(
    mocks=[
        Mock(
            module=labels.integrations.ecr,
            target="get_credentials",
            target_type="async",
            expected=AwsCredentials(
                access_key_id="access_key_id",
                secret_access_key="secret_access_key",  # noqa: S106
                session_token="session_token",  # noqa: S106
            ),
        ),
        Mock(
            module=labels.integrations.ecr,
            target="get_token",
            target_type="async",
            expected="dummy_token",
        ),
        Mock(
            module=labels.integrations.ecr,
            target="get_docker_image",
            target_type="sync",
            expected=IMAGE_METADATA,
        ),
    ],
)
async def test_ecr_connection() -> None:
    role = AwsRole(
        external_id="external_id",
        role="arn:aws:iam::123456789012:role/role_name",
    )
    image_uri = "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-repo:latest"

    token, image_metadata = await ecr_connection(role, image_uri)

    assert token == "dummy_token"  # noqa: S105
    assert image_metadata == IMAGE_METADATA


@mocks(
    mocks=[
        Mock(
            module=labels.integrations.ecr,
            target="get_credentials",
            target_type="async",
            expected=None,
        ),
    ],
)
async def test_ecr_connection_aws_credentials_not_found() -> None:
    role = AwsRole(
        external_id="external_id",
        role="arn:aws:iam::123456789012:role/role_name",
    )
    image_uri = "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-repo:latest"

    with raises(AwsCredentialsNotFoundError):
        await ecr_connection(role, image_uri)


@mocks(
    mocks=[
        Mock(
            module=aioboto3,
            target="Session",
            target_type="function",
            expected=make_mock_session,
        ),
    ],
)
async def test_get_credentials_success() -> None:
    test_role = AwsRole(
        external_id="test-external-id",
        role="arn:aws:iam::123456789012:role/test-role",
    )

    result = await get_credentials(test_role)

    assert isinstance(result, AwsCredentials)
    assert result.access_key_id == "test-access-key"
    assert result.secret_access_key == "test-secret-key"  # noqa: S105
    assert result.session_token == "test-session-token"  # noqa: S105


@mocks(
    mocks=[
        Mock(
            module=aioboto3,
            target="Session",
            target_type="function",
            expected=make_mock_session_with_exception,
        ),
    ],
)
async def test_get_credentials_error() -> None:
    test_role = AwsRole(
        external_id="test-external-id",
        role="arn:aws:iam::123456789012:role/test-role",
    )

    with raises(botocore.exceptions.ClientError):
        await get_credentials(test_role)


@mocks(
    mocks=[
        Mock(
            module=labels.integrations.ecr,
            target="run_boto3_fun",
            target_type="async",
            expected={
                "authorizationData": [
                    {
                        "authorizationToken": base64.b64encode(b"AWS:mysecretpassword").decode(
                            "utf-8",
                        ),
                    },
                ],
            },
        ),
    ],
)
async def test_get_token_success() -> None:
    credentials = AwsCredentials(
        access_key_id="dummy",
        secret_access_key="dummy",  # noqa: S106
        session_token="dummy",  # noqa: S106
    )
    password = await get_token(credentials)
    assert password == "mysecretpassword"  # noqa: S105
