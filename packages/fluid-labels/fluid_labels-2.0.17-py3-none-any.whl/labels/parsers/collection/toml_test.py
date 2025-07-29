import logging
from unittest.mock import MagicMock, patch

import pytest

import labels.parsers.collection.toml
from labels.model.indexables import IndexedDict, ParsedValue
from labels.parsers.collection.toml import (
    _nested_dict_handle_list,
    _nested_list,
    _process_node,
    handle_array,
    handle_float,
    handle_inline_table,
    handle_integer,
    handle_node,
    handle_pair,
    handle_quoted_key,
    handle_table,
    handle_table_array_element,
    nested_dict,
    nested_list,
    parse_toml_with_tree_sitter,
)
from labels.testing.mocks import Mock, mocks
from labels.testing.utils.pytest_marks import parametrize_sync
from labels.testing.utils.pytest_methods import raises
from labels.utils.exceptions import InvalidTypeError, UnexpectedNodeError


def test_key_value_pair() -> None:
    value_str = """
key = "value"
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {"key": "value"}


def test_unspecified_value(caplog: pytest.LogCaptureFixture) -> None:
    value_str = """
key = # INVALID
    """
    with caplog.at_level(logging.ERROR):
        result = parse_toml_with_tree_sitter(value_str)

    assert "Unexpected node type ERROR with value key =" in caplog.text
    assert result is not None


def test_keys() -> None:
    value_str = """
key = "value"
bare_key = "value"
bare-key = "value"
1234 = "value"
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {
        "key": "value",
        "bare_key": "value",
        "bare-key": "value",
        "1234": "value",
    }


def test_quoted_keys() -> None:
    value_str = """
"127.0.0.1" = "value"
"character encoding" = "value"
"ʎǝʞ" = "value"
'key2' = "value"
'quoted "value"' = "value"
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {
        "127.0.0.1": "value",
        "character encoding": "value",
        "ʎǝʞ": "value",
        "key2": "value",
        'quoted "value"': "value",
    }


def test_unspecified_key(caplog: pytest.LogCaptureFixture) -> None:
    value_str = """
= "no key name"  # INVALID
"" = "blank"     # VALID but discouraged
    """
    with caplog.at_level(logging.ERROR):
        result = parse_toml_with_tree_sitter(value_str)

    assert 'Unexpected node type ERROR with value = "no key name"' in caplog.text
    assert result is not None


def test_dotted_keys() -> None:
    value_str = """
name = "Orange"
physical.color = "orange"
physical.shape = "round"
site."google.com" = true
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {
        "name": "Orange",
        "physical": {"color": "orange", "shape": "round"},
        "site": {"google.com": True},
    }


def test_dotted_keys_with_space_in_keys() -> None:
    value_str = """
fruit.name = "banana"     # this is best practice
fruit. color = "yellow"    # same as fruit.color
fruit . flavor = "banana"   # same as fruit.flavor
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {"fruit": {"name": "banana", "color": "yellow", "flavor": "banana"}}


def test_key_multiple_times(caplog: pytest.LogCaptureFixture) -> None:
    value_str = """
# DO NOT DO THIS
name = "Tom"
name = "Pradyun"
"""
    with caplog.at_level(logging.ERROR):
        result = parse_toml_with_tree_sitter(value_str)

    assert "Defining a key multiple times is invalid: name" in caplog.text
    assert result is not None


def test_key_multiple_times_1(caplog: pytest.LogCaptureFixture) -> None:
    value_str = """
# THIS WILL NOT WORK
spelling = "favorite"
"spelling" = "favourite"
"""
    with caplog.at_level(logging.ERROR):
        result = parse_toml_with_tree_sitter(value_str)

    assert "Defining a key multiple times is invalid: spelling" in caplog.text
    assert result is not None


def test_add_key_after() -> None:
    value_str = """
# This makes the key "fruit" into a table.
fruit.apple.smooth = true

# So then you can add to the table "fruit" like so:
fruit.orange = 2
"""
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {"fruit": {"apple": {"smooth": True}, "orange": 2}}


def test_define_doted_keys() -> None:
    value_str = """
apple.type = "fruit"
orange.type = "fruit"

apple.skin = "thin"
orange.skin = "thick"

apple.color = "red"
orange.color = "orange"
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {
        "apple": {"type": "fruit", "skin": "thin", "color": "red"},
        "orange": {"type": "fruit", "skin": "thick", "color": "orange"},
    }


def test_float_as_dotted_key() -> None:
    value_str = """
3.14159 = "pi"
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {"3": {"14159": "pi"}}


def test_str_unicode_charters() -> None:
    value_str = """
str = "I'm a string. \"You can quote me\". Name\tJos\u00e9\nLocation\tSF."
    """
    result = parse_toml_with_tree_sitter(value_str)
    # The result is invalid, it is the fault of the tree-sitter sintax
    assert result == {"str": "I'm a string."}


def test_str_1() -> None:
    # On a Unix system, the above multi-line string will most likely be the
    # same as:
    # str2 = "Roses are red\nViolets are blue" it mut work but the parser
    # is invalid

    # On a Windows system, it will most likely be equivalent to:
    # str3 = "Roses are red\r\nViolets are blue" it mut work but the parser
    # is invalid
    value_str = '''
str1 = """
Roses are red
Violets are blue"""
    '''
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {"str1": "Roses are red\nViolets are blue"}


def test_str_2() -> None:
    value_str = '''
# The following strings are byte-for-byte equivalent:
str1 = "The quick brown fox jumps over the lazy dog."

str2 = """
The quick brown \


  fox jumps over \
    the lazy dog."""

str3 = """\
       The quick brown \
       fox jumps over \
       the lazy dog.\
       """
    '''
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {
        "str1": "The quick brown fox jumps over the lazy dog.",
        "str2": "The quick brown \n\n  fox jumps over     the lazy dog.",
        "str3": "The quick brown        fox jumps over        the lazy dog.",
    }


def test_integer() -> None:
    value_str = """
int1 = +99
int2 = 42
int3 = 0
int4 = -17
int5 = 1_000
int6 = 5_349_221
int7 = 53_49_221  # Indian number system grouping
int8 = 1_2_3_4_5  # VALID but discouraged
# hexadecimal with prefix `0x`
hex1 = 0xDEADBEEF
hex2 = 0xdeadbeef
hex3 = 0xdead_beef

# octal with prefix `0o`
oct1 = 0o01234567
oct2 = 0o755 # useful for Unix file permissions

# binary with prefix `0b`
bin1 = 0b11010110
"""
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {
        "int1": 99,
        "int2": 42,
        "int3": 0,
        "int4": -17,
        "int5": 1000,
        "int6": 5349221,
        "int7": 5349221,
        "int8": 12345,
        "hex1": 3735928559,
        "hex2": 3735928559,
        "hex3": 3735928559,
        "oct1": 342391,
        "oct2": 493,
        "bin1": 47529918736,
    }


def test_float() -> None:
    value_str = """
# fractional
flt1 = +1.0
flt2 = 3.1415
flt3 = -0.01

# exponent
flt4 = 5e+22
flt5 = 1e06
flt6 = -2E-2

# both
flt7 = 6.626e-34

flt8 = 224_617.445_991_228
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {
        "flt1": 1.0,
        "flt2": 3.1415,
        "flt3": -0.01,
        "flt4": 5e22,
        "flt5": 1000000.0,
        "flt6": -0.02,
        "flt7": 6.626e-34,
        "flt8": 224617.445991228,
    }


@parametrize_sync(
    args=["str_value"],
    cases=[
        ["invalid_float_1 = .7"],
        ["invalid_float_2 = 7."],
        ["invalid_float_3 = 3.e+20"],
    ],
)
def test_invalid_float(str_value: str, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.ERROR):
        result = parse_toml_with_tree_sitter(str_value)

    assert f"Unexpected node type ERROR with value {str_value.strip()}" in caplog.text
    assert result is not None


def test_boolean() -> None:
    value_str = """
# true
bool1 = true

# false
bool2 = false
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {
        "bool1": True,
        "bool2": False,
    }


def test_array_1() -> None:
    value_str = """
# array of strings
arr1 = [ "foo", "bar", "baz" ]

# array of integers
arr2 = [ 1, 2, 3 ]

# array of mixed types
arr3 = [ "foo", 1, true ]

# empty array
arr4 = []
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {
        "arr1": ["foo", "bar", "baz"],
        "arr2": [1, 2, 3],
        "arr3": ["foo", 1, True],
        "arr4": [],
    }


def test_array_2() -> None:
    value_str = '''
integers = [ 1, 2, 3 ]
colors = [ "red", "yellow", "green" ]
nested_arrays_of_ints = [ [ 1, 2 ], [3, 4, 5] ]
nested_mixed_array = [ [ 1, 2 ], ["a", "b", "c"] ]
string_array = [ "all", 'strings', """are the same""", \'\'\'type\'\'\' ]

# Mixed-type arrays are allowed
numbers = [ 0.1, 0.2, 0.5, 1, 2, 5 ]
contributors = [
  "Foo Bar <foo@example.com>",
  { name = "Baz Qux", email = "bazqux@example.com"}
]
    '''
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {
        "integers": [1, 2, 3],
        "colors": ["red", "yellow", "green"],
        "nested_arrays_of_ints": [[1, 2], [3, 4, 5]],
        "nested_mixed_array": [[1, 2], ["a", "b", "c"]],
        "string_array": ["all", "strings", "are the same", "type"],
        "numbers": [0.1, 0.2, 0.5, 1, 2, 5],
        "contributors": [
            "Foo Bar <foo@example.com>",
            {"name": "Baz Qux", "email": "bazqux@example.com"},
        ],
    }


def test_table_1() -> None:
    value_str = """
[table-1]
key1 = "some string"
key2 = 123

[table-2]
key1 = "another string"
key2 = 456
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {
        "table-1": {"key1": "some string", "key2": 123},
        "table-2": {"key1": "another string", "key2": 456},
    }


def test_table_2() -> None:
    value_str = """
[dog."tater.man"]
type.name = "pug"
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {"dog": {"tater.man": {"type": {"name": "pug"}}}}


def test_table_3() -> None:
    value_str = """
[a.b.c]            # this is best practice
[ d.e.f ]          # same as [d.e.f]
[ g .  h  . i ]    # same as [g.h.i]
[ j . "ʞ" . 'l' ]  # same as [j."ʞ".'l']
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {
        "a": {"b": {"c": {}}},
        "d": {"e": {"f": {}}},
        "g": {"h": {"i": {}}},
        "j": {"ʞ": {"l": {}}},
    }


def test_table_4() -> None:
    value_str = """
# [x] you
# [x.y] don't
# [x.y.z] need these
[x.y.z.w] # for this to work

[x] # defining a super-table afterward is ok
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {"x": {}}


def test_table_5() -> None:
    value_str = """
# Top-level table begins.
name = "Fido"
breed = "pug"

# Top-level table ends.
[owner]
name = "Regina Dogman"
member_since = 1999-08-04
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {
        "name": "Fido",
        "breed": "pug",
        "owner": {
            "name": "Regina Dogman",
            "member_since": "1999-08-04",
        },
    }


def test_table_6() -> None:
    value_str = """
fruit.apple.color = "red"
# Defines a table named fruit
# Defines a table named fruit.apple

fruit.apple.taste.sweet = true
# Defines a table named fruit.apple.taste
# fruit and fruit.apple were already created
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {"fruit": {"apple": {"color": "red", "taste": {"sweet": True}}}}


def test_inline_table_1() -> None:
    value_str = """
name = { first = "Tom", last = "Preston-Werner" }
point = { x = 1, y = 2 }
animal = { type.name = "pug" }
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {
        "name": {"first": "Tom", "last": "Preston-Werner"},
        "point": {"x": 1, "y": 2},
        "animal": {"type": {"name": "pug"}},
    }


def test_array_of_tables_1() -> None:
    value_str = """
[[products]]
name = "Hammer"
sku = 738594937

[[products]]  # empty table within the array

[[products]]
name = "Nail"
sku = 284758393

color = "gray"
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {
        "products": [
            {"name": "Hammer", "sku": 738594937},
            {},
            {"name": "Nail", "sku": 284758393, "color": "gray"},
        ],
    }


def test_array_of_tables_2() -> None:
    value_str = """
[[fruits]]
name = "apple"

[fruits.physical]  # subtable
color = "red"
shape = "round"

[[fruits.varieties]]  # nested array of tables
name = "red delicious"

[[fruits.varieties]]
name = "granny smith"


[[fruits]]
name = "banana"

[[fruits.varieties]]
name = "plantain"
    """
    result = parse_toml_with_tree_sitter(value_str)
    assert result == {
        "fruits": [
            {
                "name": "apple",
                "physical": {"color": "red", "shape": "round"},
                "varieties": [
                    {"name": "red delicious"},
                    {"name": "granny smith"},
                ],
            },
            {"name": "banana", "varieties": [{"name": "plantain"}]},
        ],
    }


def test_invalid_array_table_1(caplog: pytest.LogCaptureFixture) -> None:
    value_str = """
# INVALID TOML DOC
[fruit.physical]  # subtable, but to which parent element should it belong?
color = "red"
shape = "round"

[[fruit]]  # parser must throw an error upon discovering that "fruit" is
           # an array rather than a table
name = "apple"
    """
    with caplog.at_level(logging.ERROR):
        result = parse_toml_with_tree_sitter(value_str)

    assert "'IndexedDict' object has no attribute 'append'" in caplog.text
    assert result is not None


def test_invalid_array_table_2(caplog: pytest.LogCaptureFixture) -> None:
    value_str = """
# INVALID TOML DOC
[[fruits]]
name = "apple"

[[fruits.varieties]]
name = "red delicious"

# INVALID: This table conflicts with the previous array of tables
[fruits.varieties]
name = "granny smith"
    """
    with caplog.at_level(logging.ERROR):
        result = parse_toml_with_tree_sitter(value_str)

    assert "Defining a key multiple times is invalid: varieties" in caplog.text
    assert result is not None


def test_handle_array_no_match() -> None:
    mock_node = MagicMock()
    mock_child = MagicMock()

    mock_child.type = "inline_table"
    mock_node.children = [mock_child]  # type: ignore[misc]

    with patch(
        "labels.parsers.collection.toml.handle_node",
        return_value=("valor_parseado", mock_child),
    ):
        result = handle_array(mock_node)

    assert result == []


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.collection.toml,
            target="handle_string",
            target_type="sync",
            expected="'quoted_value'",
        ),
    ],
)
async def test_handle_quoted_key() -> None:
    mock_node = MagicMock()
    mock_node.text = b'"quoted value"'

    result = handle_quoted_key(mock_node)
    assert result == "quoted_value"


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.collection.toml,
            target="handle_node",
            target_type="sync",
            expected=("bare_key_value", "bare_key_node"),
        ),
    ],
)
async def test_handle_table_array_element_with_tuple() -> None:
    mock_node = MagicMock()
    mock_bare_key = MagicMock()
    mock_node.named_children = [mock_bare_key]  # type: ignore[misc]

    result = handle_table_array_element(mock_node)
    assert result == ((None, mock_bare_key), IndexedDict(mock_node))


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.collection.toml,
            target="handle_node",
            target_type="sync",
            expected="bare_key_value",
        ),
    ],
)
async def test_handle_table_array_element_non_pair() -> None:
    mock_node = MagicMock()
    mock_bare_key = MagicMock()
    mock_child = MagicMock()
    mock_child.type = "not_pair"
    mock_node.named_children = [mock_bare_key, mock_child]  # type: ignore[misc]

    result = handle_table_array_element(mock_node)
    assert result == (("bare_key_value", mock_bare_key), IndexedDict(mock_node))


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.collection.toml,
            target="handle_node",
            target_type="sync",
            expected="bare_key_value",
        ),
    ],
)
async def test_handle_table_array_element_pair_no_conditions() -> None:
    mock_node = MagicMock()
    mock_bare_key = MagicMock()
    mock_child = MagicMock()
    mock_child.type = "pair"
    mock_node.named_children = [mock_bare_key, mock_child]  # type: ignore[misc]

    result = handle_table_array_element(mock_node)
    assert result == (("bare_key_value", mock_bare_key), IndexedDict(mock_node))


def test_handle_table_array_element_non_string_key() -> None:
    mock_node = MagicMock()
    mock_bare_key = MagicMock()
    mock_child = MagicMock()
    mock_child.type = "pair"
    mock_node.named_children = [mock_bare_key, mock_child]  # type: ignore[misc]

    side_effect = ["bare_key_value", ((123, mock_child), ("value", mock_child))]

    with patch(
        "labels.parsers.collection.toml.handle_node",
        side_effect=side_effect,
    ):
        result = handle_table_array_element(mock_node)
        assert result == (("bare_key_value", mock_bare_key), IndexedDict(mock_node))


def test_handle_pair_returns_none() -> None:
    mock_node = MagicMock()
    mock_bare_key = MagicMock()
    mock_value = MagicMock()
    mock_node.named_children = [mock_bare_key, mock_value]  # type: ignore[misc]

    side_effect = [("key", "node"), ("value", "node")]

    with patch(
        "labels.parsers.collection.toml.handle_node",
        side_effect=side_effect,
    ):
        result = handle_pair(mock_node)
        assert result == ((None, mock_bare_key), (None, mock_value))


def test_handle_integer_raises_error() -> None:
    mock_node = MagicMock()
    mock_node.text = b"invalid_number"

    with pytest.raises(ValueError, match="Invalid integer value: invalid_number"):
        handle_integer(mock_node)


def test_handle_float_raises_error() -> None:
    mock_node = MagicMock()
    mock_node.text = b"invalid_float"

    with pytest.raises(ValueError, match="Invalid float value: invalid_float"):
        handle_float(mock_node)


def test_handle_inline_table_no_tuple() -> None:
    mock_node = MagicMock()
    mock_child = MagicMock()
    mock_node.named_children = [mock_child]  # type: ignore[misc]

    with patch(
        "labels.parsers.collection.toml.handle_node",
        return_value="not_a_tuple",
    ):
        result = handle_inline_table(mock_node)
        assert result == IndexedDict(mock_node)


def test_handle_inline_table_non_string_list_key() -> None:
    mock_node = MagicMock()
    mock_child = MagicMock()
    mock_node.named_children = [mock_child]  # type: ignore[misc]

    with patch(
        "labels.parsers.collection.toml.handle_node",
        return_value=((123, mock_child), ("value", mock_child)),
    ):
        result = handle_inline_table(mock_node)
        assert result == IndexedDict(mock_node)


def test_handle_table_no_tuple() -> None:
    mock_node = MagicMock()
    mock_bare_key = MagicMock()
    mock_child = MagicMock()
    mock_node.named_children = [mock_bare_key, mock_child]  # type: ignore[misc]
    data: IndexedDict[str, ParsedValue] = IndexedDict()

    with patch(
        "labels.parsers.collection.toml.handle_node",
        return_value="data",
    ):
        handle_table(mock_node, data)
        assert data == {"data": {}}


def test_handle_table_non_string_list_key() -> None:
    mock_node = MagicMock()
    mock_bare_key = MagicMock()
    mock_child = MagicMock()
    mock_node.named_children = [mock_bare_key, mock_child]  # type: ignore[misc]
    data: IndexedDict[str, ParsedValue] = IndexedDict()

    with patch(
        "labels.parsers.collection.toml.handle_node",
        return_value=((123, mock_child), ("value", mock_child)),
    ):
        handle_table(mock_node, data)
        assert data == {}


def test_handle_node_comment() -> None:
    mock_node = MagicMock()
    mock_node.type = "comment"

    result = handle_node(mock_node)
    assert result is None


def test_handle_node_unexpected_type() -> None:
    mock_node = MagicMock()
    mock_node.type = "unexpected_type"

    with raises(UnexpectedNodeError):
        handle_node(mock_node)


def test_nested_dict_handle_list_invalid_type() -> None:
    data = "not_a_list_or_dict"

    with raises(InvalidTypeError, match="Attempted to extend non-table type"):
        _nested_dict_handle_list(data)


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.collection.toml,
            target="_nested_dict_handle_list",
            target_type="sync",
            expected="not_an_indexed_dict",
        ),
    ],
)
async def test_nested_dict_non_indexed_dict_data_result() -> None:
    mock_node = MagicMock()
    data: IndexedDict[str, ParsedValue] = IndexedDict()

    nested_dict(
        data=data,
        keys="test_key",
        keys_node=mock_node,
        value="test_value",
    )
    assert data == {}


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.collection.toml,
            target="_nested_list_handle_list",
            target_type="sync",
            expected=IndexedDict[str, ParsedValue](),
        ),
    ],
)
async def test_nested_list_data_val_is_indexed_dict() -> None:
    mock_node = MagicMock()
    data: IndexedDict[str, ParsedValue] = IndexedDict()
    nested_dict: IndexedDict[str, ParsedValue] = IndexedDict(mock_node)

    data[("test_key", mock_node)] = (nested_dict, mock_node)

    _nested_list(
        data=data,
        key="test_key",
        is_last=False,
        keys_node=mock_node,
        build_key=["test_key"],
        value="test_value",
    )
    assert data == {"test_key": {}}


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.collection.toml,
            target="_nested_list_handle_list",
            target_type="sync",
            expected="not_an_indexed_dict",
        ),
    ],
)
async def test_nested_list_data_result_is_not_indexed_dict() -> None:
    mock_node = MagicMock()
    data: IndexedDict[str, ParsedValue] = IndexedDict()

    nested_list(
        data=data,
        keys="test_key",
        keys_node=mock_node,
        value="test_value",
    )
    assert data == {}


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.collection.toml,
            target="_nested_list_handle_fists_keys",
            target_type="sync",
            expected=True,
        ),
    ],
)
async def test_nested_list_dict_value_is_indexed_dict() -> None:
    mock_node = MagicMock()
    data: IndexedDict[str, ParsedValue] = IndexedDict()

    nested_list(
        data=data,
        keys="test_key",
        keys_node=mock_node,
        value="test_value",
    )

    assert isinstance(data["test_key"], IndexedDict)
    assert data["test_key"] == {}


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.collection.toml,
            target="_nested_list_handle_list",
            target_type="sync",
            expected=IndexedDict[str, ParsedValue](),
        ),
    ],
)
async def test_nested_list_data_val_is_not_indexed_dict() -> None:
    mock_node = MagicMock()
    data: IndexedDict[str, ParsedValue] = IndexedDict()
    data[("test_key", mock_node)] = ("not_an_indexed_dict", mock_node)

    _nested_list(
        data=data,
        key="test_key",
        is_last=False,
        keys_node=mock_node,
        build_key=["test_key"],
        value="test_value",
    )
    assert data == {"test_key": "not_an_indexed_dict"}


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.collection.toml,
            target="handle_node",
            target_type="sync",
            expected="not_a_tuple",
        ),
    ],
)
async def test_process_node_not_tuple() -> None:
    mock_node = MagicMock()
    mock_node.type = "pair"
    data: IndexedDict[str, ParsedValue] = IndexedDict()

    _process_node(node=mock_node, data=data)
    assert data == {}


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.collection.toml,
            target="handle_node",
            target_type="sync",
            expected=((123, "node"), ("value", "node")),
        ),
    ],
)
async def test_process_node_key_not_str_or_list() -> None:
    mock_node = MagicMock()
    mock_node.type = "pair"
    data: IndexedDict[str, ParsedValue] = IndexedDict()

    _process_node(node=mock_node, data=data)
    assert data == {}


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.collection.toml,
            target="handle_table_array_element",
            target_type="sync",
            expected=((123, "node"), ("value", "node")),
        ),
    ],
)
async def test_process_node_table_array_key_not_str_or_list() -> None:
    mock_node = MagicMock()
    mock_node.type = "table_array_element"
    data: IndexedDict[str, ParsedValue] = IndexedDict()

    _process_node(node=mock_node, data=data)
    assert data == {}


@mocks(
    mocks=[
        Mock(
            module=labels.parsers.collection.toml,
            target="_validate_key_pairs",
            target_type="sync",
            expected=False,
        ),
    ],
)
async def test_parse_toml_invalid_key_pairs(caplog: pytest.LogCaptureFixture) -> None:
    value_str = "key = value"
    with caplog.at_level(logging.ERROR):
        result = parse_toml_with_tree_sitter(value_str)

    assert "Invalid document" in caplog.text
    assert result == IndexedDict()


def test_parse_toml_root_node_not_document() -> None:
    value_str = "invalid_content"
    with patch(
        "labels.parsers.collection.toml.Parser.parse",
        return_value=MagicMock(root_node=MagicMock(type="not_document")),
    ):
        result = parse_toml_with_tree_sitter(value_str)
        assert result == IndexedDict()
