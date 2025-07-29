import tree_sitter_json
from tree_sitter import Language, Node, Parser

from labels.model.indexables import FileCoordinate, IndexedDict, IndexedList, Position


def create_test_node(content: bytes = b'{"test": "value"}') -> Node:
    parser = Parser()
    parser.language = Language(tree_sitter_json.language())
    tree = parser.parse(content)
    return tree.root_node


def test_indexed_dict_with_node() -> None:
    indexed_dict = IndexedDict[str, str]()

    key_node = create_test_node(b'{"key": "test"}')
    value_node = create_test_node(b'{"value": "test"}')

    indexed_dict[("test_key", key_node)] = ("test_value", value_node)

    assert indexed_dict["test_key"] == "test_value"

    key_pos = indexed_dict.get_key_position("test_key")
    value_pos = indexed_dict.get_value_position("test_key")

    assert key_pos is not None
    assert value_pos is not None


def test_indexed_dict_with_position() -> None:
    node = create_test_node()
    indexed_dict = IndexedDict[str, str](node)

    key_pos = Position(
        start=FileCoordinate(line=2, column=3),
        end=FileCoordinate(line=2, column=6),
    )
    value_pos = Position(
        start=FileCoordinate(line=2, column=8),
        end=FileCoordinate(line=2, column=13),
    )

    indexed_dict[("test_key", key_pos)] = ("test_value", value_pos)

    assert indexed_dict["test_key"] == "test_value"

    assert indexed_dict.get_key_position("test_key") == key_pos
    assert indexed_dict.get_value_position("test_key") == value_pos


def test_indexed_list_with_node() -> None:
    node = create_test_node()
    indexed_list = IndexedList[str](node)

    value_node = create_test_node(b'{"item": "test"}')
    indexed_list.append(("test_value", value_node))

    assert indexed_list[0] == "test_value"

    pos = indexed_list.get_position(0)
    assert pos is not None


def test_indexed_list_with_position() -> None:
    node = create_test_node()
    indexed_list = IndexedList[str](node)

    value_pos = Position(
        start=FileCoordinate(line=2, column=3),
        end=FileCoordinate(line=2, column=8),
    )
    indexed_list.append(("test_value", value_pos))

    assert indexed_list[0] == "test_value"

    assert indexed_list.get_position(0) == value_pos


def test_indexed_list_setitem() -> None:
    indexed_list = IndexedList[str]()

    pos = Position(
        start=FileCoordinate(line=1, column=1),
        end=FileCoordinate(line=1, column=5),
    )
    indexed_list.append(("initial_value", pos))

    indexed_list[0] = ("test_value", pos)

    assert indexed_list[0] == "test_value"
    assert indexed_list.get_position(0) == pos

    new_pos = Position(
        start=FileCoordinate(line=2, column=1),
        end=FileCoordinate(line=2, column=5),
    )
    indexed_list[0] = ("new_value", new_pos)

    assert indexed_list[0] == "new_value"
    assert indexed_list.get_position(0) == new_pos


def test_indexed_dict_empty() -> None:
    indexed_dict = IndexedDict[str, str]()
    assert len(indexed_dict) == 0
    assert len(indexed_dict.position_value_index) == 0
    assert len(indexed_dict.position_key_index) == 0


def test_indexed_list_empty() -> None:
    indexed_list = IndexedList[str]()
    assert len(indexed_list) == 0
