from pathlib import Path

from labels.parsers.cataloger.java.model import JavaPomProperties
from labels.parsers.cataloger.java.parse_pom_properties import parse_pom_properties
from labels.testing.utils.helpers import get_test_data_path
from labels.testing.utils.pytest_marks import parametrize_sync

SMALL_POM_PROPERTIES = get_test_data_path("dependencies/java/pom/small.pom.properties")
EXTRA_POM_PROPERTIES = get_test_data_path("dependencies/java/pom/extra.pom.properties")
COLON_DELIMITED_POM_PROPERTIES = get_test_data_path(
    "dependencies/java/pom/colon-delimited.pom.properties",
)
EQUALS_DELIMITED_POM_PROPERTIES = get_test_data_path(
    "dependencies/java/pom/equals-delimited-with-colons.pom.properties",
)
COLON_DELIMITED_WITH_EQUALS_POM_PROPERTIES = get_test_data_path(
    "dependencies/java/pom/colon-delimited-with-equals.pom.properties",
)


@parametrize_sync(
    args=["test_data_path", "expected"],
    cases=[
        [
            SMALL_POM_PROPERTIES,
            JavaPomProperties(
                name=None,
                group_id="org.anchore",
                artifact_id="example-java-app-maven",
                version="0.1.0",
                path=SMALL_POM_PROPERTIES,
                scope=None,
                extra={},
            ),
        ],
        [
            EXTRA_POM_PROPERTIES,
            JavaPomProperties(
                name="something-here",
                group_id="org.anchore",
                artifact_id="example-java-app-maven",
                version="0.1.0",
                path=EXTRA_POM_PROPERTIES,
                scope=None,
                extra={"another": "thing", "sweet": "work"},
            ),
        ],
        [
            COLON_DELIMITED_POM_PROPERTIES,
            JavaPomProperties(
                name=None,
                group_id="org.anchore",
                artifact_id="example-java-app-maven",
                version="0.1.0",
                path=COLON_DELIMITED_POM_PROPERTIES,
                scope=None,
                extra={},
            ),
        ],
        [
            EQUALS_DELIMITED_POM_PROPERTIES,
            JavaPomProperties(
                name=None,
                group_id="org.anchore",
                artifact_id="example-java:app-maven",
                version="0.1.0:something",
                path=EQUALS_DELIMITED_POM_PROPERTIES,
                scope=None,
                extra={},
            ),
        ],
        [
            COLON_DELIMITED_WITH_EQUALS_POM_PROPERTIES,
            JavaPomProperties(
                name=None,
                group_id="org.anchore",
                artifact_id="example-java=app-maven",
                version="0.1.0=something",
                path=COLON_DELIMITED_WITH_EQUALS_POM_PROPERTIES,
                scope=None,
                extra={},
            ),
        ],
    ],
)
def test_parse_pom_properties(
    test_data_path: str,
    expected: JavaPomProperties,
) -> None:
    with Path(test_data_path).open(encoding="utf-8") as reader:
        result = parse_pom_properties(test_data_path, reader.read())
        assert result is not None
        assert result == expected
