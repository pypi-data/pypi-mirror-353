from labels.parsers.cataloger.rust.utils import package_url


def test_package_url() -> None:
    assert package_url("serde", "1.0.0") == "pkg:cargo/serde@1.0.0"
    assert package_url("serde-json", "1.2.3") == "pkg:cargo/serde-json@1.2.3"
    assert package_url("tokio", "1.0.0-alpha.1") == "pkg:cargo/tokio@1.0.0-alpha.1"
