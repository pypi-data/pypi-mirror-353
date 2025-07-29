from io import StringIO

from labels.model.indexables import ParsedValue
from labels.parsers.cataloger.python.parse_wheel_egg_metadata import (
    _handle_multiline_values,
    _handle_platform,
    _process_line,
    determine_site_package_root_package,
    parse_metadata,
    parse_wheel_or_egg_metadata,
    required_dependencies,
)
from labels.testing.utils.pytest_marks import parametrize_sync


@parametrize_sync(
    args=["path", "expected"],
    cases=[
        [
            "/usr/local/lib/python3.8/site-packages/my_package-1.0.0-py3.8.egg-info",
            "/usr/local/lib/python3.8/site-packages",
        ],
        [
            "/usr/local/lib/python3.8/site-packages/my_package-1.0.0.dist-info",
            "/usr/local/lib/python3.8/site-packages",
        ],
        [
            "/usr/local/lib/python3.8/site-packages/my_package/__init__.py",
            "/usr/local/lib/python3.8/site-packages",
        ],
        [
            "/usr/local/lib/python3.8/site-packages/my_package/subpackage.egg-info",
            "/usr/local/lib/python3.8/site-packages/my_package",
        ],
    ],
)
def test_determine_site_package_root_package(path: str, expected: str) -> None:
    assert determine_site_package_root_package(path) == expected


@parametrize_sync(
    args=["line", "multi_line_key", "parsed_data", "expected_result", "expected_data"],
    cases=[
        ["new line", "", {}, "", {}],
        [
            "new line",
            "Description",
            {"Description": ["value1", "value2"]},
            "Description",
            {"Description": ["value1", "value2"]},
        ],
        [
            "new line",
            "Description",
            {"Description": "initial value"},
            "Description",
            {"Description": "initial value\nnew line"},
        ],
    ],
)
def test_handle_multiline_values_no_if(
    line: str,
    multi_line_key: str,
    parsed_data: dict[str, str | list[str]],
    expected_result: str,
    expected_data: dict[str, str | list[str]],
) -> None:
    result = _handle_multiline_values(line, multi_line_key, parsed_data)
    assert result == expected_result
    assert parsed_data == expected_data


@parametrize_sync(
    args=["line", "parsed_data", "expected_result", "expected_data"],
    cases=[
        ["This is a line without colon", {}, "", {}],
        ["", {}, "", {}],
        ["   ", {}, "", {}],
    ],
)
def test_process_line_no_if(
    line: str,
    parsed_data: dict[str, str | list[str]],
    expected_result: str,
    expected_data: dict[str, str | list[str]],
) -> None:
    result = _process_line(line, parsed_data)
    assert result == expected_result
    assert parsed_data == expected_data


@parametrize_sync(
    args=["metadata", "expected"],
    cases=[
        [
            """Name: my_package
Version: 1.0.0

Author: John Doe
""",
            {
                "Name": "my_package",
                "Version": "1.0.0",
            },
        ],
        [
            """Name: my_package
Version: 1.0.0


Author: John Doe
""",
            {
                "Name": "my_package",
                "Version": "1.0.0",
            },
        ],
        [
            """Name: my_package
Version: 1.0.0
Author: John Doe

""",
            {
                "Name": "my_package",
                "Version": "1.0.0",
                "Author": "John Doe",
            },
        ],
    ],
)
def test_parse_metadata_empty_line(metadata: str, expected: dict[str, str | list[str]]) -> None:
    result = parse_metadata(metadata)
    assert result == expected


@parametrize_sync(
    args=["requires_dis", "provides_extra", "expected"],
    cases=[
        ["requests>=2.0.0", None, ["requests>=2.0.0"]],
        [["requests>=2.0.0", "pytest>=7.0.0"], None, ["requests>=2.0.0", "pytest>=7.0.0"]],
        ["requests>=2.0.0; extra == 'test'", ["test"], []],
        [
            ["requests>=2.0.0", "pytest>=7.0.0; extra == 'test'", "black>=22.0.0; extra == 'dev'"],
            ["test", "dev"],
            ["requests>=2.0.0"],
        ],
        ["requests>=2.0.0; python_version >= '3.8'", None, ["requests>=2.0.0"]],
    ],
)
def test_required_dependencies(
    requires_dis: str | list[str],
    provides_extra: list[str] | None,
    expected: list[str],
) -> None:
    result = required_dependencies(requires_dis, provides_extra)
    assert result == expected


@parametrize_sync(
    args=["input_value", "expected"],
    cases=[
        ["linux-x86_64", "linux-x86_64"],
        [["linux-x86_64", "win32"], '["linux-x86_64", "win32"]'],
        [None, None],
        [123, None],
    ],
)
def test_handle_platform(input_value: ParsedValue, expected: str | None) -> None:
    result = _handle_platform(input_value)
    assert result == expected


@parametrize_sync(
    args=["metadata", "path", "expected_license_location"],
    cases=[
        [
            """Name: my_package
Version: 1.0.0
License-File: LICENSE
""",
            "/usr/local/lib/python3.8/site-packages/my_package-1.0.0-py3.8.egg-info",
            "/usr/local/lib/python3.8/site-packages/LICENSE",
        ],
        [
            """Name: my_package
Version: 1.0.0
License-File: docs/LICENSE.txt
""",
            "/usr/local/lib/python3.8/site-packages/my_package-1.0.0.dist-info",
            "/usr/local/lib/python3.8/site-packages/docs/LICENSE.txt",
        ],
    ],
)
def test_parse_wheel_or_egg_metadata_with_license_file(
    metadata: str,
    path: str,
    expected_license_location: str,
) -> None:
    result = parse_wheel_or_egg_metadata(path, StringIO(metadata))
    assert result is not None
    assert result.license_location is not None
    assert result.license_location.access_path == expected_license_location


@parametrize_sync(
    args=["metadata", "path"],
    cases=[
        [
            """Name: my_package
Version: 1.0.0
License-File: LICENSE
License-File: LICENSE.txt
""",
            "/usr/local/lib/python3.8/site-packages/my_package-1.0.0-py3.8.egg-info",
        ],
        [
            """Name: my_package
Version: 1.0.0
""",
            "/usr/local/lib/python3.8/site-packages/my_package-1.0.0.dist-info",
        ],
    ],
)
def test_parse_wheel_or_egg_metadata_without_license_file(
    metadata: str,
    path: str,
) -> None:
    from io import StringIO

    result = parse_wheel_or_egg_metadata(path, StringIO(metadata))
    assert result is not None
    assert result.license_location is None
