from labels.model.release import Release
from labels.parsers.cataloger.utils import extract_distro_info, purl_qualifiers
from labels.testing.utils.pytest_marks import parametrize_sync


@parametrize_sync(
    args=["qualifiers", "release", "expected"],
    cases=[
        [{"key1": "value1"}, None, {"key1": "value1"}],
        [
            {"type": "rpm"},
            Release(id_="el8", version_id=""),
            {"type": "rpm", "distro": "el8"},
        ],
        [
            {"type": "rpm"},
            Release(id_="el8", version_id="8.4"),
            {"type": "rpm", "distro": "el8-8.4"},
        ],
        [
            {"type": "rpm"},
            Release(id_="el8", version_id="", build_id="123"),
            {"type": "rpm", "distro": "el8-123"},
        ],
        [
            {"type": "rpm"},
            Release(id_="", version_id="8.4"),
            {"type": "rpm", "distro": "8.4"},
        ],
        [
            {"type": "rpm"},
            Release(id_="", version_id="", build_id=""),
            {"type": "rpm"},
        ],
        [{"key": None}, None, {}],
        [{}, None, {}],
    ],
)
def test_purl_qualifiers(
    qualifiers: dict[str, str | None],
    release: Release | None,
    expected: dict[str, str],
) -> None:
    result = purl_qualifiers(qualifiers, release)
    assert result == expected


@parametrize_sync(
    args=["pkg_str", "expected"],
    cases=[
        [
            "pkg:rpm/redhat/bash?distro_id=el8&distro_version_id=8.4&arch=x86_64",
            ("el8", "8.4", "x86_64"),
        ],
        ["pkg:rpm/redhat/bash", (None, None, None)],
        [
            "pkg:rpm/redhat/bash?distro_id=el8",
            ("el8", None, None),
        ],
        [
            "pkg:rpm/redhat/bash?",
            (None, None, None),
        ],
    ],
)
def test_extract_distro_info(
    pkg_str: str,
    expected: tuple[str | None, str | None, str | None],
) -> None:
    result = extract_distro_info(pkg_str)
    assert result == expected
