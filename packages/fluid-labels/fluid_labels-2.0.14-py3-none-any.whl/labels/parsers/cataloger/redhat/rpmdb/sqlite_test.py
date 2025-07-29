import sqlite3
import tempfile
from pathlib import Path

from labels.parsers.cataloger.redhat.rpmdb.sqlite import Sqlite, open_sqlite
from labels.testing.utils.pytest_methods import raises
from labels.utils.exceptions import InvalidDBFormatError


def create_test_db() -> tuple[str, sqlite3.Connection]:
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        connection = sqlite3.connect(temp_file.name)
        cursor = connection.cursor()

        cursor.execute("CREATE TABLE Packages (blob BLOB)")
        test_blobs = [b"test_blob_1", b"test_blob_2"]
        for blob in test_blobs:
            cursor.execute("INSERT INTO Packages (blob) VALUES (?)", (blob,))
        connection.commit()

        return temp_file.name, connection


def cleanup_db(db_path: str, connection: sqlite3.Connection) -> None:
    connection.close()
    Path(db_path).unlink()


def test_open_sqlite_success() -> None:
    db_path, connection = create_test_db()
    try:
        db = open_sqlite(db_path)
        assert isinstance(db, Sqlite)
    finally:
        cleanup_db(db_path, connection)


def test_open_sqlite_invalid_db() -> None:
    with tempfile.NamedTemporaryFile(delete=False) as invalid_db:
        invalid_db.write(b"not a sqlite database")
        invalid_db.flush()
        with raises(InvalidDBFormatError):
            open_sqlite(invalid_db.name)
        Path(invalid_db.name).unlink()


def test_read_blobs() -> None:
    db_path, connection = create_test_db()
    try:
        db = Sqlite(connection)
        blobs = list(db.read())
        assert len(blobs) == 2
        assert b"test_blob_1" in blobs
        assert b"test_blob_2" in blobs
    finally:
        cleanup_db(db_path, connection)


def test_read_empty_db() -> None:
    db_path, connection = create_test_db()
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Packages")
        connection.commit()

        db = Sqlite(connection)
        blobs = list(db.read())
        assert len(blobs) == 0
    finally:
        cleanup_db(db_path, connection)
