"""Phase 7 investigation regression tests."""

import json
from pathlib import Path

from ex04.phase7 import run_phase7_investigation

TARGET = Path("graph-home/.graphify/repos/andela/buggy-python")
GRAPH = Path("graph-home/graphify-out/graph.json")
VAULT = Path("obsidian")


def test_phase7_investigation_runner_applies_and_verifies_fix(tmp_path: Path) -> None:
    """Phase 7 runner executes the real agent workflow keylessly."""
    result = run_phase7_investigation(
        target_path=TARGET,
        graph_path=GRAPH,
        vault_path=VAULT,
        reports_dir=tmp_path / "reports",
        artifacts_dir=tmp_path / "artifacts",
    )

    assert result.fix_applied is True
    assert result.test_results["passed"] is True
    assert result.suspects[0].file_path == "snippets/foobar.py"
    assert "mutable default" in result.root_cause


def test_phase7_investigation_artifacts_are_committed() -> None:
    """Committed Phase 7 investigation artifacts must be present and verified."""
    report = Path("reports/bug_analysis.md")
    result_path = Path("artifacts/runs/phase7-investigation/result.json")

    assert report.is_file()
    assert "foo() stores state in a mutable default argument" in report.read_text(
        encoding="utf-8"
    )

    data = json.loads(result_path.read_text(encoding="utf-8"))
    assert data["fix_applied"] is True
    assert data["test_results"]["passed"] is True
