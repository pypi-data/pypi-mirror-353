from labels.advisories.utils import generate_cpe


def test_generate_cpe() -> None:
    cpe = generate_cpe("java", "com.vendor:package-name", "1.2.3")
    assert cpe == "cpe:2.3:a:com.vendor:com.vendor:package-name:1.2.3:*:*:java:*:*:*:*"
