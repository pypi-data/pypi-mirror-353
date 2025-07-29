import io
import json
import shutil
from collections.abc import Callable
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any

from deepdiff.diff import DeepDiff

from labels.core.cli import cli


def labels(args: list[str]) -> tuple[int, str, str]:
    out_buffer, err_buffer = io.StringIO(), io.StringIO()

    code: int = 0
    with redirect_stdout(out_buffer), redirect_stderr(err_buffer):
        try:
            cli(args, prog_name="labels")
        except SystemExit as exc:
            if isinstance(exc.code, int):
                code = exc.code
    try:
        return code, out_buffer.getvalue(), err_buffer.getvalue()
    finally:
        del out_buffer
        del err_buffer


def check_json_results_match(
    *,
    expected_file_path: str,
    result_file_path: str,
    excluded_fields: list[str] | None,
    custom_filter: Callable | None,
) -> None:
    __tracebackhide__ = True
    result_file = Path(result_file_path)
    expected_file = Path(expected_file_path)

    if not expected_file.exists():
        expected_file.write_text("{}", encoding="utf-8")

    with (
        result_file.open(encoding="utf-8") as pf,
        expected_file.open(encoding="utf-8") as ef,
    ):
        objt_produced = json.load(pf)
        objt_expected = json.load(ef)

    differences = DeepDiff(
        t1=objt_expected,
        t2=objt_produced,
        ignore_order=True,
        verbose_level=2,
        exclude_regex_paths=excluded_fields,
        exclude_obj_callback=custom_filter,
    )

    if differences:
        shutil.copyfile(result_file_path, expected_file_path)

    assert not differences, json.dumps(differences, indent=2)


def cleanup_file(file_path: str) -> None:
    file = Path(file_path)
    if file.exists():
        file.unlink()


def ignore_spdx_dynamic_references(obj: Any, path: str) -> bool:
    if "externalRefs" in path and isinstance(obj, dict):
        return (
            obj.get("referenceType", "").startswith("fluid-attacks:health_metadata:")
            or obj.get("referenceType") == "advisory"
        )
    return False


def ignore_cyclonedx_dynamic_properties(obj: Any, path: str) -> bool:
    if "properties" in path and isinstance(obj, dict):
        return obj.get("name", "").startswith("fluid-attacks:health_metadata:")
    return False
