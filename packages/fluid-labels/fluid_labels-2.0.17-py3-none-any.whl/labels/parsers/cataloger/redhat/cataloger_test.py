import reactivex
from reactivex import from_iterable

from labels.parsers.cataloger.generic.cataloger import Request
from labels.parsers.cataloger.redhat.cataloger import on_next_redhat
from labels.testing.utils.pytest_marks import parametrize_sync


@parametrize_sync(
    args=["file_path", "expected_parser"],
    cases=[
        ["/var/lib/rpm/rpmdb.sqlite", "redhat-parse-rpmdb"],
        ["/path/to/package.rpm", "redhat-parse-rpmdb"],
    ],
)
def test_on_next_redhat_with_valid_files(file_path: str, expected_parser: str) -> None:
    source = from_iterable([file_path])
    received: list[Request] = []

    on_next_redhat(source).subscribe(on_next=received.append)

    assert len(received) == 1
    request = received[0]
    assert isinstance(request, Request)
    assert request.parser_name == expected_parser


def test_on_next_redhat_with_invalid_file() -> None:
    source = from_iterable(["/path/to/invalid.file"])
    received: list[Request] = []

    on_next_redhat(source).subscribe(on_next=received.append)

    assert received == []


def test_on_next_redhat_exception_calls_on_error() -> None:
    source = reactivex.from_iterable([None])
    received: list[Request] = []
    errors: list[Exception] = []

    on_next_redhat(source).subscribe(  # type: ignore[arg-type]
        on_next=received.append,
        on_error=errors.append,
        on_completed=lambda: None,
    )

    assert len(errors) == 1
    assert isinstance(errors[0], Exception)
    assert len(received) == 0
