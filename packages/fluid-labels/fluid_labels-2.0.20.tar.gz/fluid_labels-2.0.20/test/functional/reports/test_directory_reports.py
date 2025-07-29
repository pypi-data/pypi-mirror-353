from collections.abc import Callable

import pytest
from freezegun import freeze_time

from test.utils import (
    check_json_results_match,
    cleanup_file,
    ignore_cyclonedx_dynamic_properties,
    ignore_spdx_dynamic_references,
    labels,
)


@pytest.mark.flaky(reruns=1, only_rerun="requests.exceptions.ReadTimeout")
@pytest.mark.parametrize(
    (
        "config_file_path",
        "expected_file_path",
        "result_file_path",
        "file_format",
        "excluded_fields",
        "custom_filter",
    ),
    [
        (
            "test/config/generate_fluid_json_sbom.yaml",
            "test/results/expected_outputs/fluid_json_sbom.json",
            "test/results/outputs/fluid_json_sbom.json",
            "Fluid JSON",
            [
                r"root\['packages'\]\[\d+\]\['advisories'\]",
                r"root\['packages'\]\[\d+\]\['health_metadata'\]",
                r"root\['packages'\]\[\d+\]\['found_by'\]",
                r"root\['packages'\]\[\d+\]\['licenses'\]",
            ],
            None,
        ),
        (
            "test/config/generate_spdx_json_sbom.yaml",
            "test/results/expected_outputs/spdx_json_sbom.json",
            "test/results/outputs/spdx_json_sbom.json",
            "SPDX JSON",
            [
                r"root\['documentNamespace'\]",
                r"root\['packages'\]\[\d+\]\['licenseDeclared'\]",
                r"root\['packages'\]\[\d+\]\['originator'\]",
                r"root\['packages'\]\[\d+\]\['checksums'\]",
                r"root\['packages'\]\[\d+\]\['externalRefs'\]\[\d+\]\['referenceType'\]",
            ],
            ignore_spdx_dynamic_references,
        ),
        (
            "test/config/generate_cyclonedx_json_sbom.yaml",
            "test/results/expected_outputs/cyclonedx_json_sbom.json",
            "test/results/outputs/cyclonedx_json_sbom.json",
            "CYCLONEDX JSON",
            [
                r"root\['metadata'\]\['component'\]\['bom-ref'\]",
                r"root\['serialNumber'\]",
                r"root\['dependencies'\]\[0\]\['ref'\]",
                r"root\['components'\]\[\d+\]\['properties'\]\[\d+\]\['name'\]",
                r"root\['components'\]\[\d+\]\['licenses'\]",
                r"root\['components'\]\[\d+\]\['authors'\]",
                r"root\['components'\]\[\d+\]\['hashes'\]",
                r"root\['vulnerabilities'\]",
            ],
            ignore_cyclonedx_dynamic_properties,
        ),
    ],
)
@freeze_time("2025-01-01 12:00:00")
def test_sbom_report(  # noqa: PLR0913
    *,
    config_file_path: str,
    expected_file_path: str,
    result_file_path: str,
    file_format: str,
    excluded_fields: list[str] | None,
    custom_filter: Callable | None,
) -> None:
    cleanup_file(result_file_path)

    code, stdout, stderr = labels(["config", config_file_path])

    assert code == 0
    assert "Generating SBOM from dir: test/data/dependencies" in stdout
    assert f"Valid {file_format} format, generating output file at {result_file_path}" in stdout
    assert "Output file successfully generated" in stdout
    assert not stderr

    check_json_results_match(
        expected_file_path=expected_file_path,
        result_file_path=result_file_path,
        excluded_fields=excluded_fields,
        custom_filter=custom_filter,
    )
