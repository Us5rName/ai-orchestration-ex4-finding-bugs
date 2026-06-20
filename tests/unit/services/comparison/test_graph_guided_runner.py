"""Graph-guided runner production-path regressions."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

from ex04.services.comparison.graph_guided_runner import GraphGuidedRunner
from ex04.shared.types import Entity, GraphData, Relationship
from ex04.shared.types_request import ComparisonRequest


def _gatekeeper() -> MagicMock:
    gk = MagicMock()
    response = MagicMock()
    response.text = json.dumps({
        "root_cause": "bad branch",
        "suspected_files": ["src/a.py"],
        "suspected_symbols": ["buggy"],
        "confidence": "medium",
        "evidence": [{
            "file": "src/a.py", "line_start": 1, "line_end": 1,
            "symbol": "buggy", "reason": "graph candidate",
        }],
    })
    response.input_tokens = 11
    response.output_tokens = 7
    gk.send.return_value = response
    return gk


def _request() -> ComparisonRequest:
    return ComparisonRequest(
        bug_report="buggy branch", provider="openai", run_id="graph-r1",
        max_tool_calls=10,
    )


def test_graph_runner_uses_actual_operation_counts() -> None:
    graph = GraphData(
        entities=[Entity("buggy", "function", "src/a.py", (1, 3))],
        relationships=[Relationship("buggy", "helper", "calls")],
    )
    result = GraphGuidedRunner(_gatekeeper()).run(_request(), graph, None)
    assert result.tool_calls == 3
    assert len(result.evidence) == 1
    assert result.telemetry_available is True


def test_missing_graph_anchor_is_explicit_limitation() -> None:
    graph = GraphData(entities=[Entity("missing", "function")], relationships=[])
    result = GraphGuidedRunner(_gatekeeper()).run(_request(), graph, None)
    assert any("lacks source anchor" in item for item in result.limitations)
