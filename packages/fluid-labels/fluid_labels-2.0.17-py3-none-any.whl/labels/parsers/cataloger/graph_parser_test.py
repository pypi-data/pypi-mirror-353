import ctypes
from unittest.mock import MagicMock, patch

from tree_sitter import Node

from labels.parsers.cataloger import graph_parser
from labels.parsers.cataloger.graph_parser import ParsingError, adj, lang_from_so, parse_ast_graph
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.pytest_marks import parametrize_sync
from labels.testing.utils.pytest_methods import raises


def test_lang_from_so_fails_when_language_ptr_is_none() -> None:
    language = "test_language"
    mock_lib = MagicMock()
    mock_lib.tree_sitter_test_language = MagicMock(
        return_value=ctypes.c_void_p(None),
        restype=ctypes.c_void_p,
    )

    with patch("ctypes.cdll.LoadLibrary", return_value=mock_lib):
        with raises(ValueError) as exc_info:
            lang_from_so(language)

        assert str(exc_info.value) == f"Failed to load language: {language}"


@parametrize_sync(
    args=["node", "expected_error"],
    cases=[
        [MagicMock(spec=object), ParsingError],
        [MagicMock(spec=Node, has_error=True), ParsingError],
    ],
)
def test_validate_node_raises_parsing_error(
    node: object,
    expected_error: type[Exception],
) -> None:
    with raises(expected_error):
        if not isinstance(node, Node) or node.has_error:
            raise ParsingError


@mocks(
    mocks=[
        Mock(
            module=graph_parser,
            target="parse_content",
            target_type="function",
            expected=MagicMock(
                return_value=MagicMock(
                    root_node=MagicMock(spec=Node, has_error=True),
                ),
            ),
        ),
    ],
)
async def test_parse_ast_graph_returns_none_on_parsing_error() -> None:
    result = parse_ast_graph(b"invalid content", "python")
    assert result is None


def test_adj_returns_empty_tuple_when_depth_is_zero() -> None:
    graph = graph_parser.Graph()
    graph.add_node("1")
    graph.add_node("2")
    graph.add_edge("1", "2")

    result = adj(graph, "1", depth=0)
    assert result == ()
