import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from defusedxml import ElementTree as DefusedET
from spdx_tools.spdx.model.actor import Actor, ActorType
from spdx_tools.spdx.model.document import CreationInfo, Document
from spdx_tools.spdx.validation.validation_message import ValidationContext, ValidationMessage

import labels.output.spdx.output_handler
from labels.model.core import OutputFormat, SbomConfig, SourceType
from labels.model.sources import ImageContext, ImageMetadata
from labels.output.spdx.output_handler import format_spdx_sbom, validate_spdx_sbom
from labels.output.utils import create_packages_for_test
from labels.resolvers.container_image import ContainerImage
from labels.resolvers.directory import Directory
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.pytest_methods import raises
from labels.utils.exceptions import SPDXValidationError


def test_format_spdx_sbom_json() -> None:
    test_packages, test_relationships = create_packages_for_test()

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_path = Path(temp_file.name)

        directory_config = SbomConfig(
            source="test/directory",
            source_type=SourceType.DIRECTORY,
            output_format=OutputFormat.SPDX_JSON,
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

        format_spdx_sbom(
            packages=test_packages,
            relationships=test_relationships,
            config=directory_config,
            resolver=directory_resolver,
        )

        with temp_path.open() as f:
            sbom_data = json.load(f)
            assert sbom_data["name"] == "test/directory"
            assert "packages" in sbom_data
            assert len(sbom_data["packages"]) == 3
            assert "relationships" in sbom_data
            assert len(sbom_data["relationships"]) == 4

        temp_path.unlink()


def test_format_spdx_sbom_xml() -> None:
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

    temp_dir = tempfile.mkdtemp()
    image_context = ImageContext(
        id=image_metadata.digest,
        name=image_metadata.name,
        publisher="",
        arch=image_metadata.architecture,
        size="0",
        full_extraction_dir=temp_dir,
        layers_dir=f"{temp_dir}/layers",
        manifest={},
        image_ref=image_metadata.image_ref,
    )

    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as temp_file:
        temp_path = Path(temp_file.name)

        container_config = SbomConfig(
            source="python:3.10",
            source_type=SourceType.DOCKER,
            output_format=OutputFormat.SPDX_XML,
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

        format_spdx_sbom(
            packages=test_packages,
            relationships=test_relationships,
            config=container_config,
            resolver=container_resolver,
        )

        xml_path = temp_path.with_suffix(".xml")
        assert xml_path.exists()

        tree = DefusedET.parse(xml_path)
        root = tree.getroot()

        spdx_id = root.find("SPDXID")
        assert spdx_id is not None
        assert spdx_id.text == "SPDXRef-DOCUMENT"

        doc_name = root.find("name")
        assert doc_name is not None
        assert doc_name.text == "docker.io/library/python:3.10"

        assert "packages" in [elem.tag for elem in root]
        packages = root.findall("packages")
        assert len(packages) == 3

        assert "relationships" in [elem.tag for elem in root]
        relationships = root.findall("relationships")
        assert len(relationships) == 4

        xml_path.unlink()


def test_format_spdx_sbom_empty() -> None:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_path = Path(temp_file.name)

        config = SbomConfig(
            source="test/directory",
            source_type=SourceType.DIRECTORY,
            output_format=OutputFormat.SPDX_JSON,
            output=str(temp_path.with_suffix("")),
            exclude=(),
            docker_user=None,
            docker_password=None,
            aws_external_id=None,
            aws_role=None,
            execution_id=None,
            debug=False,
        )
        resolver = Directory(root="test/directory", exclude=())

        format_spdx_sbom(
            packages=[],
            relationships=[],
            config=config,
            resolver=resolver,
        )

        json_path = temp_path.with_suffix(".json")
        assert json_path.exists()

        with json_path.open() as f:
            sbom_data = json.load(f)
            assert sbom_data["name"] == "test/directory"
            assert (
                sbom_data["comment"] == "No packages or relationships were found in the resource."
            )
            assert len(sbom_data["packages"]) == 1
            assert sbom_data["packages"][0]["name"] == "NONE"
            assert "relationships" not in sbom_data

        json_path.unlink()


@mocks(
    mocks=[
        Mock(
            module=labels.output.spdx.output_handler,
            target="validate_full_spdx_document",
            target_type="sync",
            expected=[
                ValidationMessage(
                    validation_message="Test validation error",
                    context=ValidationContext(),
                ),
            ],
        ),
    ],
)
async def test_validate_spdx_sbom() -> None:
    with raises(SPDXValidationError):
        validate_spdx_sbom(
            file_format="json",
            file_name="test",
            document=Document(
                CreationInfo(
                    spdx_version="SPDX-2.3",
                    spdx_id="SPDXRef-DOCUMENT",
                    name="test",
                    data_license="CC0-1.0",
                    document_namespace="test",
                    creators=[Actor(ActorType.TOOL, "Test", None)],
                    created=datetime.now(UTC),
                ),
            ),
        )
