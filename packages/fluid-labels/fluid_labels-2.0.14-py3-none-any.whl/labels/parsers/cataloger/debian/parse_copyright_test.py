import io

from labels.parsers.cataloger.debian.parse_copyright import (
    ensure_is_single_license,
    find_license_clause,
    parse_licenses_from_copyright,
)


def test_find_license_clause() -> None:
    line = "License: MIT"
    pattern = r"^License: (?P<license>\S*)"
    value_group = "license"
    result = find_license_clause(pattern, value_group, line)
    assert result == "MIT"

    line = "/usr/share/common-licenses/GPL-3.0"
    pattern = r"/usr/share/common-licenses/(?P<license>[0-9A-Za-z_.\\-]+)"
    result = find_license_clause(pattern, value_group, line)
    assert result == "GPL-3.0"

    line = "License: none"
    result = find_license_clause(pattern, value_group, line)
    assert result is None


def test_ensure_is_single_license() -> None:
    assert ensure_is_single_license("MIT") == "MIT"
    assert ensure_is_single_license("MIT or Apache-2.0") is None
    assert ensure_is_single_license("MIT and Apache-2.0") is None
    assert ensure_is_single_license("none") is None
    assert ensure_is_single_license("GPL-3.0.") == "GPL-3.0"


def test_parse_licenses_from_copyright() -> None:
    input_data = """License: MIT"""
    reader = io.StringIO(input_data)
    result: list[str] = parse_licenses_from_copyright(reader)
    assert result == ["MIT"]

    input_data = """License: MIT\n/usr/share/common-licenses/GPL-3.0\nLicense: MIT"""
    reader = io.StringIO(input_data)
    result = parse_licenses_from_copyright(reader)
    assert set(result) == {"MIT", "GPL-3.0"}

    input_data = """License: MIT and Apache-2.0"""
    reader = io.StringIO(input_data)
    result = parse_licenses_from_copyright(reader)
    assert result == ["MIT"]

    input_data = """License: MIT."""
    reader = io.StringIO(input_data)
    result = parse_licenses_from_copyright(reader)
    assert result == ["MIT"]

    input_data = """License: none"""
    reader = io.StringIO(input_data)
    result = parse_licenses_from_copyright(reader)
    assert result == []
