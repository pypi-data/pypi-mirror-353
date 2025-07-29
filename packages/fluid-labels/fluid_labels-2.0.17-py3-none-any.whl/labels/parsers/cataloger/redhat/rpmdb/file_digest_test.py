from labels.testing.utils.pytest_marks import parametrize_sync

from .file_digest import DigestAlgorithm


@parametrize_sync(
    args=["algorithm_id", "expected_name"],
    cases=[
        [1, "md5"],
        [2, "sha1"],
        [3, "ripemd160"],
        [5, "md2"],
        [6, "tiger192"],
        [7, "haval-5-160"],
        [8, "sha256"],
        [9, "sha384"],
        [10, "sha512"],
        [11, "sha224"],
        [999, "unknown-digest-algorithm"],
        [-1, "unknown-digest-algorithm"],
    ],
)
def test_digest_algorithm(algorithm_id: int, expected_name: str) -> None:
    digest = DigestAlgorithm(algorithm=algorithm_id)
    assert digest.get_algorithm_name() == expected_name
    assert str(digest) == expected_name
