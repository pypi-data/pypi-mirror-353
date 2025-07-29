import sqlite3
from collections.abc import Callable
from types import ModuleType
from typing import cast
from unittest import mock

import labels.advisories.database
from labels.advisories.images import ImagesDatabase
from labels.advisories.images_test import get_mocked_connection as images_get_mocked_connection
from labels.advisories.roots import RootsDatabase
from labels.advisories.roots_test import get_mocked_connection as roots_get_mocked_connection
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.pytest_marks import parametrize_sync

DATABASE_IMPLEMENTATIONS: list[list[object]] = [
    [ImagesDatabase],
    [RootsDatabase],
]

DATABASE_IMPLEMENTATIONS_WITH_CONNECTION: list[list[object]] = [
    [ImagesDatabase, images_get_mocked_connection],
    [RootsDatabase, roots_get_mocked_connection],
]


@parametrize_sync(
    args=["database_class"],
    cases=DATABASE_IMPLEMENTATIONS,
)
def test_database_get_connection_none(
    database_class: type[ImagesDatabase | RootsDatabase],
) -> None:
    database = database_class()
    database.connection = None

    result_connection = database.get_connection()
    assert result_connection is not None
    result_connection.close()


@parametrize_sync(
    args=["database_class", "get_mocked_connection"],
    cases=DATABASE_IMPLEMENTATIONS_WITH_CONNECTION,
)
def test_database_get_connection_existent(
    database_class: type[ImagesDatabase | RootsDatabase],
    get_mocked_connection: Callable[[str], sqlite3.Connection],
) -> None:
    database = database_class()
    assert database.connection is None
    new_connection = get_mocked_connection(":memory:")
    database.connection = new_connection
    assert database.connection is not None
    assert database.connection == new_connection
    database.connection.close()


@parametrize_sync(
    args=["database_class"],
    cases=DATABASE_IMPLEMENTATIONS,
)
@mocks(
    mocks=[
        Mock(
            module=cast(ModuleType, labels.advisories.database.BaseDatabase),
            target="_initialize_db",
            target_type="sync",
            expected=True,
        ),
    ],
)
async def test_database_initialize(
    database_class: type[ImagesDatabase | RootsDatabase],
) -> None:
    database = database_class()
    database.initialize()

    assert database.connection is not None
    database.connection.close()


@parametrize_sync(
    args=["database_class"],
    cases=DATABASE_IMPLEMENTATIONS,
)
@mocks(
    mocks=[
        Mock(
            module=cast(ModuleType, labels.advisories.database.BaseDatabase),
            target="is_up_to_date",
            target_type="sync",
            expected=True,
        ),
    ],
)
async def test_initialize_db_up_to_date(
    database_class: type[ImagesDatabase | RootsDatabase],
) -> None:
    with mock.patch("labels.advisories.database.Path") as mock_path:
        mock_path.return_value.is_file.return_value = True
        database = database_class()
        database.initialize()
        assert database.connection is not None


@parametrize_sync(
    args=["database_class"],
    cases=DATABASE_IMPLEMENTATIONS,
)
@mocks(
    mocks=[
        Mock(
            module=cast(ModuleType, labels.advisories.database.BaseDatabase),
            target="is_up_to_date",
            target_type="sync",
            expected=False,
        ),
        Mock(
            module=cast(ModuleType, labels.advisories.database.BaseDatabase),
            target="_get_database_file",
            target_type="sync",
            expected=None,
        ),
    ],
)
async def test_initialize_db_needs_update(
    database_class: type[ImagesDatabase | RootsDatabase],
) -> None:
    with mock.patch("labels.advisories.database.Path") as mock_path:
        mock_path.return_value.is_file.return_value = True
        database = database_class()
        database.initialize()
        assert database.connection is not None
        mock_path.return_value.unlink.assert_called_once()


@parametrize_sync(
    args=["database_class"],
    cases=DATABASE_IMPLEMENTATIONS,
)
@mocks(
    mocks=[
        Mock(
            module=cast(ModuleType, labels.advisories.database.BaseDatabase),
            target="is_up_to_date",
            target_type="function",
            expected=mock.MagicMock(side_effect=Exception("Connection error")),
        ),
    ],
)
async def test_initialize_db_exception_with_local_db(
    database_class: type[ImagesDatabase | RootsDatabase],
) -> None:
    with mock.patch("labels.advisories.database.Path") as mock_path:
        mock_path.return_value.is_file.return_value = True
        database = database_class()
        database.initialize()
        assert database.connection is not None


@parametrize_sync(
    args=["database_class"],
    cases=DATABASE_IMPLEMENTATIONS,
)
@mocks(
    mocks=[
        Mock(
            module=cast(ModuleType, labels.advisories.database.BaseDatabase),
            target="is_up_to_date",
            target_type="function",
            expected=mock.MagicMock(side_effect=Exception("Connection error")),
        ),
    ],
)
async def test_initialize_db_exception_without_local_db(
    database_class: type[ImagesDatabase | RootsDatabase],
) -> None:
    with mock.patch("labels.advisories.database.Path") as mock_path:
        mock_path.return_value.is_file.return_value = False
        database = database_class()
        database.initialize()
        assert database.connection is None


@parametrize_sync(
    args=["database_class"],
    cases=DATABASE_IMPLEMENTATIONS,
)
async def test_is_database_up_to_date_with_newer_local(
    database_class: type[ImagesDatabase | RootsDatabase],
) -> None:
    mock_s3_client = mock.MagicMock(
        head_object=mock.MagicMock(
            return_value={"LastModified": mock.MagicMock(timestamp=lambda: 100.0)},
        ),
    )
    with (
        mock.patch("boto3.client", return_value=mock_s3_client),
        mock.patch("labels.advisories.database.Path") as mock_path,
    ):
        mock_path.return_value.stat.return_value.st_mtime = 200.0
        database = database_class()
        assert database.is_up_to_date(local_database_exists=True) is True


@parametrize_sync(
    args=["database_class"],
    cases=DATABASE_IMPLEMENTATIONS,
)
async def test_is_database_up_to_date_with_older_local(
    database_class: type[ImagesDatabase | RootsDatabase],
) -> None:
    mock_s3_client = mock.MagicMock(
        head_object=mock.MagicMock(
            return_value={"LastModified": mock.MagicMock(timestamp=lambda: 200.0)},
        ),
    )
    with (
        mock.patch("boto3.client", return_value=mock_s3_client),
        mock.patch("labels.advisories.database.Path") as mock_path,
    ):
        mock_path.return_value.stat.return_value.st_mtime = 100.0
        database = database_class()
        assert database.is_up_to_date(local_database_exists=True) is False


@parametrize_sync(
    args=["database_class"],
    cases=DATABASE_IMPLEMENTATIONS,
)
async def test_is_database_up_to_date_without_local(
    database_class: type[ImagesDatabase | RootsDatabase],
) -> None:
    mock_s3_client = mock.MagicMock(
        head_object=mock.MagicMock(
            return_value={"LastModified": mock.MagicMock(timestamp=lambda: 100.0)},
        ),
    )
    with mock.patch("boto3.client", return_value=mock_s3_client):
        database = database_class()
        assert database.is_up_to_date(local_database_exists=False) is False
