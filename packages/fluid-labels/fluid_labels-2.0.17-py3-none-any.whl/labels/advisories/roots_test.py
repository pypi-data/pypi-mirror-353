import sqlite3
from unittest import mock

from labels.advisories.roots import get_package_advisories, get_vulnerabilities


def create_database_connection(database: str) -> sqlite3.Connection:
    return sqlite3.connect(database)


def setup_test_database(connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE advisories (
        adv_id TEXT,
        source TEXT,
        vulnerable_version TEXT,
        severity_level TEXT,
        severity TEXT,
        severity_v4 TEXT,
        epss REAL,
        details TEXT,
        percentile REAL,
        cwe_ids TEXT,
        cve_finding TEXT,
        package_manager TEXT,
        platform_version TEXT,
        package_name TEXT,
        auto_approve BOOLEAN
    )
    """)

    cursor.execute("""
    INSERT INTO advisories VALUES (
        'ADV-001', 'https://example.com', '>=1.0.0', 'High', '7.5', '8.0',
        0.5, 'Descripción', 0.75, '["CWE-79"]', 'CVE-2023-1234', 'npm',
        'ubuntu:20.04', 'test-package', false
    )
    """)
    connection.commit()


def get_mocked_connection(database: str) -> sqlite3.Connection:
    connection = create_database_connection(database)
    setup_test_database(connection)
    return connection


@mock.patch("labels.advisories.roots.DATABASE.get_connection")
def test_get_package_advisorie(connect_to_db: mock.MagicMock) -> None:
    connection = get_mocked_connection(":memory:")
    connect_to_db.return_value = connection
    try:
        result = get_package_advisories("npm", "test-package", "1.1.0")

        assert len(result) == 1
        assert result[0].id == "ADV-001"
        assert result[0].urls == ["https://example.com"]
        assert result[0].version_constraint == ">=1.0.0"
        assert result[0].severity == "High"
        assert result[0].namespace == "npm"
        assert result[0].cwe_ids == ["CWE-79"]
        assert result[0].cve_finding == "CVE-2023-1234"
        assert result[0].auto_approve is False
    finally:
        connection.close()


@mock.patch("labels.advisories.roots.DATABASE.get_connection")
def test_get_vulnerabilities_with_matching_versions(connect_to_db: mock.MagicMock) -> None:
    connection = get_mocked_connection(":memory:")
    connect_to_db.return_value = connection
    try:
        result = get_vulnerabilities("npm", "test-package", "1.1.0")

        assert len(result) == 1
        assert result[0].id == "ADV-001"
    finally:
        connection.close()


@mock.patch("labels.advisories.roots.DATABASE.get_connection")
def test_get_vulnerabilities_with_non_matching_versions(connect_to_db: mock.MagicMock) -> None:
    connection = get_mocked_connection(":memory:")
    connect_to_db.return_value = connection
    try:
        result = get_vulnerabilities("npm", "test-package", "0.9.0")
        assert len(result) == 0
    finally:
        connection.close()


@mock.patch("labels.advisories.roots.DATABASE.get_connection")
def test_get_vulnerabilities_with_empty_params(connect_to_db: mock.MagicMock) -> None:
    connection = get_mocked_connection(":memory:")
    connect_to_db.return_value = connection
    try:
        result = get_vulnerabilities("npm", "", "1.1.0")

        assert len(result) == 0
    finally:
        connection.close()
