import os
import tempfile
from collections.abc import Callable
from pathlib import Path

import pytest

from test.utils import check_json_results_match, cleanup_file, labels


@pytest.mark.flaky(reruns=1, only_rerun="requests.exceptions.ReadTimeout")
@pytest.mark.parametrize(
    (
        "template_file_path",
        "expected_file_path",
        "result_file_path",
        "file_format",
        "excluded_fields",
        "custom_filter",
    ),
    [
        (
            "test/config/generate_ecr_sbom.yaml.template",
            "test/results/expected_outputs/fluid_json_ecr_sbom.json",
            "test/results/outputs/fluid_json_ecr_sbom.json",
            "Fluid JSON",
            [
                r"root\['packages'\]\[\d+\]\['advisories'\]",
                r"root\['packages'\]\[\d+\]\['health_metadata'\]",
                r"root\['packages'\]\[\d+\]\['found_by'\]",
                r"root\['packages'\]\[\d+\]\['licenses'\]",
                r"root\['sbom_details'\]\['timestamp'\]",
            ],
            None,
        ),
    ],
)
def test_sbom_report(  # noqa: PLR0913
    *,
    template_file_path: str,
    expected_file_path: str,
    result_file_path: str,
    file_format: str,
    excluded_fields: list[str] | None,
    custom_filter: Callable | None,
) -> None:
    cleanup_file(result_file_path)
    template_path = Path(template_file_path)

    with (
        tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as temp_config,
        template_path.open() as f,
    ):
        config_content = f.read()

        config_content = config_content.replace("${AWS_TEST_ROLE}", os.environ["AWS_TEST_ROLE"])
        config_content = config_content.replace("${AWS_EXTERNAL_ID}", os.environ["AWS_EXTERNAL_ID"])

        temp_config.write(config_content)
        temp_config.flush()

        try:
            code, stdout, stderr = labels(["config", temp_config.name])

            assert code == 0
            ecr_message = (
                "Generating SBOM from ecr: "
                "205810638802.dkr.ecr.us-east-1.amazonaws.com/labels/test:alpine-sha256-de0eb0b3f2a4"
            )
            assert ecr_message in stdout
            assert (
                f"Valid {file_format} format, generating output file at {result_file_path}"
                in stdout
            )
            assert "Output file successfully generated" in stdout
            assert not stderr

            check_json_results_match(
                expected_file_path=expected_file_path,
                result_file_path=result_file_path,
                excluded_fields=excluded_fields,
                custom_filter=custom_filter,
            )
        finally:
            Path(temp_config.name).unlink()
