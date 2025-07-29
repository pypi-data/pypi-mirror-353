from labels.testing.utils.pytest_marks import parametrize_sync
from labels.utils.strings import format_exception


@parametrize_sync(
    args=["input_exc", "expected"],
    cases=[
        [
            """Error occurred
    For further information visit https://example.com
    Some other details""",
            """Error occurred
    Some other details""",
        ],
        [
            """Error occurred
    Some other details""",
            """Error occurred
    Some other details""",
        ],
        [
            """Error occurred
    For further information visit https://example.com
    Some other details
    For further information check the docs""",
            """Error occurred
    Some other details
""",
        ],
    ],
)
def test_format_exception(input_exc: str, expected: str) -> None:
    assert format_exception(input_exc) == expected
