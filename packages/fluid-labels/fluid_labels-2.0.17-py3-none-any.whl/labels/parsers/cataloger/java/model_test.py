from labels.model.package import PackageType
from labels.parsers.cataloger.java.model import JavaPomProperties
from labels.testing.utils.pytest_marks import parametrize_sync


@parametrize_sync(
    args=["group_id", "expected_type"],
    cases=[
        ["org.jenkins-ci.plugins", PackageType.JenkinsPluginPkg],
        ["org.jenkins-ci.plugins.something", PackageType.JenkinsPluginPkg],
        ["io.jenkins.plugins", PackageType.JenkinsPluginPkg],
        ["io.jenkins.plugins.myPlugin", PackageType.JenkinsPluginPkg],
        ["com.example.jenkins.plugin.test", PackageType.JenkinsPluginPkg],
        ["org.example.jenkins.plugin", PackageType.JenkinsPluginPkg],
        ["org.apache.commons", PackageType.JavaPkg],
        ["com.example", PackageType.JavaPkg],
        ["", PackageType.JavaPkg],
        [None, PackageType.JavaPkg],
        ["org.jenkins", PackageType.JavaPkg],
        ["com.jenkinsci", PackageType.JavaPkg],
    ],
)
def test_pkg_type_indicated(group_id: str | None, expected_type: PackageType) -> None:
    props = JavaPomProperties(
        group_id=group_id,
        artifact_id="test-artifact",
        version="1.0.0",
        path="/test/path",
    )
    assert props.pkg_type_indicated() == expected_type
