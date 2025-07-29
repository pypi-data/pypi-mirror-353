import pytest

from labels.parsers.cataloger.redhat.rpmdb.inet import htonl, htonlu


def test_htonl_basic_conversion() -> None:
    assert htonl(0x12345678) == 0x78563412
    assert htonl(-1) == -1
    assert htonl(0) == 0
    assert htonl(0x00001234) == 0x34120000


def test_htonl_overflow_error(caplog: pytest.LogCaptureFixture) -> None:
    assert htonl(2**32) == 0
    assert "Failed to convert integer" in caplog.text


def test_htonl_negative_overflow_error(caplog: pytest.LogCaptureFixture) -> None:
    assert htonl(-(2**32)) == 0
    assert "Failed to convert integer" in caplog.text


def test_htonlu_basic_conversion() -> None:
    assert htonlu(0x12345678) == 0x78563412
    assert htonlu(0) == 0
    assert htonlu(0xFFFFFFFF) == 0xFFFFFFFF


def test_htonlu_overflow_error(caplog: pytest.LogCaptureFixture) -> None:
    assert htonlu(2**32) == 0
    assert "Failed to convert unsigned integer" in caplog.text


def test_htonlu_negative_error(caplog: pytest.LogCaptureFixture) -> None:
    assert htonlu(-1) == 0
    assert "Failed to convert unsigned integer" in caplog.text
