from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

import phpserialize
import pytest
from pydantic_core import InitErrorDetails, ValidationError

from labels.model.file import Coordinates, Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.php.parse_serialized import parse_pecl_serialized, php_to_python
from labels.testing.utils.helpers import get_test_data_path
from labels.utils.file import new_location


def test_parse_composer_lock() -> None:
    test_data_path = get_test_data_path("dependencies/php/memcached.reg")
    expected_packages = [
        Package(
            name="memcached",
            version="3.2.0",
            locations=[
                Location(
                    coordinates=Coordinates(
                        real_path=test_data_path,
                        file_system_id=None,
                        line=None,
                    ),
                    access_path=test_data_path,
                    annotations={},
                ),
            ],
            language=Language.PHP,
            licenses=[],
            type=PackageType.PhpPeclPkg,
            metadata=None,
            p_url="pkg:pecl/memcached@3.2.0",
            dependencies=None,
            found_by=None,
            health_metadata=None,
            is_dev=False,
        ),
    ]
    with Path(test_data_path).open(encoding="utf-8") as reader:
        pkgs, _ = parse_pecl_serialized(
            None,
            None,
            LocationReadCloser(location=new_location(test_data_path), read_closer=reader),
        )
        for pkg in pkgs:
            pkg.health_metadata = None
            pkg.licenses = []
        assert pkgs == expected_packages


def test_php_to_python() -> None:
    data = b'O:8:"stdClass":2:{s:4:"name";s:4:"test";s:5:"value";i:123;}'
    php_obj = phpserialize.loads(data, decode_strings=True, object_hook=phpserialize.phpobject)
    result = php_to_python(php_obj)
    assert isinstance(result, dict)
    assert result == {"name": "test", "value": 123}

    test_dict = {
        "key1": php_obj,
        "key2": {"nested": "value"},
    }
    result = php_to_python(test_dict)
    assert isinstance(result, dict)
    assert result == {
        "key1": {"name": "test", "value": 123},
        "key2": {"nested": "value"},
    }

    test_list = [php_obj, "string", 123]
    result = php_to_python(test_list)
    assert isinstance(result, list)
    assert result == [{"name": "test", "value": 123}, "string", 123]

    assert php_to_python("test") == "test"
    assert php_to_python(123) == 123
    assert php_to_python(phpserialize.loads(b"b:1;")) is True


def test_parse_pecl_serialized_missing_fields() -> None:
    data = b'O:8:"stdClass":1:{s:7:"version";O:8:"stdClass":1:{s:7:"release";s:5:"1.0.0";}}'
    reader = LocationReadCloser(
        location=new_location("test.reg"),
        read_closer=TextIOWrapper(BytesIO(data)),
    )
    with patch(
        "phpserialize.loads",
        return_value=phpserialize.loads(
            data,
            decode_strings=True,
            object_hook=phpserialize.phpobject,
        ),
    ):
        pkgs, rels = parse_pecl_serialized(None, None, reader)
        assert pkgs == []
        assert rels == []

    # Caso 2: Sin versión
    data = b'O:8:"stdClass":1:{s:4:"name";s:4:"test";}'
    reader = LocationReadCloser(
        location=new_location("test.reg"),
        read_closer=TextIOWrapper(BytesIO(data)),
    )
    with patch(
        "phpserialize.loads",
        return_value=phpserialize.loads(
            data,
            decode_strings=True,
            object_hook=phpserialize.phpobject,
        ),
    ):
        pkgs, rels = parse_pecl_serialized(None, None, reader)
        assert pkgs == []
        assert rels == []


def test_parse_pecl_serialized_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    data = (
        b'O:8:"stdClass":2:{s:4:"name";s:4:"test";s:7:"version";'
        b'O:8:"stdClass":1:{s:7:"release";s:5:"1.0.0";}}'
    )
    reader = LocationReadCloser(
        location=new_location("test.reg"),
        read_closer=TextIOWrapper(BytesIO(data)),
    )

    with (
        patch(
            "phpserialize.loads",
            return_value=phpserialize.loads(
                data,
                decode_strings=True,
                object_hook=phpserialize.phpobject,
            ),
        ),
        patch("labels.model.package.Package.__init__") as mock_init,
    ):
        mock_init.side_effect = ValidationError.from_exception_data(
            title="",
            line_errors=[
                InitErrorDetails(
                    type="missing",
                    loc=("name",),
                    input=None,
                    ctx={},
                ),
            ],
        )

        pkgs, rels = parse_pecl_serialized(None, None, reader)
        assert pkgs == []
        assert rels == []
        assert (
            "Malformed package. Required fields are missing or data types are incorrect."
            in caplog.text
        )
