from labels.model.release import Release
from labels.testing.utils.pytest_marks import parametrize_sync


@parametrize_sync(
    args=["release_data", "expected_str"],
    cases=[
        [
            {"id_": "ubuntu", "version_id": "22.04", "pretty_name": "Ubuntu 22.04 LTS"},
            "Ubuntu 22.04 LTS",
        ],
        [
            {"id_": "ubuntu", "version_id": "22.04", "name": "Ubuntu"},
            "Ubuntu",
        ],
        [
            {"id_": "ubuntu", "version_id": "22.04", "version": "22.04 LTS"},
            "ubuntu 22.04 LTS",
        ],
        [
            {"id_": "ubuntu", "version_id": "22.04"},
            "ubuntu 22.04",
        ],
        [
            {"id_": "ubuntu", "version_id": "", "build_id": "20230101"},
            "ubuntu 20230101",
        ],
        [
            {"id_": "ubuntu", "version_id": ""},
            "ubuntu ",
        ],
    ],
)
def test_release_str(
    release_data: dict[str, str | list[str] | None],
    expected_str: str,
) -> None:
    release = Release.model_validate(release_data)
    assert str(release) == expected_str
