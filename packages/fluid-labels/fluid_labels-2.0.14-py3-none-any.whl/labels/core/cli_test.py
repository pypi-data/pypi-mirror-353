from unittest.mock import patch

from click.testing import CliRunner

from labels.core.cli import cli
from labels.testing.utils.helpers import get_test_data_path
from labels.testing.utils.pytest_marks import parametrize_sync


def test_run_labels_from_config() -> None:
    runner = CliRunner()
    test_data_path = get_test_data_path("core/minimal_config.yaml")
    with (
        patch("labels.core.cli.build_labels_config_from_file") as mock_build_config_from_file,
        patch("labels.core.cli.execute_labels_scan") as mock_execute,
    ):
        mock_build_config_from_file.return_value = None
        mock_execute.return_value = None

        result = runner.invoke(cli, ["config", test_data_path])

        assert result.exit_code == 0
        assert result.exception is None
        assert "Fluid Attacks" in result.output
        assert " We hack your software." in result.output

        mock_build_config_from_file.assert_called_once_with(test_data_path)


@parametrize_sync(
    args=["target", "cli_args", "expected_args"],
    cases=[
        [
            "./",
            [
                "scan",
                "./",
                "--source",
                "dir",
                "--output",
                "output.json",
                "--format",
                "spdx-json",
            ],
            {
                "source": "dir",
                "output": "output.json",
                "format": "spdx-json",
                "docker_user": None,
                "docker_password": None,
                "aws_external_id": None,
                "aws_role": None,
                "debug": False,
            },
        ],
        [
            "registry.example.com/my-image:latest",
            [
                "scan",
                "registry.example.com/my-image:latest",
                "--source",
                "docker",
                "--output",
                "output.json",
                "--format",
                "spdx-json",
                "--docker-user",
                "username",
                "--docker-password",
                "password",
            ],
            {
                "source": "docker",
                "output": "output.json",
                "format": "spdx-json",
                "docker_user": "username",
                "docker_password": "password",
                "aws_external_id": None,
                "aws_role": None,
                "debug": False,
            },
        ],
    ],
)
def test_run_labels_from_args(
    target: str,
    cli_args: list[str],
    expected_args: dict[str, str | None | bool],
) -> None:
    runner = CliRunner()

    with (
        patch("labels.core.cli.build_labels_config_from_args") as mock_build_config_from_args,
        patch("labels.core.cli.execute_labels_scan") as mock_execute,
    ):
        mock_build_config_from_args.return_value = None
        mock_execute.return_value = None

        result = runner.invoke(cli, cli_args)

        assert result.exit_code == 0
        assert result.exception is None
        assert "Fluid Attacks" in result.output
        assert " We hack your software." in result.output

        mock_build_config_from_args.assert_called_once_with(target, **expected_args)


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Fluid labels CLI" in result.output
    assert "config" in result.output
    assert "scan" in result.output


def test_run_labels_invalid_format() -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "scan",
            "./",
            "--source",
            "dir",
            "--format",
            "invalid-format",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid value for '--format'" in result.output
