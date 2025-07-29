import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from cyclonedx.validation import ValidationError
from defusedxml import ElementTree as DefusedET

from labels.model.core import OutputFormat, SbomConfig, SourceType
from labels.model.sources import ImageContext, ImageMetadata
from labels.output.cyclonedx.output_handler import (
    format_cyclonedx_sbom,
    validate_sbom_json,
    validate_sbom_xml,
)
from labels.output.utils import create_packages_for_test
from labels.resolvers.container_image import ContainerImage
from labels.resolvers.directory import Directory
from labels.testing.utils.pytest_methods import raises
from labels.utils.exceptions import CycloneDXValidationError


def test_format_cyclone_json() -> None:
    test_packages, test_relationships = create_packages_for_test()

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_path = Path(temp_file.name)

        directory_config = SbomConfig(
            source="test/directory",
            source_type=SourceType.DIRECTORY,
            output_format=OutputFormat.CYCLONEDX_JSON,
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

        format_cyclonedx_sbom(
            packages=test_packages,
            relationships=test_relationships,
            config=directory_config,
            resolver=directory_resolver,
        )

        with temp_path.open() as f:
            sbom_data = json.load(f)
            assert "components" in sbom_data
            assert len(sbom_data["components"]) == 3
            assert "dependencies" in sbom_data
            assert len(sbom_data["dependencies"]) == 4
            assert "metadata" in sbom_data
            assert sbom_data["metadata"]["component"]["name"] == "test/directory"
            assert "vulnerabilities" in sbom_data
            assert len(sbom_data["vulnerabilities"]) == 1

        temp_path.unlink()


def test_format_cyclone_xml() -> None:
    test_packages, test_relationships = create_packages_for_test()
    test_metadata = ImageMetadata(
        name="test-image",
        digest="sha256:test",
        repotags=["test:latest"],
        created="2025-04-25T00:00:00Z",
        dockerversion="20.10.0",
        labels={},
        architecture="amd64",
        os="linux",
        layers=[],
        layersdata=[],
        env=[],
        image_ref="test-image:latest",
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        layers_dir = Path(temp_dir) / "layers"
        layers_dir.mkdir()

        test_context = ImageContext(
            id="test_id",
            name="test-image",
            publisher="test-publisher",
            arch="amd64",
            size="1000",
            full_extraction_dir=temp_dir,
            layers_dir=str(layers_dir),
            manifest={"layers": []},
            image_ref="test-image:latest",
        )

        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

            container_config = SbomConfig(
                source="test-image:latest",
                source_type=SourceType.DOCKER,
                output_format=OutputFormat.CYCLONEDX_XML,
                output=str(temp_path.with_suffix("")),
                exclude=(),
                docker_user=None,
                docker_password=None,
                aws_external_id=None,
                aws_role=None,
                execution_id=None,
                debug=False,
            )
            container_resolver = ContainerImage(img=test_metadata, context=test_context)

            format_cyclonedx_sbom(
                packages=test_packages,
                relationships=test_relationships,
                config=container_config,
                resolver=container_resolver,
            )

            tree = DefusedET.parse(temp_path)
            root = tree.getroot()
            ns = {"bom": "http://cyclonedx.org/schema/bom/1.6"}

            components = root.findall(".//bom:components/bom:component", ns)
            assert len(components) == 3

            dependencies = root.findall(".//bom:dependencies/bom:dependency", ns)
            assert len(dependencies) == 4

            metadata_component = root.find(".//bom:metadata/bom:component", ns)
            assert metadata_component is not None
            component_name = metadata_component.find("bom:name", ns)
            component_version = metadata_component.find("bom:version", ns)
            assert component_name is not None
            assert component_version is not None
            assert component_name.text == "test-image:latest"
            assert component_version.text == test_context.id

            temp_path.unlink()


async def test_cyclonedx_xml_validation_error() -> None:
    with patch(
        "labels.output.cyclonedx.output_handler.make_schemabased_validator",
    ) as mock_validator:
        validation_error = ValidationError("Mock XML validation error")
        mock_validator.return_value.validate_str.return_value = validation_error
        with raises(CycloneDXValidationError):
            validate_sbom_xml("<invalid>xml</invalid>", "test.xml")


async def test_cyclonedx_json_validation_error() -> None:
    validation_error = ValidationError("Mock JSON validation error")
    with patch("cyclonedx.validation.json.JsonStrictValidator") as mock_validator:
        mock_validator.return_value.validate_str.return_value = validation_error
        with raises(CycloneDXValidationError):
            validate_sbom_json('{"invalid": "json"}', "test.json")
