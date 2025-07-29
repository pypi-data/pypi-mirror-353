import shutil
import tarfile
import tempfile
from pathlib import Path

from labels.model.file import Location, Type
from labels.model.sources import ImageContext, ImageMetadata, LayerData
from labels.resolvers.container_image import (
    ContainerImage,
    ContainerImageContentResolver,
    ContainerImagePathResolver,
    _normalize_rel_root,
    get_type_from_tar_member,
    is_in_dependency_dir,
)
from labels.testing.utils.pytest_marks import parametrize_sync
from labels.testing.utils.pytest_methods import raises


def create_test_image_context() -> tuple[str, ImageContext, ImageMetadata]:
    temp_dir = tempfile.mkdtemp()
    layers_dir = tempfile.mkdtemp()
    layer_id = "sha256:test_layer"

    layer_contents_dir = tempfile.mkdtemp()

    (Path(layer_contents_dir) / "file1.txt").write_text("test content 1")
    (Path(layer_contents_dir) / "file2.txt").write_text("test content 2")
    (Path(layer_contents_dir) / "file3.json").write_text('{"name": "test"}')

    (Path(layer_contents_dir) / "subdir1").mkdir(parents=True)
    (Path(layer_contents_dir) / "subdir1" / "package.json").write_text(
        '{"dependencies": {"express": "^4.17.1"}}',
    )
    (Path(layer_contents_dir) / "subdir1" / "requirements.txt").write_text("flask==2.0.1")
    (Path(layer_contents_dir) / "subdir1" / "node_modules").mkdir(parents=True)

    (Path(layer_contents_dir) / "subdir2").mkdir(parents=True)
    (Path(layer_contents_dir) / "subdir2" / "Dockerfile").write_text("FROM ubuntu:20.04")
    (Path(layer_contents_dir) / "subdir2" / "Dockerfile.alpine").write_text("FROM alpine:3.13")
    (Path(layer_contents_dir) / "subdir2" / "app.rpm").write_text("RedHat package")
    (Path(layer_contents_dir) / "subdir2" / "package.apk").write_text("Alpine package")

    layer_tar_path = Path(layers_dir) / layer_id / "layer.tar"
    layer_tar_path.parent.mkdir(parents=True)
    with tarfile.open(layer_tar_path, "w") as tar:
        tar.add(
            layer_contents_dir,
            arcname="",
        )

    extract_target = Path(temp_dir) / layer_id
    extract_target.mkdir(parents=True)
    with tarfile.open(layer_tar_path, "r") as tar:
        for member in tar.getmembers():
            member_path = Path(member.name)
            if not str(member_path).startswith(("/", "../")):
                tar.extract(member, path=extract_target)

    test_layer = LayerData(
        mimetype="application/vnd.docker.image.rootfs.diff.tar",
        digest=layer_id,
        size=1000,
        annotations=None,
    )

    img_metadata = ImageMetadata(
        name="test-image:latest",
        digest="sha256:test_digest",
        repotags=["test-image:latest"],
        created="2025-01-01T00:00:00Z",
        dockerversion="20.10.0",
        labels={},
        architecture="amd64",
        os="linux",
        layers=[layer_id],
        layersdata=[test_layer],
        env=[],
        image_ref="docker://test-image:latest",
    )

    manifest = {
        "layers": [{"digest": layer_id}],
        "config": {"digest": "sha256:test_config"},
    }

    img_context = ImageContext(
        id=img_metadata.digest,
        name=img_metadata.name,
        publisher="",
        arch=img_metadata.architecture,
        size="1000",
        full_extraction_dir=temp_dir,
        layers_dir=layers_dir,
        manifest=manifest,
        image_ref=img_metadata.image_ref,
    )

    shutil.rmtree(layer_contents_dir)

    return temp_dir, img_context, img_metadata


def test_path_resolver_has_path() -> None:
    temp_dir, img_context, img_metadata = create_test_image_context()
    try:
        path_resolver = ContainerImagePathResolver(
            img=img_metadata,
            context=img_context,
        )
        assert path_resolver.has_path("file1.txt")
        assert path_resolver.has_path("subdir1/package.json")
        assert path_resolver.has_path("subdir2/package.apk")
        assert not path_resolver.has_path("nonexistent.txt")
    finally:
        shutil.rmtree(temp_dir)
        shutil.rmtree(img_context.layers_dir)


def test_path_resolver_files_by_path() -> None:
    temp_dir, img_context, img_metadata = create_test_image_context()
    try:
        path_resolver = ContainerImagePathResolver(
            img=img_metadata,
            context=img_context,
        )
        locations = path_resolver.files_by_path(
            "file1.txt",
            "subdir2/Dockerfile.alpine",
            "nonexistent.txt",
        )
        assert len(locations) == 2
        assert locations[0].access_path is not None
        assert locations[0].access_path == "/file1.txt"
        assert locations[0].coordinates is not None
        assert locations[0].coordinates.real_path.endswith("file1.txt")
    finally:
        shutil.rmtree(temp_dir)
        shutil.rmtree(img_context.layers_dir)


def test_path_resolver_walk_file() -> None:
    temp_dir, img_context, img_metadata = create_test_image_context()
    try:
        path_resolver = ContainerImagePathResolver(
            img=img_metadata,
            context=img_context,
        )
        files = [f.lstrip("/") for f in path_resolver.walk_file()]
        assert "file1.txt" in files
        assert "subdir1/package.json" in files
        assert "node_modules" not in files
        assert "subdir2/app.rpm" in files
        assert len(files) == 9
    finally:
        shutil.rmtree(temp_dir)
        shutil.rmtree(img_context.layers_dir)


def test_content_resolver_file_contents() -> None:
    temp_dir, img_context, img_metadata = create_test_image_context()
    try:
        content_resolver = ContainerImageContentResolver(
            img=img_metadata,
            context=img_context,
        )
        path_resolver = ContainerImagePathResolver(
            img=img_metadata,
            context=img_context,
        )

        locations = path_resolver.files_by_path("file1.txt")
        assert len(locations) == 1

        contents = content_resolver.file_contents_by_location(locations[0])
        assert contents is not None
        with contents as f:
            content = f.read()
            assert content == "test content 1"

        location = Location(
            coordinates=None,
            access_path="file1.txt",
            annotations={},
        )
        contents_empty = content_resolver.file_contents_by_location(location)
        assert contents_empty is None
    finally:
        shutil.rmtree(temp_dir)
        shutil.rmtree(img_context.layers_dir)


@parametrize_sync(
    args=["glob_patterns", "expected_paths"],
    cases=[
        [["*.txt"], {"file1.txt", "file2.txt"}],
        [["subdir1/*.json"], {"subdir1/package.json"}],
        [["subdir1/*.txt"], {"subdir1/requirements.txt"}],
        [["subdir2/*.rpm"], {"subdir2/app.rpm"}],
        [["subdir2/*.apk"], {"subdir2/package.apk"}],
        [["subdir2/Dockerfile"], {"subdir2/Dockerfile"}],
        [["**/*Dockerfile*"], {"subdir2/Dockerfile", "subdir2/Dockerfile.alpine"}],
        [["*.json"], {"file3.json"}],
        [["subdir2/*.txt"], set()],
        [["**/*.txt"], {"file1.txt", "file2.txt", "subdir1/requirements.txt"}],
    ],
)
def test_path_resolver_files_by_glob(*, glob_patterns: list[str], expected_paths: set[str]) -> None:
    temp_dir, img_context, img_metadata = create_test_image_context()
    try:
        path_resolver = ContainerImagePathResolver(
            img=img_metadata,
            context=img_context,
        )
        locations = path_resolver.files_by_glob(*glob_patterns)
        found_paths = {
            loc.access_path.lstrip("/") for loc in locations if loc.access_path is not None
        }
        assert found_paths == expected_paths

        for location in locations:
            assert location.coordinates is not None
            assert Path(location.coordinates.real_path).exists()

    finally:
        shutil.rmtree(temp_dir)
        shutil.rmtree(img_context.layers_dir)


@parametrize_sync(
    args=["path", "dependency_dirs", "expected"],
    cases=[
        ["/app/frontend/node_modules/package", {"/app/frontend", "/app/backend/"}, True],
        ["/app/backend/node_modules/some-dep", {"/app/frontend", "/app/backend/"}, True],
        ["/app/frontend/src/components", {"/app/frontend", "/app/backend/"}, False],
        ["/app/backend/src/main.js", {"/app/frontend", "/app/backend/"}, False],
        ["/other/path/node_modules", {"/app/frontend", "/app/backend/"}, False],
        ["/app/frontendother/node_modules", {"/app/frontend", "/app/backend/"}, False],
    ],
)
def test_is_in_dependency_dir(*, path: str, dependency_dirs: set[str], expected: bool) -> None:
    assert is_in_dependency_dir(path, dependency_dirs) == expected


@parametrize_sync(
    args=["root", "base_path", "expected"],
    cases=[
        ["/path/to/root", "/path/to", "/root"],
        ["/path/to", "/path/to", "/"],
        ["/path/to/something", "/path", "/to/something"],
        ["/app/src/components", "/app", "/src/components"],
        ["/home/user/app", "/home/user/app", "/"],
        ["/var/www/html", "/var/www", "/html"],
    ],
)
def test_normalize_rel_root(root: str, base_path: str, expected: str) -> None:
    assert _normalize_rel_root(root, base_path) == expected


@parametrize_sync(
    args=["tar_type", "expected_type"],
    cases=[
        [tarfile.SYMTYPE, Type.TYPE_SYM_LINK],
        [tarfile.LNKTYPE, Type.TYPE_HARD_LINK],
        [tarfile.REGTYPE, Type.TYPE_REGULAR],
        [tarfile.DIRTYPE, Type.TYPE_DIRECTORY],
        [tarfile.FIFOTYPE, Type.TYPE_FIFO],
        [tarfile.CHRTYPE, Type.TYPE_CHARACTER_DEVICE],
        [tarfile.BLKTYPE, Type.TYPE_BLOCK_DEVICE],
        [b"X", Type.TYPE_IRREGULAR],
    ],
)
def test_get_type_from_tar_member(tar_type: bytes, expected_type: Type) -> None:
    member = tarfile.TarInfo("test_file")
    member.type = tar_type
    assert get_type_from_tar_member(member) == expected_type


async def test_container_image_minimal_integration() -> None:
    temp_dir, img_context, img_metadata = create_test_image_context()
    try:
        container = ContainerImage(
            img=img_metadata,
            context=img_context,
        )

        assert container.has_path("file1.txt")
        assert not container.has_path("nonexistent.txt")

        locations = container.files_by_path("file1.txt", "subdir1/package.json")
        assert len(locations) == 2
        file1_location = locations[0]
        assert file1_location.access_path == "/file1.txt"

        glob_files = container.files_by_glob("**/*.txt")
        assert len(glob_files) >= 2

        contents = container.file_contents_by_location(file1_location)
        assert contents is not None
        with contents as f:
            content = f.read()
            assert content == "test content 1"

        with raises(NotImplementedError):
            container.file_metadata_by_location(file1_location)

        all_files = list(container.walk_file())
        assert "/file1.txt" in all_files
        assert "/subdir1/package.json" in all_files
        assert len(all_files) >= 2
        assert not any("node_modules" in f for f in all_files)

    finally:
        shutil.rmtree(temp_dir)
        shutil.rmtree(img_context.layers_dir)
