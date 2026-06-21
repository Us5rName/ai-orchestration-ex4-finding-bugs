"""Tests for bounded NaiveRunner structured JSON output and budgets."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ex04.services.comparison.naive_runner import NaiveRunner, _parse_json_response
from ex04.shared.types_results import InvestigationResult


def _make_gatekeeper(response_text: str = "") -> MagicMock:
    gk = MagicMock()
    resp = MagicMock()
    resp.text = response_text
    resp.input_tokens = 10
    resp.output_tokens = 5
    gk.send.return_value = resp
    return gk


def _make_files(tmp: Path, count: int, size: int = 100) -> list[Path]:
    files = []
    for i in range(count):
        path = tmp / f"module_{i}.py"
        path.write_text("x = 1\n" * (size // 6 + 1))
        files.append(path)
    return files


def _valid_json(files: list[str] | None = None) -> str:
    first = (files or ["module_0.py"])[0]
    return json.dumps(
        {
            "root_cause": "off-by-one in loop",
            "suspected_files": files or ["module_0.py"],
            "suspected_symbols": ["process_data"],
            "confidence": "high",
            "evidence": [
                {
                    "file": first,
                    "line_start": 1,
                    "line_end": 1,
                    "symbol": "process_data",
                    "reason": "reported failure location",
                }
            ],
        }
    )


def test_max_files_enforced() -> None:
    with tempfile.TemporaryDirectory() as td:
        files = _make_files(Path(td), 10)
        result = NaiveRunner(_make_gatekeeper(), max_files=3).run(
            "IndexError in process_data",
            files,
        )
    assert result.files_read <= 3


def test_max_bytes_enforced() -> None:
    with tempfile.TemporaryDirectory() as td:
        files = _make_files(Path(td), 5, size=500)
        result = NaiveRunner(_make_gatekeeper(), max_files=20, max_bytes=300).run(
            "IndexError in process_data",
            files,
        )
    assert result.files_read <= 1


def test_invalid_json_sets_parser_failed() -> None:
    gk = _make_gatekeeper("I am not sure what the problem is.")
    with tempfile.TemporaryDirectory() as td:
        result = NaiveRunner(gk).run("bug report", _make_files(Path(td), 2))
    assert result.parser_status == "parse_failed"


def test_empty_response_sets_parser_empty() -> None:
    gk = _make_gatekeeper("")
    with tempfile.TemporaryDirectory() as td:
        result = NaiveRunner(gk).run("bug", _make_files(Path(td), 1))
    assert result.parser_status == "empty"


def test_valid_json_with_valid_anchor_sets_parser_ok() -> None:
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "module_0.py"
        src.write_text("def process_data(): pass\n")
        result = NaiveRunner(_make_gatekeeper(_valid_json(["module_0.py"]))).run(
            "IndexError bug",
            [src],
        )
    assert result.parser_status == "parsed_ok"
    assert result.root_cause == "off-by-one in loop"


def test_valid_json_missing_keys_sets_parser_failed() -> None:
    gk = _make_gatekeeper(json.dumps({"root_cause": "x"}))
    with tempfile.TemporaryDirectory() as td:
        result = NaiveRunner(gk).run("bug", _make_files(Path(td), 1))
    assert result.parser_status == "parse_failed"


def test_invalid_anchor_records_limitation() -> None:
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "real_module.py"
        src.write_text("pass\n")
        gk = _make_gatekeeper(_valid_json(["nonexistent.py"]))
        result = NaiveRunner(gk).run("bug", [src])
    assert any("nonexistent.py" in lim for lim in result.limitations)


def test_empty_source_list_does_not_crash() -> None:
    result = NaiveRunner(_make_gatekeeper(_valid_json([]))).run("bug", [])
    assert isinstance(result, InvestigationResult)
    assert result.files_read == 0


def test_all_budget_counters_populated() -> None:
    with tempfile.TemporaryDirectory() as td:
        files = _make_files(Path(td), 3)
        gk = _make_gatekeeper(_valid_json(["module_0.py"]))
        result = NaiveRunner(gk).run("bug", files)
    assert result.files_read >= 1
    assert result.bytes_read >= 0
    assert result.tool_calls >= 1
    assert result.model_calls == 1
    assert result.iterations == 1
    assert result.duration_seconds >= 0.0
    assert result.input_tokens == 10
    assert result.output_tokens == 5


def test_result_is_investigation_result() -> None:
    result = NaiveRunner(_make_gatekeeper("")).run("bug", [])
    assert isinstance(result, InvestigationResult)


@pytest.mark.parametrize(
    ("text", "expected_status"),
    [
        (_valid_json(["f.py"]), "parsed_ok"),
        (f"```json\n{_valid_json(['f.py'])}\n```", "parsed_ok"),
        ("not json at all", "parse_failed"),
        ('{"root_cause":"x"}', "parse_failed"),
        ("", "empty"),
    ],
)
def test_parse_json_response_variants(text: str, expected_status: str) -> None:
    status, _ = _parse_json_response(text)
    assert status == expected_status
