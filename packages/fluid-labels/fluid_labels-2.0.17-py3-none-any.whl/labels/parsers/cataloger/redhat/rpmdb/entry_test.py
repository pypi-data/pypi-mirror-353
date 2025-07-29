import struct

from labels.parsers.cataloger.redhat.rpmdb.entry import (
    EntryInfo,
    HdrBlob,
    align_diff,
    data_length,
    ei2h,
    hdrblob_init,
    hdrchk_align,
    hdrchk_range,
    hdrchk_tag,
    hdrchk_type,
    header_import,
    strtaglen,
)
from labels.parsers.cataloger.redhat.rpmdb.rpmtags import (
    HEADER_I18NTABLE,
    RPM_INT16_TYPE,
    RPM_INT32_TYPE,
    RPM_MAX_TYPE,
    RPM_MIN_TYPE,
    RPM_STRING_ARRAY_TYPE,
    RPM_STRING_TYPE,
)
from labels.testing.utils import raises

BUFFER_ERROR = "unpack_from requires a buffer of at least 4 bytes"


def test_hdrblob_creation() -> None:
    blob = HdrBlob(
        pe_list=[],
        i_length=1,
        d_length=2,
        pv_len=3,
        data_start=4,
        data_end=5,
        region_tag=6,
        ril=7,
        rdl=8,
    )
    assert blob.pe_list == []
    assert blob.i_length == 1
    assert blob.d_length == 2
    assert blob.pv_len == 3
    assert blob.data_start == 4
    assert blob.data_end == 5
    assert blob.region_tag == 6
    assert blob.ril == 7
    assert blob.rdl == 8


def test_hdrchk_range() -> None:
    assert hdrchk_range(10, 5) is False
    assert hdrchk_range(10, -1) is True
    assert hdrchk_range(10, 11) is True


def test_hdrchk_tag() -> None:
    assert hdrchk_tag(HEADER_I18NTABLE - 1) is True
    assert hdrchk_tag(HEADER_I18NTABLE) is False
    assert hdrchk_tag(HEADER_I18NTABLE + 1) is False


def test_hdrchk_type() -> None:
    assert hdrchk_type(RPM_MIN_TYPE - 1) is True
    assert hdrchk_type(RPM_MIN_TYPE) is False
    assert hdrchk_type(RPM_MAX_TYPE) is False
    assert hdrchk_type(RPM_MAX_TYPE + 1) is True


def test_hdrchk_align() -> None:
    assert hdrchk_align(RPM_STRING_TYPE, 0) is False
    assert hdrchk_align(RPM_STRING_TYPE, 1) is False
    assert hdrchk_align(RPM_INT16_TYPE, 1) is True
    assert hdrchk_align(RPM_INT16_TYPE, 2) is False


def test_ei2h() -> None:
    entry = EntryInfo(tag=1, type=2, offset=3, count=4)
    converted = ei2h(entry)
    assert isinstance(converted, EntryInfo)


def test_data_length() -> None:
    data = b"test\0"
    assert data_length(data, RPM_STRING_TYPE, 1, 0, len(data)) == 5

    data = b"test1\0test2\0"
    assert data_length(data, RPM_STRING_ARRAY_TYPE, 2, 0, len(data)) == 12

    data = b"test\0"
    assert data_length(data, RPM_MAX_TYPE + 1, 1, 0, len(data)) == 0


def test_strtaglen() -> None:
    data = b"test\0"
    assert strtaglen(data, 1, 0, len(data)) == 5

    data = b"test1\0test2\0"
    assert strtaglen(data, 2, 0, len(data)) == 12

    assert strtaglen(data, 1, 10, 5) == -1


def test_align_diff() -> None:
    assert align_diff(RPM_STRING_TYPE, 0) == 0
    assert align_diff(RPM_INT16_TYPE, 1) == 1
    assert align_diff(RPM_INT32_TYPE, 2) == 2


def test_invalid_hdrblob_init() -> None:
    with raises(struct.error, match=BUFFER_ERROR):
        hdrblob_init(b"")

    with raises(struct.error, match=BUFFER_ERROR):
        hdrblob_init(b"123")


def test_invalid_header_import() -> None:
    with raises(struct.error, match=BUFFER_ERROR):
        header_import(b"")

    with raises(struct.error, match=BUFFER_ERROR):
        header_import(b"123")
