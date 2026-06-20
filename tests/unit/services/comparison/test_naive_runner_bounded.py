"""Tests for bounded NaiveRunner — structured JSON output, budget enforcement.

Success requires valid JSON output with required keys and at least one
confirmed source anchor. Phrase/keyword matching is NOT tested here because
it is NOT used for success determination.

Traceability: [TODO P6-R03-REV], [Correction #3]
"""

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
        p = tmp / f"module_{i}.py"
        p.write_text("x = 1\n" * (size // 6 + 1))
        files.append(p)
    return files


def _valid_json(files: list[str] | None = None) -> str:
    first = (files or ["module_0.py"])[0]
    return json.dumps({
        "root_cause": "off-by-one in loop",
        "suspected_files": files or ["module_0.py"],
        "suspected_symbols": ["process_data"],
        "confidence": "high",
        "evidence": [{
            "file": first, "line_start": 1, "line_end": 1,
            "symbol": "process_data", "reason": "reported failure location",
        }],
    })


def test_max_files_enforced() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        files = _make_files(tmp, 10)
        runner = NaiveRunner(_make_gatekeeper(), max_files=3)
        result = runner.run("IndexError in process_data", files)
    assert result.files_read <= 3


def test_max_bytes_enforced() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        files = _make_files(tmp, 5, size=500)
        runner = NaiveRunner(_make_gatekeeper(), max_files=20, max_bytes=300)
        result = runner.run("IndexError in process_data", files)
    assert result.files_read <= 1


def test_invalid_json_sets_parser_failed() -> None:
    gk = _make_gatekeeper("I am not sure what the problem is.")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        files = _make_files(tmp, 2)
        result = NaiveRunner(gk).run("bug report", files)
    assert result.parser_status == "parse_failed"


def test_empty_response_sets_parser_empty() -> None:
    gk = _make_gatekeeper("")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        files = _make_files(tmp, 1)
        result = NaiveRunner(gk).run("bug", files)
    assert result.parser_status == "empty"


def test_valid_json_with_valid_anchor_sets_parser_ok() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        src = tmp / "module_0.py"
        src.write_text("def process_data(): pass\n")
        gk = _make_gatekeeper(_valid_json(["module_0.py"]))
        result = NaiveRunner(gk).run("IndexError bug", [src])
    assert result.parser_status == "parsed_ok"
    assert result.root_cause == "off-by-one in loop"


def test_valid_json_missing_keys_sets_parser_failed() -> None:
    bad_json = json.dumps({"root_cause": "x"})  # missing suspected_files, suspected_symbols
    gk = _make_gatekeeper(bad_json)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        files = _make_files(tmp, 1)
        result = NaiveRunner(gk).run("bug", files)
    assert result.parser_status == "parse_failed"


def test_invalid_anchor_records_limitation() -> None:
    """Suspected file not in corpus → limitation recorded."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        src = tmp / "real_module.py"
        src.write_text("pass\n")
        gk = _make_gatekeeper(_valid_json(["nonexistent.py"]))
        result = NaiveRunner(gk).run("bug", [src])
    assert any("nonexistent.py" in lim for lim in result.limitations)


def test_empty_source_list_does_not_crash() -> None:
    gk = _make_gatekeeper(_valid_json([]))
    result = NaiveRunner(gk).run("bug", [])
    assert isinstance(result, InvestigationResult)
    assert result.files_read == 0


def test_all_budget_counters_populated() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        files = _make_files(tmp, 3)
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
    gk = _make_gatekeeper("")
    result = NaiveRunner(gk).run("bug", [])
    assert isinstance(result, InvestigationResult)


@pytest.mark.parametrize("text,expected_status", [
    (json.dumps({
        "root_cause": "x", "suspected_files": ["f.py"], "suspected_symbols": ["g"],
        "confidence": "low",
        "evidence": [{"file": "f.py", "line_start": 1, "line_end": 1,
                      "symbol": "g", "reason": "anchor"}],
    }), "parsed_ok"),
    ("not json at all", "parse_failed"),
    ('{"root_cause":"x"}', "parse_failed"),
    ("", "empty"),
])
def test_parse_json_response_variants(text: str, expected_status: str) -> None:
    status, _ = _parse_json_response(text)
    assert status == expected_status
