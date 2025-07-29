from typing import cast

import tree_sitter_yaml
from tree_sitter import Language as TLanguage
from tree_sitter import Node, Parser

from labels.model.indexables import IndexedDict, IndexedList, Position
from labels.parsers.collection.yaml import (
    _handle_block_mapping_node,
    _handle_block_node,
    _handle_block_sequence_item,
    _handle_block_sequence_node,
    _handle_float_scalar_node,
    _handle_flow_mapping_node,
    _handle_flow_node,
    _handle_flow_sequence_node,
    _handle_node_result,
    handle_node,
    parse_yaml_with_tree_sitter,
)
from labels.testing.utils.pytest_methods import raises
from labels.utils.exceptions import (
    UnexpectedChildrenLengthError,
    UnexpectedNodeError,
    UnexpectedNodeTypeError,
)


def test_parse_yaml_with_tree_sitter_basic() -> None:
    yaml_content = """
key1: value1
key2: value2
"""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert isinstance(result, IndexedDict)
    assert len(result) == 2
    assert "key1" in result
    assert "key2" in result
    assert result["key1"] == "value1"
    assert result["key2"] == "value2"

    key1_pos = result.get_key_position("key1")
    assert isinstance(key1_pos, Position)
    assert key1_pos.start.line == 2


def test_parse_yaml_with_tree_sitter_nested() -> None:
    yaml_content = """
outer:
  inner1: value1
  inner2: value2
"""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert isinstance(result, IndexedDict)
    assert len(result) == 1
    assert "outer" in result
    outer_dict = result["outer"]
    assert isinstance(outer_dict, IndexedDict)
    assert len(outer_dict) == 2
    assert outer_dict["inner1"] == "value1"
    assert outer_dict["inner2"] == "value2"


def test_parse_yaml_with_tree_sitter_types() -> None:
    yaml_content = """
string_value: text
int_value: 42
bool_value: true
null_value: null
float_value: 3.14
"""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert isinstance(result, IndexedDict)
    assert result["string_value"] == "text"
    assert result["int_value"] == 42
    assert result["bool_value"] is True
    assert result["null_value"] is None
    assert result["float_value"] == 3.14


def test_parse_yaml_with_tree_sitter_invalid() -> None:
    invalid_yaml = "{"
    result = parse_yaml_with_tree_sitter(invalid_yaml)
    assert result is None


def test_block_mapping_with_missing_value() -> None:
    yaml_content = """
key1:
key2: value2
"""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert isinstance(result, IndexedDict)
    assert result["key1"] is None
    assert result["key2"] == "value2"


def test_generate_position() -> None:
    yaml_content = "key: value"
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert isinstance(result, IndexedDict)
    key_pos = result.get_key_position("key")
    assert isinstance(key_pos, Position)
    assert key_pos.start.line == 1
    assert key_pos.start.column == 1
    assert key_pos.end.line == 1
    assert key_pos.end.column == 4


def test_block_mapping_children_structure() -> None:
    yaml_content = """
key1: value1
invalid:
  - not a colon
key2: value2
"""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert isinstance(result, IndexedDict)

    assert len(result) == 3
    assert result["key1"] == "value1"
    assert isinstance(result["invalid"], IndexedList)
    assert result["key2"] == "value2"


def test_flow_mapping() -> None:
    yaml_content = """
mapping: {key1: value1, key2: value2}
"""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert isinstance(result, IndexedDict)
    flow_map = result["mapping"]
    assert isinstance(flow_map, IndexedDict)
    assert len(flow_map) == 2
    assert flow_map["key1"] == "value1"
    assert flow_map["key2"] == "value2"


def test_boolean_scalar_empty() -> None:
    yaml_content = """
empty_bool:
non_empty_bool: true
"""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert isinstance(result, IndexedDict)
    assert result["empty_bool"] is None
    assert result["non_empty_bool"] is True


def test_float_scalar_formats() -> None:
    yaml_content = """
standard: 3.14
no_decimal: 42.
scientific: 1.23e-4
"""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert isinstance(result, IndexedDict)
    assert result["standard"] == 3.14
    assert result["no_decimal"] == 42.0
    assert result["scientific"] == 0.000123


def test_block_scalar_markers() -> None:
    yaml_content = """
folded: >
  Line1
  Line2
  Line3

literal: |
  Line1
  Line2
  Line3
"""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert isinstance(result, IndexedDict)
    assert result["folded"] == "Line1 Line2 Line3"
    literal_value = result["literal"]
    assert isinstance(literal_value, str)
    assert literal_value.rstrip() == "Line1\nLine2\nLine3"


def test_scalar_types() -> None:
    yaml_content = """
plain: plain text
string: "quoted text"
single: 'single quoted'
empty: ""
"""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert isinstance(result, IndexedDict)
    assert result["plain"] == "plain text"
    assert result["string"] == "quoted text"
    assert result["single"] == "single quoted"
    assert result["empty"] == ""


def test_empty_document() -> None:
    yaml_content = ""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert result is None


def test_unexpected_node() -> None:
    yaml_content = "!!invalid tag"
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert result is None


def test_document_structure() -> None:
    yaml_content = """
# Valid document
---
key: value
...
---
key2: value2
"""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert result is None


def test_boolean_empty_node() -> None:
    yaml_content = """
empty_bool:
bool_with_text: true
"""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert isinstance(result, IndexedDict)
    assert result["empty_bool"] is None


def test_integer_invalid_formats() -> None:
    yaml_content = """
valid_hex: 0xFF
invalid_hex: 0xZZ
decimal: 42_000
binary: 0b1010
octal: 0o777
"""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert result is None


def test_flow_sequence_errors() -> None:
    yaml_content = """
valid: [item1, [nested, items], {key: value}]
invalid: [missing, comma invalid, item]
"""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert isinstance(result, IndexedDict)
    valid_seq = result["valid"]
    assert isinstance(valid_seq, IndexedList)
    assert len(valid_seq) == 3
    assert isinstance(valid_seq[1], IndexedList)
    assert isinstance(valid_seq[2], IndexedDict)


def test_float_edge_cases() -> None:
    yaml_content = """
empty:
nan: .nan
inf: .inf
neg_inf: -.inf
implicit_float: 1.
explicit_float: 1.0e+10
"""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert isinstance(result, IndexedDict)
    assert result["empty"] is None
    assert isinstance(result["nan"], float)
    assert isinstance(result["inf"], float)
    assert isinstance(result["neg_inf"], float)
    assert result["implicit_float"] == 1.0
    assert result["explicit_float"] == 1.0e10


def test_block_scalar_indentation() -> None:
    yaml_content = """
folded_indented: >2
  First line
    Indented line
  Last line

literal_indented: |2
  First line
    Indented line
  Last line
"""
    result = parse_yaml_with_tree_sitter(yaml_content)
    assert isinstance(result, IndexedDict)
    assert isinstance(result["folded_indented"], str)
    value = result["literal_indented"]
    assert isinstance(value, str)


def test_malformed_documents() -> None:
    yaml_contents = [
        """---
doc1: value1
---
doc2: value2
""",
        """--
key: value
""",
        """---
...
""",
        """!tag
key: value
""",
    ]
    for content in yaml_contents:
        result = parse_yaml_with_tree_sitter(content)
        assert not result


def test_handle_node_unknown_type() -> None:
    class MockNode:
        @property
        def type(self) -> str:
            return "unknown_node_type"

    node = MockNode()
    with raises(UnexpectedNodeError) as exc_info:
        handle_node(cast(Node, node))
    assert str(exc_info.value) == "Unexpected node type unknown_node_type"


def test_handle_node_result() -> None:
    class MockNode:
        @property
        def type(self) -> str:
            return "test_node"

    mock_node = MockNode()
    result = (cast(Node, mock_node), "test_value")
    node, value = _handle_node_result(result)
    assert node is mock_node
    assert value == "test_value"

    test_exception = ValueError("test error")
    result_with_error = (cast(Node, mock_node), test_exception)
    with raises(ValueError) as exc_info:
        _handle_node_result(result_with_error)
    assert str(exc_info.value) == "test error"


def test_flow_mapping_invalid_pair_children() -> None:
    yaml_content = "{key1: value1, key2:}"
    parser_language = TLanguage(tree_sitter_yaml.language())
    parser = Parser(parser_language)
    result = parser.parse(yaml_content.encode("utf-8"))

    document_node = result.root_node.children[0]
    block_node = document_node.children[0]
    flow_mapping_node = block_node.children[0]

    with raises(UnexpectedNodeError) as exc_info:
        _handle_flow_mapping_node(flow_mapping_node)
    assert str(exc_info.value) == "Unexpected node type flow_pair with value key2:"


def test_block_mapping_non_string_key() -> None:
    yaml_content = """
key1: value1
42: value2
key3: value3
"""
    parser_language = TLanguage(tree_sitter_yaml.language())
    parser = Parser(parser_language)
    result = parser.parse(yaml_content.encode("utf-8"))

    document_node = result.root_node.children[0]
    block_node = document_node.children[0]
    block_mapping_node = block_node.children[0]

    _, data = _handle_block_mapping_node(block_mapping_node)
    assert isinstance(data, IndexedDict)
    assert len(data) == 2
    assert "key1" in data
    assert "key3" in data
    assert data["key1"] == "value1"
    assert data["key3"] == "value3"
    assert "42" not in data


def test_flow_mapping_non_string_key() -> None:
    yaml_content = "{str_key: value1, 42: value2, another_key: value3}"
    parser_language = TLanguage(tree_sitter_yaml.language())
    parser = Parser(parser_language)
    result = parser.parse(yaml_content.encode("utf-8"))

    document_node = result.root_node.children[0]
    block_node = document_node.children[0]
    flow_mapping_node = block_node.children[0]

    _, data = _handle_flow_mapping_node(flow_mapping_node)
    assert isinstance(data, IndexedDict)
    assert len(data) == 2
    assert "str_key" in data
    assert "another_key" in data
    assert data["str_key"] == "value1"
    assert data["another_key"] == "value3"
    assert "42" not in data


def test_block_sequence_invalid_child_type() -> None:
    yaml_content = """---
sequence:
  - valid_item
  invalid_item
  - another_valid_item
"""
    parser_language = TLanguage(tree_sitter_yaml.language())
    parser = Parser(parser_language)
    result = parser.parse(yaml_content.encode("utf-8"))

    error_node = next(child for child in result.root_node.children if child.type == "ERROR")

    with raises(UnexpectedNodeTypeError) as exc_info:
        _handle_block_sequence_node(error_node)
    assert str(exc_info.value) == "Unexpected node type - for block_sequence_item"


def test_block_sequence_item_invalid_structure() -> None:
    yaml_content = """---
sequence:
  - item1
  - item2, item3
"""
    parser_language = TLanguage(tree_sitter_yaml.language())
    parser = Parser(parser_language)
    result = parser.parse(yaml_content.encode("utf-8"))

    document_node = result.root_node.children[0]
    block_node = next(child for child in document_node.children if child.type == "block_node")
    block_mapping_node = next(
        child for child in block_node.children if child.type == "block_mapping"
    )
    block_mapping_pair = next(
        child for child in block_mapping_node.children if child.type == "block_mapping_pair"
    )

    sequence_node = block_mapping_pair.children[2]

    invalid_node = next(
        child
        for child in sequence_node.children
        if child.type not in {"block_sequence_item", "comment"}
    )

    with raises(UnexpectedNodeTypeError) as exc_info:
        _handle_block_sequence_item(invalid_node)
    assert str(exc_info.value) == f"Unexpected node type {invalid_node.type}"


def test_flow_sequence_invalid_node_type() -> None:
    yaml_content = """
sequence: [item1, invalid_node, item3]
"""
    parser_language = TLanguage(tree_sitter_yaml.language())
    parser = Parser(parser_language)
    result = parser.parse(yaml_content.encode("utf-8"))

    document_node = result.root_node.children[0]
    block_node = next(child for child in document_node.children if child.type == "block_node")
    block_mapping_node = next(
        child for child in block_node.children if child.type == "block_mapping"
    )
    block_mapping_pair = next(
        child for child in block_mapping_node.children if child.type == "block_mapping_pair"
    )

    flow_sequence_node = block_mapping_pair.children[2]

    with raises(UnexpectedNodeTypeError) as exc_info:
        _handle_flow_sequence_node(flow_sequence_node)
    assert str(exc_info.value) == "Unexpected node type flow_sequence for flow_node"


def test_float_scalar_invalid_value() -> None:
    yaml_content = """
invalid_float: not_a_number
"""
    parser_language = TLanguage(tree_sitter_yaml.language())
    parser = Parser(parser_language)
    result = parser.parse(yaml_content.encode("utf-8"))

    document_node = result.root_node.children[0]
    block_node = next(child for child in document_node.children if child.type == "block_node")
    block_mapping_node = next(
        child for child in block_node.children if child.type == "block_mapping"
    )
    block_mapping_pair = next(
        child for child in block_mapping_node.children if child.type == "block_mapping_pair"
    )

    float_node = block_mapping_pair.children[2]

    with raises(ValueError) as exc_info:
        _handle_float_scalar_node(float_node)
    assert str(exc_info.value) == "Invalid float value: not_a_number"


def test_block_node_too_many_children() -> None:
    class MockNode:
        @property
        def type(self) -> str:
            return "block_node"

        @property
        def children(self) -> list[Node]:
            return [cast(Node, MockNode()), cast(Node, MockNode())]

    mock_node = cast(Node, MockNode())
    with raises(UnexpectedChildrenLengthError) as exc_info:
        _handle_block_node(mock_node)
    assert str(exc_info.value) == "Unexpected node type block_node for 1 children"


def test_flow_node_too_many_children() -> None:
    class MockNode:
        @property
        def type(self) -> str:
            return "flow_node"

        @property
        def children(self) -> list[Node]:
            return [cast(Node, MockNode()), cast(Node, MockNode())]

    mock_node = cast(Node, MockNode())
    with raises(UnexpectedChildrenLengthError) as exc_info:
        _handle_flow_node(mock_node)
    assert str(exc_info.value) == "Unexpected node type flow_node for 1 children"


def test_plain_scalar_too_many_children() -> None:
    class MockNode:
        @property
        def type(self) -> str:
            return "plain_scalar"

        @property
        def children(self) -> list[Node]:
            return [cast(Node, MockNode()), cast(Node, MockNode())]

    mock_node = cast(Node, MockNode())
    with raises(UnexpectedChildrenLengthError) as exc_info:
        from labels.parsers.collection.yaml import _handle_plain_scalar

        _handle_plain_scalar(mock_node)
    assert str(exc_info.value) == "Unexpected node type plain_scalar for 1 children"


def test_handle_node_with_cause() -> None:
    class MockNode:
        @property
        def type(self) -> str:
            return "string_scalar"

        @property
        def text(self) -> bytes:
            error_msg = "Error al decodificar texto"
            raise RuntimeError(error_msg)

    mock_node = cast(Node, MockNode())
    with raises(UnexpectedNodeError) as exc_info:
        handle_node(mock_node)
    assert str(exc_info.value) == "Unexpected node type string_scalar"
    assert isinstance(exc_info.value.__cause__, RuntimeError)
    assert str(exc_info.value.__cause__) == "Error al decodificar texto"


def test_block_mapping_ignores_non_pair_nodes() -> None:
    yaml_content = """
key1: value1
# This is a comment
key2: value2
"""
    parser_language = TLanguage(tree_sitter_yaml.language())
    parser = Parser(parser_language)
    result = parser.parse(yaml_content.encode("utf-8"))

    document_node = result.root_node.children[0]
    block_node = next(child for child in document_node.children if child.type == "block_node")
    block_mapping_node = next(
        child for child in block_node.children if child.type == "block_mapping"
    )

    _, data = _handle_block_mapping_node(block_mapping_node)
    assert isinstance(data, IndexedDict)
    assert len(data) == 2
    assert "key1" in data
    assert "key2" in data
    assert data["key1"] == "value1"
    assert data["key2"] == "value2"
