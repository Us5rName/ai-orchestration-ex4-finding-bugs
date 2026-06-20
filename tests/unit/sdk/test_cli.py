"""Unit tests for the CLI entry point — SDK delegation, no business logic."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ex04 import __main__ as cli


def _patch_sdk(sdk: MagicMock):
    """Patch Ex04SDK.from_config to return the given mock SDK."""
    return patch.object(cli.Ex04SDK, "from_config", return_value=sdk)


def test_help_lists_commands(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        cli.main(["--help"])
    out = capsys.readouterr().out
    for cmd in ("graphify", "investigate", "compare", "pipeline"):
        assert cmd in out


def test_graphify_delegates_to_sdk() -> None:
    sdk = MagicMock()
    with _patch_sdk(sdk):
        assert cli.main(["graphify", "/path"]) == 0
    sdk.run_graphify.assert_called_once_with("/path")


def test_investigate_delegates_to_sdk() -> None:
    sdk = MagicMock()
    with _patch_sdk(sdk):
        assert cli.main(["investigate", "boom"]) == 0
    sdk.investigate_bug.assert_called_once_with("boom")


def test_compare_delegates_to_sdk() -> None:
    sdk = MagicMock()
    with _patch_sdk(sdk):
        assert cli.main(["compare", "boom"]) == 0
    sdk.run_comparison.assert_called_once_with("boom", [])


def test_pipeline_delegates_to_sdk() -> None:
    sdk = MagicMock()
    with _patch_sdk(sdk):
        assert cli.main(["pipeline", "/path", "boom"]) == 0
    sdk.full_pipeline.assert_called_once_with("/path", "boom")


def test_bug_report_from_file(tmp_path: Path) -> None:
    report = tmp_path / "bug.txt"
    report.write_text("file bug", encoding="utf-8")
    sdk = MagicMock()
    with _patch_sdk(sdk):
        assert cli.main(["investigate", f"@{report}"]) == 0
    sdk.investigate_bug.assert_called_once_with("file bug")


def test_not_implemented_returns_code_3() -> None:
    with _patch_sdk(MagicMock()) as p:
        p.side_effect = NotImplementedError("phase 4")
        assert cli.main(["graphify", "/path"]) == 3


def test_file_not_found_returns_code_2() -> None:
    with _patch_sdk(MagicMock()) as p:
        p.side_effect = FileNotFoundError("missing")
        assert cli.main(["graphify", "/path"]) == 2


def test_generic_error_returns_code_1() -> None:
    with _patch_sdk(MagicMock()) as p:
        p.side_effect = RuntimeError("kaboom")
        assert cli.main(["graphify", "/path"]) == 1
