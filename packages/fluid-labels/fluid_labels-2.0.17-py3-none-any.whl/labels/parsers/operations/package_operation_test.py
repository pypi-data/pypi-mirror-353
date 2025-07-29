import shutil
import tempfile
import threading
from pathlib import Path
from unittest.mock import Mock

import pytest
import reactivex
from reactivex.scheduler import ThreadPoolScheduler

from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship, RelationshipType
from labels.parsers.cataloger.generic.cataloger import Request, Task
from labels.parsers.cataloger.python.model import PythonPackage
from labels.parsers.operations.package_operation import (
    gen_location_tasks,
    handle_relationships,
    log_and_continue,
    package_operations_factory,
    process_file_item,
    strip_version_specifier,
)
from labels.resolvers.directory import Directory
from labels.testing.utils.pytest_marks import parametrize_sync


@parametrize_sync(
    args=["input_str", "expected"],
    cases=[
        ["simple-pkg", "simple-pkg"],
        ["pkg>=1.0.0", "pkg"],
        ["pkg<=2.0.0", "pkg"],
        ["pkg>1.0.0", "pkg"],
        ["pkg<2.0.0", "pkg"],
        ["pkg==1.0.0", "pkg"],
        ["pkg [extras]", "pkg"],
        ["pkg (>=1.0.0)", "pkg"],
        ["  pkg  ", "pkg"],
        ["", ""],
        ["pkg[test]>=1.0.0", "pkg"],
    ],
)
def test_strip_version_specifier(input_str: str, expected: str) -> None:
    assert strip_version_specifier(input_str) == expected


def test_handle_relationships() -> None:
    test_packages = [
        Package(
            name="test-package",
            version="1.0.0",
            locations=[],
            licenses=[],
            language=Language.PYTHON,
            type=PackageType.PythonPkg,
            p_url="pkg:pypi/test-package@1.0.0",
            metadata=PythonPackage(
                name="test-package",
                version="1.0.0",
                dependencies=["dep-package>=2.0.0"],
            ),
            found_by="python-installed-package-cataloger",
        ),
        Package(
            name="dep-package",
            version="2.0.0",
            locations=[],
            licenses=[],
            language=Language.PYTHON,
            type=PackageType.PythonPkg,
            p_url="pkg:pypi/dep-package@2.0.0",
            metadata=PythonPackage(
                name="dep-package",
                version="2.0.0",
                dependencies=[],
            ),
            found_by="python-installed-package-cataloger",
        ),
    ]

    relationships = handle_relationships(test_packages)
    assert len(relationships) == 1
    assert relationships[0].from_.name == "dep-package"
    assert relationships[0].to_.name == "test-package"
    assert relationships[0].type == RelationshipType.DEPENDENCY_OF_RELATIONSHIP


def test_handle_relationships_missing_dep_in_packages() -> None:
    packages = [
        Package(
            name="test-package",
            version="1.0.0",
            locations=[],
            licenses=[],
            language=Language.PYTHON,
            type=PackageType.PythonPkg,
            p_url="pkg:pypi/test-package@1.0.0",
            metadata=PythonPackage(
                name="test-package",
                version="1.0.0",
                dependencies=["dep-package>=2.0.0"],
            ),
            found_by="python-installed-package-cataloger",
        ),
    ]
    relationships = handle_relationships(packages)
    assert len(relationships) == 0


def test_handle_relationships_not_python() -> None:
    packages = [
        Package(
            name="test-package",
            version="1.0.0",
            locations=[],
            licenses=[],
            language=Language.PYTHON,
            type=PackageType.PythonPkg,
            p_url="pkg:pypi/test-package@1.0.0",
            metadata=PythonPackage(
                name="test-package",
                version="1.0.0",
                dependencies=["dep-package>=2.0.0"],
            ),
            found_by="parser-name",
        ),
    ]
    relationships = handle_relationships(packages)
    assert len(relationships) == 0


def test_handle_relationships_empty() -> None:
    relationships = handle_relationships([])
    assert len(relationships) == 0


def test_handle_relationships_complex() -> None:
    test_packages = [
        Package(
            name="root-package",
            version="1.0.0",
            locations=[],
            licenses=[],
            language=Language.PYTHON,
            type=PackageType.PythonPkg,
            p_url="pkg:pypi/root-package@1.0.0",
            metadata=PythonPackage(
                name="root-package",
                version="1.0.0",
                dependencies=["dep-a>=1.0.0", "dep-b>=1.0.0"],
            ),
            found_by="python-installed-package-cataloger",
        ),
        Package(
            name="dep-a",
            version="1.0.0",
            locations=[],
            licenses=[],
            language=Language.PYTHON,
            type=PackageType.PythonPkg,
            p_url="pkg:pypi/dep-a@1.0.0",
            metadata=PythonPackage(
                name="dep-a",
                version="1.0.0",
                dependencies=["dep-c>=1.0.0"],
            ),
            found_by="python-installed-package-cataloger",
        ),
        Package(
            name="dep-b",
            version="1.0.0",
            locations=[],
            licenses=[],
            language=Language.PYTHON,
            type=PackageType.PythonPkg,
            p_url="pkg:pypi/dep-b@1.0.0",
            metadata=PythonPackage(
                name="dep-b",
                version="1.0.0",
                dependencies=[],
            ),
            found_by="python-installed-package-cataloger",
        ),
        Package(
            name="dep-c",
            version="1.0.0",
            locations=[],
            licenses=[],
            language=Language.PYTHON,
            type=PackageType.PythonPkg,
            p_url="pkg:pypi/dep-c@1.0.0",
            metadata=PythonPackage(
                name="dep-c",
                version="1.0.0",
                dependencies=[],
            ),
            found_by="python-installed-package-cataloger",
        ),
    ]

    relationships = handle_relationships(test_packages)
    assert len(relationships) == 3
    relationship_pairs = {(r.from_.name, r.to_.name) for r in relationships}
    expected_pairs = {
        ("dep-a", "root-package"),
        ("dep-b", "root-package"),
        ("dep-c", "dep-a"),
    }
    assert relationship_pairs == expected_pairs


def test_gen_location_tasks() -> None:
    test_directory = tempfile.mkdtemp()
    try:
        test_file = Path(test_directory) / "test.txt"
        test_file.write_text("test content")

        resolver = Directory(root=test_directory, exclude=())

        test_request = Request(
            real_path="test.txt",
            parser=Mock(),
            parser_name="test-parser",
        )

        source = reactivex.just(test_request)
        result = []
        errors = []

        gen_location_tasks(resolver)(source).subscribe(
            on_next=lambda x: result.append(x),
            on_error=lambda e: errors.append(e),
        )

        assert len(result) == 1
        assert len(errors) == 0

        assert isinstance(result[0], Task)
        assert result[0].parser == test_request.parser
        assert result[0].parser_name == test_request.parser_name
        assert result[0].location.access_path == "test.txt"

    finally:
        shutil.rmtree(test_directory)


def test_gen_location_tasks_error() -> None:
    resolver = Mock()
    resolver.files_by_path.side_effect = Exception("Test error")

    test_request = Request(
        real_path="/test/path",
        parser=Mock(),
        parser_name="test-parser",
    )

    source = reactivex.just(test_request)
    result = []
    errors = []

    gen_location_tasks(resolver)(source).subscribe(
        on_next=lambda x: result.append(x),
        on_error=lambda e: errors.append(e),
    )

    assert len(result) == 0
    assert len(errors) == 1
    assert str(errors[0]) == "Test error"

    resolver.files_by_path.assert_called_once_with(test_request.real_path)


def test_log_and_continue(caplog: pytest.LogCaptureFixture) -> None:
    test_exception = Exception("Test error message")
    test_file = "test_file.txt"

    result: list[None] = []
    log_and_continue(test_exception, test_file).subscribe(
        on_next=lambda x: result.append(x),
    )

    assert len(result) == 0
    expected_error = (
        f"Error found while resolving packages of {test_file}: "
        f"{test_exception}: {type(None).__name__}: None"
    )
    assert expected_error in caplog.text


def test_process_file_item() -> None:
    test_directory = tempfile.mkdtemp()
    try:
        test_file = Path(test_directory) / "requirements.txt"
        test_file.write_text("test-package==1.0.0")

        resolver = Directory(root=test_directory, exclude=())
        pool_scheduler = ThreadPoolScheduler(1)

        result: list[tuple[list[Package], list[Relationship]]] = []
        errors: list[Exception] = []
        completed = threading.Event()

        process_file_item("requirements.txt", resolver, pool_scheduler).subscribe(
            on_next=lambda x: result.append(x),
            on_error=lambda e: errors.append(e),
            on_completed=lambda: completed.set(),
        )

        completed.wait(timeout=5)
        assert len(result) == 1
        assert len(errors) == 0
        packages, relationships = result[0]
        assert len(packages) == 1
        assert len(relationships) == 0

    finally:
        shutil.rmtree(test_directory)


def test_process_file_item_error() -> None:
    test_directory = tempfile.mkdtemp()
    try:
        resolver = Directory(root=test_directory, exclude=())
        pool_scheduler = ThreadPoolScheduler(1)

        result: list[tuple[list[Package], list[Relationship]]] = []
        errors: list[Exception] = []
        completed = threading.Event()

        process_file_item("nonexistent.txt", resolver, pool_scheduler).subscribe(
            on_next=lambda x: result.append(x),
            on_error=lambda e: errors.append(e),
            on_completed=lambda: completed.set(),
        )

        completed.wait(timeout=5)
        assert len(result) == 0
        assert len(errors) == 0

    finally:
        shutil.rmtree(test_directory)


def test_package_operations_factory() -> None:
    test_directory = tempfile.mkdtemp()
    try:
        requirements_files = [
            ("pkg1/requirements.txt", "package-1==1.0.0\npackage-3>=2.0.0"),
            ("pkg2/requirements.txt", "package-2==2.0.0"),
        ]

        for file_path, content in requirements_files:
            full_path = Path(test_directory) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

        resolver = Directory(root=test_directory, exclude=())
        packages, relationships = package_operations_factory(resolver)

        assert len(packages) == 3
        assert len(relationships) == 0

    finally:
        shutil.rmtree(test_directory)


def test_package_operations_factory_error() -> None:
    test_directory = tempfile.mkdtemp()
    try:
        test_file = Path(test_directory) / "requirements.txt"
        test_file.write_text("invalid==package==1.0.0")

        resolver = Directory(root=test_directory, exclude=())
        packages, relationships = package_operations_factory(resolver)

        assert len(packages) == 0
        assert len(relationships) == 0

    finally:
        shutil.rmtree(test_directory)


@parametrize_sync(
    args=["test_error"],
    cases=[
        [Exception("Test error")],
        [ValueError("Test value error")],
        [RuntimeError("Test runtime error")],
    ],
)
def test_error_handling_in_package_operations_factory(test_error: Exception) -> None:
    mock_resolver = Mock()
    mock_resolver.walk_file.return_value = ["test_file"]

    def mock_files_by_path(*_: str) -> None:
        raise test_error

    mock_resolver.files_by_path = mock_files_by_path

    packages, relationships = package_operations_factory(mock_resolver)

    assert len(packages) == 0
    assert len(relationships) == 0
