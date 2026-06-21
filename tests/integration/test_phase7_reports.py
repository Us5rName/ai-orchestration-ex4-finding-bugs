"""Phase 7 report generation regression tests."""

from pathlib import Path

from ex04.phase7 import generate_phase7_reports

GRAPH = Path("graph-home/graphify-out/graph.json")
RESULT = Path("artifacts/runs/phase7-investigation/result.json")


def test_phase7_report_generator_writes_expected_files(tmp_path: Path) -> None:
    """Report generator must create diagrams, diff, root cause, and pipeline docs."""
    outputs = generate_phase7_reports(GRAPH, RESULT, tmp_path)

    assert set(outputs) == {"diagrams", "root_cause", "diff", "pipeline", "index"}
    assert "```mermaid" in outputs["diagrams"].read_text(encoding="utf-8")
    assert "```diff" in outputs["diff"].read_text(encoding="utf-8")


def test_phase7_committed_reports_are_present() -> None:
    """Committed report artifacts must include diagrams and narrative reports."""
    required = [
        Path("reports/diagrams.md"),
        Path("reports/root_cause.md"),
        Path("reports/diff_foobar.md"),
        Path("reports/pipeline.md"),
        Path("reports/README.md"),
    ]

    assert all(path.is_file() for path in required)
    assert "```mermaid" in Path("reports/diagrams.md").read_text(encoding="utf-8")
    assert "```mermaid" in Path("README.md").read_text(encoding="utf-8")
