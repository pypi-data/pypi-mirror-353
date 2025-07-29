from collections.abc import Callable
from typing import TextIO
from unittest.mock import MagicMock, Mock

from reactivex import from_iterable

from labels.model.file import Location, LocationReadCloser
from labels.model.resolver import Resolver
from labels.parsers.cataloger.alpine.parse_apk_db import parse_apk_db
from labels.parsers.cataloger.arch.parse_alpm import parse_alpm_db
from labels.parsers.cataloger.debian.parse_dpkg_db import parse_dpkg_db
from labels.parsers.cataloger.generic.cataloger import (
    Request,
    Task,
    execute_parsers,
    on_next_db_file,
)
from labels.parsers.cataloger.generic.parser import Environment
from labels.parsers.cataloger.redhat.parse_rpm_db import parse_rpm_db
from labels.testing.utils.pytest_marks import parametrize_sync


def test_execute_parsers_with_none_content_reader() -> None:
    resolver = Mock(spec=Resolver)
    resolver.file_contents_by_location.return_value = None

    environment = Mock(spec=Environment)
    location = Mock(spec=Location)
    location.access_path = "test/path"
    parser = Mock()
    parser_name = "test-parser"

    task = Task(
        location=location,
        parser=parser,
        parser_name=parser_name,
    )

    result = []
    observable = from_iterable([task]).pipe(
        execute_parsers(resolver, environment),
    )
    observable.subscribe(lambda x: result.append(x))

    assert len(result) == 0
    parser.assert_not_called()


def test_execute_parsers_with_exception() -> None:
    resolver = Mock(spec=Resolver)
    content_reader = MagicMock(spec=TextIO)
    resolver.file_contents_by_location.return_value = content_reader

    environment = Mock(spec=Environment)
    location = Mock(spec=Location)
    location.access_path = "test/path"
    parser = Mock()
    parser.side_effect = Exception("Test error")
    parser_name = "test-parser"

    task = Task(
        location=location,
        parser=parser,
        parser_name=parser_name,
    )

    error_occurred = False
    observable = from_iterable([task]).pipe(
        execute_parsers(resolver, environment),
    )

    def on_error(error: Exception) -> None:
        nonlocal error_occurred
        error_occurred = True
        assert str(error) == "Test error"

    observable.subscribe(
        on_next=lambda _: None,
        on_error=on_error,
    )

    assert error_occurred
    parser.assert_called_once_with(
        resolver,
        environment,
        LocationReadCloser(
            location=location,
            read_closer=content_reader,
        ),
    )


@parametrize_sync(
    args=["file_path", "expected_parser", "expected_parser_name"],
    cases=[
        ["test/lib/apk/db/installed", parse_apk_db, "apk-db-selector"],
        ["/var/lib/dpkg/status", parse_dpkg_db, "dpkg-db-selector"],
        ["/var/lib/pacman/local/test/desc", parse_alpm_db, "alpm-db-selector"],
        ["/var/lib/rpm/Packages", parse_rpm_db, "environment-parser"],
    ],
)
def test_on_next_db_file_with_valid_files(
    file_path: str,
    expected_parser: Callable[[Resolver, Environment, LocationReadCloser], None],
    expected_parser_name: str,
) -> None:
    source = from_iterable([file_path])
    received: list[Request] = []

    on_next_db_file(source).subscribe(on_next=received.append)

    assert len(received) == 1
    request = received[0]
    assert isinstance(request, Request)
    assert request.real_path == file_path
    assert request.parser == expected_parser
    assert request.parser_name == expected_parser_name


def test_on_next_db_file_with_invalid_file() -> None:
    source = from_iterable(["/path/to/invalid.file"])
    received: list[Request] = []

    on_next_db_file(source).subscribe(on_next=received.append)

    assert received == []


def test_on_next_db_file_exception_calls_on_error() -> None:
    source = from_iterable([None])
    received: list[Request] = []
    errors: list[Exception] = []

    on_next_db_file(source).subscribe(  # type: ignore[arg-type]
        on_next=received.append,
        on_error=errors.append,
        on_completed=lambda: None,
    )

    assert len(errors) == 1
    assert isinstance(errors[0], Exception)
    assert len(received) == 0
