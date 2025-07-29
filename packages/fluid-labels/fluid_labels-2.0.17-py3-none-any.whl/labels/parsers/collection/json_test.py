from unittest.mock import MagicMock, patch

import pytest
from tree_sitter import Node

import labels.parsers.collection.json as json_module
from labels.model.indexables import FileCoordinate, IndexedDict, IndexedList, Position
from labels.parsers.collection.json import _handle_object_node, parse_json_with_tree_sitter
from labels.testing.mocks import Mock, mocks
from labels.utils.exceptions import UnexpectedNodeError


def test_parse_json() -> None:
    content = """{
    "a": 1,
    "b": 2,
    "numbers": [1,
        2,
            3,
        4.5, -4],
    "booleans": [true, false],
    "strings": ["hello", "world"],
    "null": null
  }
    """
    result = parse_json_with_tree_sitter(content)
    assert isinstance(result, IndexedDict)
    assert result.get_value_position("b").start == FileCoordinate(line=3, column=10)
    assert result.get_key_position("a") == Position(
        start=FileCoordinate(line=2, column=5),
        end=FileCoordinate(line=2, column=8),
    )
    assert result.get_value_position("numbers").start == FileCoordinate(line=4, column=16)
    assert isinstance(result["numbers"], IndexedList)
    assert result["numbers"].get_position(2).start == FileCoordinate(line=6, column=13)


def test_parse_json_with_unexpected_node() -> None:
    content = """{
    "valid": true,
    "invalid": [1, 2, @invalid_token, 4]
    }"""

    result = parse_json_with_tree_sitter(content)

    assert isinstance(result, IndexedDict)
    assert result["valid"] is True
    assert isinstance(result["invalid"], IndexedList)
    assert len(result["invalid"]) == 3
    assert result["invalid"][0] == 1
    assert result["invalid"][1] == 2
    assert result["invalid"][2] == 4


def test_parse_json_with_none_key_text() -> None:
    mock_node = MagicMock(spec=Node)
    mock_node.type = "object"
    mock_pair = MagicMock(spec=Node)
    mock_pair.type = "pair"
    mock_key = MagicMock(spec=Node)
    mock_key.text = None
    mock_value = MagicMock(spec=Node)
    mock_pair.children = [mock_key, MagicMock(spec=Node), mock_value]  # type: ignore[misc]
    mock_node.children = [mock_pair]  # type: ignore[misc]

    mock_root = MagicMock(spec=Node)
    mock_root.type = "document"
    mock_root.children = [mock_node]  # type: ignore[misc]

    with patch("tree_sitter.Parser.parse") as mock_parse:
        mock_parse.return_value.root_node = mock_root  # type: ignore[misc]
        result = parse_json_with_tree_sitter("{}")

        assert isinstance(result, IndexedDict)
        assert len(result) == 0


def test_parse_json_with_unexpected_object_node(caplog: pytest.LogCaptureFixture) -> None:
    mock_node = MagicMock(spec=Node)
    mock_node.type = "object"

    mock_pair = MagicMock(spec=Node)
    mock_pair.type = "pair"
    mock_key = MagicMock(spec=Node)
    mock_key.text = b'"key"'
    mock_pair.children = [mock_key, MagicMock(spec=Node), MagicMock(spec=Node)]  # type: ignore[misc]
    mock_node.children = [mock_pair]  # type: ignore[misc]

    with patch(
        "labels.parsers.collection.json.handle_json_node",
        side_effect=UnexpectedNodeError(""),
    ):
        result = _handle_object_node(mock_node)

        assert result == (mock_node, IndexedDict())
        assert "Unexpected node type encountered while handling object node" in caplog.text


def test_parse_json_with_unexpected_node_in_root(caplog: pytest.LogCaptureFixture) -> None:
    with patch(
        "labels.parsers.collection.json.handle_json_node",
        side_effect=UnexpectedNodeError(""),
    ):
        result = parse_json_with_tree_sitter("{}")

        assert isinstance(result, IndexedDict)
        assert len(result) == 0
        assert "Unexpected node type encountered" in caplog.text


@mocks(
    mocks=[
        Mock(
            module=json_module,
            target="handle_json_node",
            target_type="sync",
            expected=(None, None),
        ),
    ],
)
async def test_parse_json_with_invalid_value_type(caplog: pytest.LogCaptureFixture) -> None:
    result = parse_json_with_tree_sitter("{}")

    assert isinstance(result, IndexedDict)
    assert len(result) == 0
    assert "JSON parsing failed" in caplog.text
