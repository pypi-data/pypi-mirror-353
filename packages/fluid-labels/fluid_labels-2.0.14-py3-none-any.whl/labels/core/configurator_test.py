import confuse
import pytest

from labels.core.configurator import build_labels_config_from_args, build_labels_config_from_file
from labels.model.core import OutputFormat, SbomConfig, ScanArgs, SourceType
from labels.model.sources import AwsCredentials
from labels.testing.utils.helpers import get_test_data_path
from labels.testing.utils.pytest_marks import parametrize_sync
from labels.testing.utils.pytest_methods import raises
from labels.utils.exceptions import InvalidConfigFileError


@parametrize_sync(
    args=["source_str", "expected_type"],
    cases=[
        ["dir", SourceType.DIRECTORY],
        ["docker", SourceType.DOCKER],
        ["ecr", SourceType.ECR],
    ],
)
def test_build_labels_config_from_args_source_types(
    source_str: str,
    expected_type: SourceType,
) -> None:
    config = build_labels_config_from_args(
        "test/path",
        source=source_str,
        format="cyclonedx-json",
        output="output.json",
        docker_user=None,
        docker_password=None,
        aws_external_id=None,
        aws_role=None,
        config=False,
        debug=False,
    )
    assert config.source_type == expected_type


@parametrize_sync(
    args=["output_format", "expected_type"],
    cases=[
        ["fluid-json", OutputFormat.FLUID_JSON],
        ["cyclonedx-json", OutputFormat.CYCLONEDX_JSON],
        ["cyclonedx-xml", OutputFormat.CYCLONEDX_XML],
        ["spdx-json", OutputFormat.SPDX_JSON],
        ["spdx-xml", OutputFormat.SPDX_XML],
    ],
)
def test_build_labels_config_from_args_output_formats(
    output_format: str,
    expected_type: OutputFormat,
) -> None:
    config = build_labels_config_from_args(
        "test/path",
        source="dir",
        format=output_format,
        output="output.json",
        docker_user=None,
        docker_password=None,
        aws_external_id=None,
        aws_role=None,
        config=False,
        debug=False,
    )
    assert config.output_format == expected_type


def test_build_labels_config_invalid_source_type() -> None:
    invalid_source = "invalid"
    with raises(ValueError, match=f"{invalid_source} is not a valid SourceType"):
        build_labels_config_from_args(
            "test/path",
            source=invalid_source,
            format="cyclonedx-json",
            output="output.json",
            docker_user=None,
            docker_password=None,
            aws_external_id=None,
            aws_role=None,
            config=False,
            debug=False,
        )


def test_build_labels_config_invalid_output_format() -> None:
    invalid_output_format = "invalid"
    with raises(ValueError, match=f"{invalid_output_format} is not a valid OutputFormat"):
        build_labels_config_from_args(
            "test/path",
            source="dir",
            format=invalid_output_format,
            output="output.json",
            docker_user=None,
            docker_password=None,
            aws_external_id=None,
            aws_role=None,
            config=False,
            debug=False,
        )


@parametrize_sync(
    args=["arg", "kwargs", "expected"],
    cases=[
        [
            "test/path",
            {
                "source": "dir",
                "format": "cyclonedx-json",
                "output": "output.json",
                "docker_user": None,
                "docker_password": None,
                "aws_external_id": None,
                "aws_role": None,
                "config": False,
                "debug": False,
            },
            SbomConfig(
                source="test/path",
                source_type=SourceType.DIRECTORY,
                output_format=OutputFormat.CYCLONEDX_JSON,
                output="output.json",
            ),
        ],
        [
            "registry.example.com/image:tag",
            {
                "source": "docker",
                "format": "cyclonedx-json",
                "output": "output.json",
                "docker_user": "user",
                "docker_password": "pass",
                "aws_external_id": "ext-id",
                "aws_role": "role",
                "config": False,
                "debug": True,
            },
            SbomConfig(
                source="registry.example.com/image:tag",
                source_type=SourceType.DOCKER,
                execution_id=None,
                output_format=OutputFormat.CYCLONEDX_JSON,
                output="output.json",
                exclude=(),
                docker_user="user",
                docker_password="pass",  # noqa: S106
                aws_external_id="ext-id",
                aws_role="role",
                debug=True,
            ),
        ],
    ],
)
def test_build_labels_config_valid_scenarios(
    arg: str,
    kwargs: ScanArgs,
    expected: SbomConfig,
) -> None:
    config = build_labels_config_from_args(arg, **kwargs)
    assert config == expected


def test_build_labels_config_from_config_invalid_path() -> None:
    invalid_path = get_test_data_path("core/nonexistent.yaml")
    with raises(
        InvalidConfigFileError,
        match=f"The configuration file is not a valid file: {invalid_path}",
    ):
        build_labels_config_from_file(str(invalid_path))


def test_build_labels_config_from_config_invalid_extension() -> None:
    invalid_file = get_test_data_path("core/invalid_format_config.txt")
    with raises(InvalidConfigFileError, match="The configuration file must be a YAML format"):
        build_labels_config_from_file(str(invalid_file))


def test_build_labels_from_config_config_missing_required_fields() -> None:
    config_file = get_test_data_path("core/invalid_config.yaml")
    with raises(confuse.ConfigError, match="source_type not found"):  # type: ignore[misc]
        build_labels_config_from_file(str(config_file))


def test_build_labels_from_config_config_valid_config() -> None:
    config_file = get_test_data_path("core/valid_config.yaml")
    config = build_labels_config_from_file(str(config_file))

    assert config == SbomConfig(
        source="test/path",
        source_type=SourceType.DIRECTORY,
        execution_id="test-123",
        output_format=OutputFormat.CYCLONEDX_JSON,
        output="output.json",
        exclude=("node_modules", ".git"),
        docker_user="user",
        docker_password="pass",  # noqa: S106
        aws_external_id="ext-id",
        aws_role="aws-role",
        debug=True,
        include_package_metadata=True,
    )


def test_build_labels_ecr_credentials() -> None:
    config_file = get_test_data_path("core/ecr_credentials_analysis.yaml")
    config = build_labels_config_from_file(str(config_file))

    assert config == SbomConfig(
        source="registry.example.com/image:tag",
        source_type=SourceType.ECR_WITH_CREDENTIALS,
        execution_id="test-123",
        output_format=OutputFormat.FLUID_JSON,
        output="output.json",
        aws_credentials=AwsCredentials(
            access_key_id="fake-access-key-id",
            secret_access_key="fake-secret-access-key",  # noqa: S106
            session_token=None,
        ),
    )


def test_build_labels_from_config_config_minimal_config() -> None:
    config_file = get_test_data_path("core/minimal_config.yaml")
    config = build_labels_config_from_file(str(config_file))

    assert config == SbomConfig(
        source="test/path",
        source_type=SourceType.DIRECTORY,
        execution_id=None,
        output_format=OutputFormat.CYCLONEDX_JSON,
        output="output.json",
        exclude=(),
        docker_user=None,
        docker_password=None,
        aws_external_id=None,
        aws_role=None,
        debug=False,
    )


def test_build_labels_for_static_scan() -> None:
    config_file = get_test_data_path("core/static_scan_config.yaml")
    config = build_labels_config_from_file(str(config_file), static_scan=True)

    assert config == SbomConfig(
        source="./root_nickname",
        source_type=SourceType.DIRECTORY,
        execution_id=None,
        output_format=OutputFormat.FLUID_JSON,
        output="spots/test/results/labels_results",
        include=("glob(**/*.csproj)", "glob(**/*.cs)"),
        exclude=("glob(**/.git)",),
        debug=False,
        include_package_metadata=False,
    )


def test_build_labels_config_with_unrecognized_keys(caplog: pytest.LogCaptureFixture) -> None:
    config_file = get_test_data_path("core/unrecognized_config.yaml")

    with caplog.at_level("WARNING"):
        build_labels_config_from_file(str(config_file))

    assert "Some keys were not recognized" in caplog.text
