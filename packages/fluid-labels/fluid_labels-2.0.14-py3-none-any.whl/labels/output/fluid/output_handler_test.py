import json
import tempfile
from pathlib import Path

from labels.model.core import OutputFormat, SbomConfig, SourceType
from labels.model.sources import ImageContext, ImageMetadata
from labels.output.fluid.output_handler import (
    format_fluid_sbom,
    validate_fluid_json,
    write_json_to_file,
)
from labels.output.utils import create_packages_for_test
from labels.resolvers.container_image import ContainerImage
from labels.resolvers.directory import Directory
from labels.testing.utils.pytest_methods import raises
from labels.utils.exceptions import FluidJSONValidationError


def test_write_json_to_file() -> None:
    test_content = {"key": "value"}
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        write_json_to_file(temp_path, test_content)

        with Path(temp_path).open() as f:
            written_content = json.load(f)
            assert written_content == test_content

        temp_path.unlink()


def test_validate_fluid_json_success() -> None:
    result = {
        "sbom_details": {
            "name": "test-namespace",
            "version": "1.0",
            "timestamp": "2025-04-23T00:00:00Z",
            "tool": "Fluid-Labels",
            "organization": "Fluid attacks",
        },
        "packages": [],
        "relationships": [],
    }
    test_path = Path("test.json")
    validate_fluid_json(result, test_path)


def test_validate_fluid_json_error() -> None:
    test_path = Path("test.json")
    result = {"invalid": "schema"}

    with raises(FluidJSONValidationError):
        validate_fluid_json(result, test_path)


def test_format_fluid_sbom_directory() -> None:
    test_packages, test_relationships = create_packages_for_test()

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_path = Path(temp_file.name)

        directory_config = SbomConfig(
            source="test/directory",
            source_type=SourceType.DIRECTORY,
            output_format=OutputFormat.FLUID_JSON,
            output=str(temp_path.with_suffix("")),
            exclude=(),
            docker_user=None,
            docker_password=None,
            aws_external_id=None,
            aws_role=None,
            execution_id=None,
            debug=False,
        )
        directory_resolver = Directory(root="test/directory", exclude=())

        format_fluid_sbom(
            packages=test_packages,
            relationships=test_relationships,
            config=directory_config,
            resolver=directory_resolver,
        )

        with temp_path.open() as f:
            sbom_data = json.load(f)
            assert "sbom_details" in sbom_data
            assert sbom_data["sbom_details"]["name"] == "test/directory"
            assert "packages" in sbom_data
            assert len(sbom_data["packages"]) == 3
            assert "relationships" in sbom_data
            assert len(sbom_data["relationships"]) == 1

        temp_path.unlink()


def test_format_fluid_sbom_container() -> None:
    test_packages, test_relationships = create_packages_for_test()

    image_metadata = ImageMetadata(
        name="python",
        digest="sha256:a123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        repotags=["python:3.10", "python:latest"],
        created="2023-01-01T00:00:00Z",
        dockerversion="20.10.12",
        architecture="amd64",
        os="linux",
        layers=[],
        layersdata=[],
        image_ref="docker.io/library/python:3.10",
        labels={},
        env=[],
    )

    image_context = ImageContext(
        id=image_metadata.digest,
        name=image_metadata.name,
        publisher="",
        arch=image_metadata.architecture,
        size="0",
        full_extraction_dir="temp_dir",
        layers_dir="temp_dir/layers",
        manifest={},
        image_ref=image_metadata.image_ref,
    )

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_path = Path(temp_file.name)

        container_config = SbomConfig(
            source="python:3.10",
            source_type=SourceType.DOCKER,
            output_format=OutputFormat.FLUID_JSON,
            output=str(temp_path.with_suffix("")),
            exclude=(),
            docker_user=None,
            docker_password=None,
            aws_external_id=None,
            aws_role=None,
            execution_id=None,
            debug=False,
        )

        container_resolver = ContainerImage(img=image_metadata, context=image_context)

        format_fluid_sbom(
            packages=test_packages,
            relationships=test_relationships,
            config=container_config,
            resolver=container_resolver,
        )

        with temp_path.open() as f:
            sbom_data = json.load(f)
            assert "sbom_details" in sbom_data
            assert sbom_data["sbom_details"]["name"] == "docker.io/library/python:3.10"
            assert sbom_data["sbom_details"]["version"] == image_metadata.digest
            assert "packages" in sbom_data
            assert len(sbom_data["packages"]) == 3
            assert "relationships" in sbom_data
            assert len(sbom_data["relationships"]) == 1

        temp_path.unlink()
