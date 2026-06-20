"""Tests for bounded NaiveRunner navigation and budget enforcement."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ex04.services.comparison.naive_runner import NaiveRunner, _response_indicates_finding
from ex04.shared.types import RunMetrics


def _make_gatekeeper(response_text: str = "root cause: off-by-one") -> MagicMock:
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
        # Each file is ~500 bytes; limit is 300 bytes → only 0 or 1 file
        files = _make_files(tmp, 5, size=500)
        runner = NaiveRunner(_make_gatekeeper(), max_files=20, max_bytes=300)
        result = runner.run("IndexError in process_data", files)
    assert result.files_read <= 1


def test_non_indicator_response_is_not_success() -> None:
    gk = _make_gatekeeper("I am not sure what the problem is.")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        files = _make_files(tmp, 2)
        runner = NaiveRunner(gk, max_files=5)
        result = runner.run("bug report", files)
    assert result.found_root_cause is False


def test_indicator_response_is_success() -> None:
    gk = _make_gatekeeper("root cause: missing bounds check at line 14")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        files = _make_files(tmp, 2)
        runner = NaiveRunner(gk, max_files=5)
        result = runner.run("IndexError bug", files)
    assert result.found_root_cause is True


def test_empty_source_list_does_not_crash() -> None:
    gk = _make_gatekeeper("root cause found")
    runner = NaiveRunner(gk)
    result = runner.run("bug", [])
    assert isinstance(result, RunMetrics)
    assert result.files_read == 0


@pytest.mark.parametrize(
    "text,expected",
    [
        ("root cause: off-by-one", True),
        ("fix: add guard clause", True),
        ("IndexError on line 14", True),
        ("Traceback (most recent call last)", True),
        ("I cannot determine the issue", False),
        ("", False),
    ],
)
def test_response_indicator_patterns(text: str, expected: bool) -> None:
    assert _response_indicates_finding(text) == expected
