"""Phase 7 graph snapshot regression tests."""

from pathlib import Path

from ex04.services.graph.parser import GraphParser

GRAPH_ROOT = Path("graph-home/graphify-out")
TARGET_ROOT = Path("graph-home/.graphify/repos/andela/buggy-python")


def test_phase7_graph_snapshot_is_parseable() -> None:
    """Committed Phase 7 graph output must parse into non-empty graph data."""
    graph_data = GraphParser().parse(GRAPH_ROOT / "graph.json")

    assert len(graph_data.entities) >= 10
    assert len(graph_data.relationships) >= 5
    assert len(graph_data.communities) >= 1


def test_phase7_graph_report_and_target_are_present() -> None:
    """Phase 7 graph evidence must include the report and target source."""
    assert (GRAPH_ROOT / "GRAPH_REPORT.md").is_file()
    assert (TARGET_ROOT / "snippets" / "__init__.py").is_file()
    assert (TARGET_ROOT / "main.py").is_file()
