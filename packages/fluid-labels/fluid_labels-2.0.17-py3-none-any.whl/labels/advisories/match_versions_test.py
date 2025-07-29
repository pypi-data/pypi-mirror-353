from labels.advisories.match_versions import (
    match_vulnerable_versions,
)
from labels.testing.utils.pytest_marks import parametrize_sync

VERSIONS_TESTS: list[list[object]] = [
    ["^1.0.0", "<0.0", False],
    ["^7.0.0", "=6.12.2", False],
    ["^7.0.0", "=6.12.2 || =6.9.1", False],
    ["~2.2.3", ">=3.0.0 <=4.0.0", False],
    ["=2.2", ">=2.3.0 <=2.4.0", False],
    ["~0.8.0", ">=0 <=1.8.6", True],
    ["1.8.0", ">=0 <=0.3.0 || >=1.0.1 <=1.8.6", True],
    ["^2.1.0", ">=0 <11.0.5 || >=11.1.0 <11.1.0", True],
    ["2.1.0", "~2", True],
    ["=2.3.0-pre", ">=2.1.1 <2.3.0", False],
    ["=2.3.0-pre", ">=2.3.0 <2.7.0", False],
    ["=2.2.0-rc1", ">=2.1.1 <2.3.0", True],
    ["=2.1.0-pre", "=2.1.0-pre", True],
    ["=2.1.0-pre", "=2.1.0", False],
    [">2.1.1 <=2.3.0", "<2.1.0||=2.3.0-pre||>=2.4.0 <2.5.0", True],
    [">2.1.1 <2.3.0", "<2.1.0||=2.3.1-pre", False],
    ["1.0.0-beta.8", "<=1.0.0-beta.6", False],
    ["1.0.0-beta.4", "<=1.0.0-beta.6", True],
    ["^1.0.0-rc.10", ">2.0.0 <=4.0.0", False],
    ["^1.0.0-rc.10", ">=1.0.0 <=2.0.0", True],
    ["^7.23.2", ">=0 <7.23.2 || >=8.0.0-alpha.0 <8.0.0-alpha.4", False],
    ["7.23.2", ">=0 <=7.23.2", True],
    ["7.23.2", ">=6.5.1", True],
    ["=7.23.2", ">=6.5.1", True],
    [">=11.1", ">=0 <12.3.3", True],
    ["^1.2.0", ">=0 <1.0.3", False],
    ["2.0.0||^3.0.0", ">=3.0.0", True],
    ["3.*", ">=3.2.0 <4.0.0", True],
    ["4.0", "=3.5.1 || =4.0 || =5.0", True],
    ["4.2.2.RELEASE", ">0 <4.2.16", True],
    ["2.13.14", ">0 <2.13.14-1", False],
    ["8.4", ">=0 <7.6.3 || >=8.0.0 <8.4.0", False],
    ["6.1.5.Final", ">=6.1.2 <6.1.5", False],
    ["6.1.5.Final", ">=6.1.2 <=6.1.5", True],
    ["==3.0.0 || >=4.0.1 <4.0.2 || ==4.0.1", "=3.0.0", True],
    ["1.16.5-x86_64-darwin", "<1.16.5", False],
    ["1.16.5-x86_64-mingw-10", "<1.16.5", False],
    ["1.16.5-aarch64-linux", "<=1.16.5", True],
    ["0.0.0-20221012-56ae", ">=0.0.0 <0.17.0", True],
    ["0.0.0-20221012-56ae", "<0.17.0", True],
    ["=0.10.0-20221012-e7cb96979f69", "<0.10.0", False],
    ["=0.10.0-20221012-e7cb96979f69", "<=0.10.0", True],
    ["${lombokVersion}", ">0", False],
    ["", ">0", False],
    ["0.0.0", None, False],
    ["2.*,<2.3", ">=2.0.1", True],
    ["2.*,<2.3", ">=1.3.0 <2.0.0", False],
    ["1.2.0", ">=1.0.0,<=2.0.0", True],
    ["1.2.0", ">=1.0.0,   <=2.0.0", True],
    ["3.2.0+incompatible", ">1.0.0 <=3.2.0", True],
]


@parametrize_sync(args=["dep_ver", "vuln_ver", "expected"], cases=VERSIONS_TESTS)
def test_match_vulnerable_versions(*, dep_ver: str, vuln_ver: str | None, expected: bool) -> None:
    is_vulnerable = match_vulnerable_versions(dep_ver, vuln_ver)
    assert is_vulnerable == expected
