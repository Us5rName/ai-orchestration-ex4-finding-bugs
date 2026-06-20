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
        assert cli.main(["compare", "/path", "boom"]) == 0
    sdk.compare_target.assert_called_once_with("/path", "boom")


def test_compare_does_not_call_run_comparison_directly() -> None:
    """CLI compare must delegate through compare_target, not run_comparison."""
    sdk = MagicMock()
    with _patch_sdk(sdk):
        cli.main(["compare", "/path", "boom"])
    sdk.run_comparison.assert_not_called()


def test_compare_at_file_bug_report(tmp_path: Path) -> None:
    report = tmp_path / "bug.txt"
    report.write_text("file bug", encoding="utf-8")
    sdk = MagicMock()
    with _patch_sdk(sdk):
        assert cli.main(["compare", "/path", f"@{report}"]) == 0
    sdk.compare_target.assert_called_once_with("/path", "file bug")


def test_compare_passes_target_path(tmp_path: Path) -> None:
    """CLI must forward target_path to compare_target unchanged."""
    sdk = MagicMock()
    with _patch_sdk(sdk):
        cli.main(["compare", str(tmp_path), "crash"])
    sdk.compare_target.assert_called_once_with(str(tmp_path), "crash")


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


def test_help_lists_new_subcommands(capsys: pytest.CaptureFixture[str]) -> None:
    """investigate-naive and investigate-graph must appear in help output."""
    with pytest.raises(SystemExit):
        cli.main(["--help"])
    out = capsys.readouterr().out
    assert "investigate-naive" in out
    assert "investigate-graph" in out


def test_investigate_naive_calls_sdk_method() -> None:
    """investigate-naive must delegate to sdk.run_naive_investigation, not re-implement."""
    sdk = MagicMock()
    with _patch_sdk(sdk):
        rc = cli.main(["investigate-naive", "the bug"])
    assert rc == 0
    sdk.run_naive_investigation.assert_called_once()
    sdk.run_comparison.assert_not_called()
    sdk.investigate_bug.assert_not_called()


def test_investigate_graph_calls_sdk_method() -> None:
    """investigate-graph must delegate to sdk.run_graph_investigation, not re-implement."""
    sdk = MagicMock()
    with _patch_sdk(sdk):
        rc = cli.main(["investigate-graph", "the bug"])
    assert rc == 0
    sdk.run_graph_investigation.assert_called_once()
    sdk.run_comparison.assert_not_called()
    sdk.investigate_bug.assert_not_called()


def test_investigate_naive_passes_bug_report() -> None:
    """ComparisonRequest.bug_report must match the CLI argument."""
    sdk = MagicMock()
    with _patch_sdk(sdk):
        cli.main(["investigate-naive", "null ptr crash"])
    req = sdk.run_naive_investigation.call_args[0][0]
    assert req.bug_report == "null ptr crash"


def test_investigate_naive_custom_run_id() -> None:
    """--run-id flag must be forwarded to ComparisonRequest."""
    sdk = MagicMock()
    with _patch_sdk(sdk):
        cli.main(["investigate-naive", "bug", "--run-id", "myrun42"])
    req = sdk.run_naive_investigation.call_args[0][0]
    assert req.run_id == "myrun42"


def test_investigate_naive_no_logic_duplication() -> None:
    """SDK method must be called exactly once; CLI adds no investigation logic."""
    sdk = MagicMock()
    with _patch_sdk(sdk):
        cli.main(["investigate-naive", "some bug"])
    assert sdk.run_naive_investigation.call_count == 1
