import pytest

from labels.enrichers.dart.get import get_pub_package


@pytest.mark.flaky(reruns=3, runs_delay=2)
async def test_get_pub_package_real_request() -> None:
    result = get_pub_package("http")
    assert result is not None
    assert result["name"] == "http"
    assert "latest" in result
    assert "version" in result["latest"]
