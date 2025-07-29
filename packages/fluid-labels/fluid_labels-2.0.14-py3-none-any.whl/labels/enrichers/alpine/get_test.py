import pytest

import labels.enrichers.alpine.get
from labels.enrichers.alpine.get import (
    format_distro_version,
    get_package_versions_html,
    normalize_architecture,
)
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.pytest_marks import parametrize_async


@parametrize_async(
    args=["arch", "expected"],
    cases=[
        ["x86_64", "x86_64"],
        ["amd64", "x86_64"],
        ["i386", "x86"],
        ["i686", "x86"],
        ["arm", "arm"],
        ["armhf", "arm"],
        ["arm64", "aarch64"],
        ["aarch64", "aarch64"],
        ["ppc64le", "ppc64le"],
        ["s390x", "s390x"],
        ["unknown", "unknown"],
        [None, None],
    ],
)
async def test_normalize_architecture(arch: str | None, expected: str | None) -> None:
    result = normalize_architecture(arch)
    assert result == expected if expected != "unknown" else arch


@parametrize_async(
    args=["version", "expected"],
    cases=[
        ["3.14.0", "v3.14"],
        ["3.14", "3.14"],
        ["edge", "edge"],
        [None, "edge"],
        ["v3.14", "v3.14"],
    ],
)
async def test_format_distro_version(version: str | None, expected: str) -> None:
    result = format_distro_version(version)
    assert result == expected


@parametrize_async(
    args=["arch", "version", "expected_response"],
    cases=[
        ["x86_64", None, "test response"],
        ["amd64", "3.14.0", "test response"],
        ["unknown", None, None],
        [None, None, None],
    ],
)
@mocks(
    mocks=[
        Mock(
            module=labels.enrichers.alpine.get,
            target="make_get",
            target_type="function",
            expected=lambda *_, **kwargs: None
            if kwargs.get("params", {}).get("arch") == "unknown"
            else "test response",
        ),
    ],
)
async def test_get_package_versions_html(
    arch: str | None,
    version: str | None,
    expected_response: str | None,
) -> None:
    result = get_package_versions_html("test-pkg", distro_version=version, arch=arch)
    assert result == expected_response


@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_real_package_fetch() -> None:
    result = get_package_versions_html("alpine-base", arch="x86_64")
    assert result is not None
    assert "alpine-base" in result
    assert "x86_64" in result
