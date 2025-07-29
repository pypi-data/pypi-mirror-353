from labels.utils.licenses.validation import (
    find_license_by_pattern,
    sanitize_license_string,
    validate_licenses,
)


def test_sanitize_license_string() -> None:
    assert sanitize_license_string("  MIT  ") == "MIT"
    assert sanitize_license_string("Apache,2.0") == "Apache 2.0"
    assert sanitize_license_string("GPL\t3.0") == "GPL 3.0"
    assert sanitize_license_string("MIT    License") == "MIT"
    assert sanitize_license_string("Apache,  Version  2.0") == "Apache 2.0"


def test_find_license_by_pattern() -> None:
    assert find_license_by_pattern("mit") == "MIT"
    assert find_license_by_pattern("gpl 3.0") == "GPL-3.0-only"
    assert find_license_by_pattern("apache 2.0") == "Apache-2.0"
    assert find_license_by_pattern("Invalid License") is None


def test_validate_licenses_basic_integration() -> None:
    result = validate_licenses(["MIT", "Apache 2.0"])
    assert result == ["Apache-2.0", "MIT"]

    result = validate_licenses(["MIT License", "The MIT License", "Apache Version 2.0"])
    assert result == ["Apache-2.0", "MIT"]

    result = validate_licenses(["MIT", "Invalid", "Apache 2.0"])
    assert result == ["Apache-2.0", "MIT"]

    assert validate_licenses(["Unknown", "Nope"]) == []
    assert validate_licenses([]) == []


def test_validate_licenses_with_full_name_fallback() -> None:
    result = validate_licenses(["GNU General Public License v3.0 only"])
    assert result == ["GPL-3.0-only"]
