import reactivex
from reactivex import from_iterable

from labels.parsers.cataloger.generic.cataloger import Request
from labels.parsers.cataloger.java.cataloger import on_next_java
from labels.testing.utils.pytest_marks import parametrize_sync


@parametrize_sync(
    args=["file_path", "expected_parser_name"],
    cases=[
        ["pom.xml", "java-parse-pom-xml"],
        ["/path/to/pom.xml", "java-parse-pom-xml"],
        ["some/path/pom.xml", "java-parse-pom-xml"],
        ["example.jar", "java-archive-parse"],
        ["lib/example.war", "java-archive-parse"],
        ["app.ear", "java-archive-parse"],
        ["module.par", "java-archive-parse"],
        ["service.sar", "java-archive-parse"],
        ["native.nar", "java-archive-parse"],
        ["plugin.jpi", "java-archive-parse"],
        ["hudson.hpi", "java-archive-parse"],
        ["liferay.lpkg", "java-archive-parse"],
        ["gradle.lockfile", "java-parse-gradle-lock"],
        ["path/to/gradle.lockfile", "java-parse-gradle-lock"],
        ["build.gradle", "java-parse-gradle-lock"],
        ["module/build.gradle", "java-parse-gradle-lock"],
        ["settings.gradle.kts", "java-parse-gradle-kts"],
        ["app/build.gradle.kts", "java-parse-gradle-kts"],
        ["android.apk", "java-parse-apk"],
        ["apps/myapp.apk", "java-parse-apk"],
        ["build.sbt", "java-parse-build-stb"],
        ["project/build.sbt", "java-parse-build-stb"],
        ["gradle-wrapper.properties", "java-parse-gradle-properties"],
        ["/gradle-wrapper.properties", "java-parse-gradle-properties"],
        ["path/to/gradle-wrapper.properties", "java-parse-gradle-properties"],
    ],
)
def test_on_next_java_with_valid_files(file_path: str, expected_parser_name: str) -> None:
    source = from_iterable([file_path])
    received: list[Request] = []

    on_next_java(source).subscribe(on_next=received.append)

    assert len(received) == 1
    request = received[0]
    assert isinstance(request, Request)
    assert request.parser_name == expected_parser_name
    assert request.real_path == file_path


def test_on_next_java_with_invalid_file() -> None:
    source = from_iterable(["/path/to/invalid.file"])
    received: list[Request] = []

    on_next_java(source).subscribe(on_next=received.append)

    assert received == []


def test_on_next_java_exception_calls_on_error() -> None:
    source = reactivex.from_iterable([None])
    received: list[Request] = []
    errors: list[Exception] = []

    on_next_java(source).subscribe(  # type: ignore[arg-type]
        on_next=received.append,
        on_error=errors.append,
        on_completed=lambda: None,
    )

    assert len(errors) == 1
    assert isinstance(errors[0], Exception)
    assert len(received) == 0
