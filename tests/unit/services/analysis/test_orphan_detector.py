"""Tests for OrphanDetector — EXT-1 (FR-7.5).

All tests are deterministic and keyless.
Traceability: [PRD-EXT §EXT-1], [TODO T7.07]
"""

from __future__ import annotations

from ex04.services.analysis.orphan_detector import OrphanDetector
from ex04.shared.types import Entity, GraphData, Relationship


def _make_graph() -> GraphData:
    """Sample graph with known topology for deterministic tests."""
    entities = [
        Entity("A", "class", "a.py", (1, 10)),
        Entity("B", "class", "b.py", (1, 5)),
        Entity("C", "function", "c.py", (1, 3)),
        Entity("D", "function", "d.py", (1, 2)),
    ]
    relationships = [
        Relationship("A", "B", "calls"),
        Relationship("A", "C", "calls"),
        Relationship("B", "C", "imports"),
    ]
    return GraphData(entities=entities, relationships=relationships)


def test_empty_graph_returns_limitation() -> None:
    """Empty graph returns report with limitations."""
    detector = OrphanDetector()
    report = detector.detect(GraphData())
    assert report.orphan_count == 0
    assert any("empty" in lim.lower() for lim in report.limitations)


def test_isolated_node_detected() -> None:
    """Node with no connections is detected as orphan when threshold=0."""
    graph = _make_graph()
    detector = OrphanDetector()
    report = detector.detect(graph, min_connections=0)
    orphan_names = {n.name for n in report.orphan_nodes}
    assert "D" in orphan_names


def test_threshold_includes_low_degree_nodes() -> None:
    """threshold=1 includes nodes with degree ≤ 1."""
    graph = _make_graph()
    detector = OrphanDetector()
    report = detector.detect(graph, min_connections=1)
    orphan_names = {n.name for n in report.orphan_nodes}
    assert "D" in orphan_names


def test_high_degree_nodes_excluded() -> None:
    """High-degree nodes (A, B, C) are not orphans at threshold=0."""
    graph = _make_graph()
    detector = OrphanDetector()
    report = detector.detect(graph, min_connections=0)
    orphan_names = {n.name for n in report.orphan_nodes}
    assert "A" not in orphan_names
    assert "B" not in orphan_names


def test_source_anchors_populated() -> None:
    """Orphan nodes with file_path get populated source anchors."""
    graph = GraphData(entities=[Entity("X", "class", "x.py", (5, 20))])
    detector = OrphanDetector()
    report = detector.detect(graph)
    assert report.orphan_nodes[0].source_anchor == "x.py:5-20"


def test_total_entities_count() -> None:
    """total_entities matches number of entities in graph_data."""
    graph = _make_graph()
    report = OrphanDetector().detect(graph)
    assert report.total_entities == 4


def test_weak_components_detected() -> None:
    """D is isolated → appears in weak components."""
    graph = _make_graph()
    report = OrphanDetector().detect(graph)
    all_members = [m for wc in report.weak_components for m in wc.members]
    assert "D" in all_members


def test_limitations_include_disclaimer() -> None:
    """Report includes disclaimer about low connectivity not implying defect."""
    graph = _make_graph()
    report = OrphanDetector().detect(graph)
    assert any("not imply" in lim.lower() for lim in report.limitations)


def test_evidence_class() -> None:
    """OrphanReport evidence_class is deterministic_keyless_evidence."""
    report = OrphanDetector().detect(GraphData())
    assert report.evidence_class == "deterministic_keyless_evidence"
