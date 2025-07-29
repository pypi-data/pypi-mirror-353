from labels.parsers.cataloger.elixir.utils import package_url


def test_package_url_basic() -> None:
    result = package_url("phoenix", "1.7.10")
    expected = "pkg:hex/phoenix@1.7.10"
    assert result == expected


def test_package_url_with_special_characters() -> None:
    result = package_url("phoenix_live_view", "0.18.18")
    expected = "pkg:hex/phoenix_live_view@0.18.18"
    assert result == expected


def test_package_url_with_empty_version() -> None:
    result = package_url("ecto", "")
    expected = "pkg:hex/ecto"
    assert result == expected
