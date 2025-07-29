from labels.model.core import OutputFormat, SourceType
from labels.testing.utils.pytest_methods import raises


def test_output_format_from_string_valid() -> None:
    assert OutputFormat.from_string("fluid-json") == OutputFormat.FLUID_JSON
    assert OutputFormat.from_string("cyclonedx-json") == OutputFormat.CYCLONEDX_JSON
    assert OutputFormat.from_string("cyclonedx-xml") == OutputFormat.CYCLONEDX_XML
    assert OutputFormat.from_string("spdx-json") == OutputFormat.SPDX_JSON
    assert OutputFormat.from_string("spdx-xml") == OutputFormat.SPDX_XML


def test_output_format_from_string_invalid() -> None:
    with raises(ValueError, match="invalid-format is not a valid OutputFormat"):
        OutputFormat.from_string("invalid-format")


def test_source_type_from_string_valid() -> None:
    assert SourceType.from_string("dir") == SourceType.DIRECTORY
    assert SourceType.from_string("docker") == SourceType.DOCKER
    assert SourceType.from_string("docker-daemon") == SourceType.DOCKER_DAEMON
    assert SourceType.from_string("ecr") == SourceType.ECR


def test_source_type_from_string_invalid() -> None:
    with raises(ValueError, match="invalid-source is not a valid SourceType"):
        SourceType.from_string("invalid-source")
