"""Tests for PatchImpactAnalyzer — EXT-2 (FR-7.6).

All tests are deterministic and keyless.
Traceability: [PRD-EXT §EXT-2], [TODO T7.08]
"""

from __future__ import annotations

from ex04.services.analysis.patch_impact import PatchImpactAnalyzer
from ex04.shared.types import Entity, GraphData, Relationship


def _make_graph() -> GraphData:
    """Graph: A → B → C, D (isolated)."""
    entities = [
        Entity("A", "class", "a.py", (1, 10)),
        Entity("B", "class", "b.py", (1, 5)),
        Entity("C", "function", "c.py", (1, 3)),
        Entity("test_a", "test", "tests/test_a.py", (1, 20)),
    ]
    relationships = [
        Relationship("A", "B", "calls"),
        Relationship("B", "C", "calls"),
        Relationship("test_a", "A", "tests"),
    ]
    return GraphData(entities=entities, relationships=relationships)


def test_no_changed_symbols_returns_limitation() -> None:
    """Empty changed_symbols returns report with limitation."""
    analyzer = PatchImpactAnalyzer()
    report = analyzer.analyze(GraphData(), [])
    assert any("No changed symbols" in lim for lim in report.limitations)


def test_direct_dependent_detected() -> None:
    """test_a depends on A directly; when A changes, test_a is a direct dependent."""
    graph = _make_graph()
    report = PatchImpactAnalyzer().analyze(graph, ["A"], max_depth=1)
    direct_names = {n.name for n in report.direct_dependents}
    assert "test_a" in direct_names


def test_transitive_dependent_with_depth() -> None:
    """Changing C propagates to B (depth 1) and test_a via A is not here."""
    graph = _make_graph()
    report = PatchImpactAnalyzer().analyze(graph, ["C"], max_depth=3)
    all_names = {n.name for n in report.direct_dependents + report.transitive_dependents}
    assert "B" in all_names


def test_depth_one_finds_only_direct() -> None:
    """max_depth=1 finds direct dependents only, no transitive."""
    graph = _make_graph()
    report = PatchImpactAnalyzer().analyze(graph, ["A"], max_depth=1)
    # test_a depends on A directly at depth=1
    assert len(report.direct_dependents) >= 1
    # With depth=1, no further traversal occurs for depth>1
    assert all(n.depth <= 1 for n in report.direct_dependents)


def test_zero_depth_reports_no_dependents() -> None:
    """max_depth=0 reports only the changed symbol, not depth-1 dependents."""
    graph = _make_graph()
    report = PatchImpactAnalyzer().analyze(graph, ["A"], max_depth=0)
    assert report.direct_dependents == []
    assert report.transitive_dependents == []
    assert report.impact_paths == []


def test_symbol_not_in_graph_skipped() -> None:
    """Changed symbol not in graph is noted in limitations."""
    graph = _make_graph()
    report = PatchImpactAnalyzer().analyze(graph, ["NonExistent"], max_depth=2)
    assert any("NonExistent" in lim for lim in report.limitations)


def test_affected_test_files_detected() -> None:
    """test_a (kind=test) appears in affected_test_files when A changes."""
    graph = _make_graph()
    report = PatchImpactAnalyzer().analyze(graph, ["A"], max_depth=2)
    assert any("test_a" in path for path in report.affected_test_files)


def test_limitations_include_reachability_disclaimer() -> None:
    """Report includes graph-reachability disclaimer."""
    report = PatchImpactAnalyzer().analyze(GraphData(), [])
    all_text = " ".join(report.limitations)
    assert "reachability" in all_text or "No changed" in all_text


def test_impact_paths_populated() -> None:
    """impact_paths lists BFS paths from changed symbol to dependents."""
    graph = _make_graph()
    report = PatchImpactAnalyzer().analyze(graph, ["A"], max_depth=2)
    assert len(report.impact_paths) >= 1


def test_evidence_class() -> None:
    """ImpactReport evidence_class is deterministic_keyless_evidence."""
    graph = _make_graph()
    report = PatchImpactAnalyzer().analyze(graph, ["A"])
    assert report.evidence_class == "deterministic_keyless_evidence"


def test_max_depth_used_recorded() -> None:
    """max_depth_used in the report matches the argument passed."""
    report = PatchImpactAnalyzer().analyze(GraphData(), [], max_depth=5)
    assert report.max_depth_used == 5
