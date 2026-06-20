"""Agent State — defines LangGraph state schema for the debugging workflow.

Defines the AgentState TypedDict that flows through all agent nodes,
plus re-exports the Suspect dataclass and TokenMetrics for node usage.

## Contract (AgentServiceInterface)

| Component | Type | Phase |
|---|---|---|
| `AgentState` | TypedDict | P4 |
| `Suspect` | dataclass | P4 |

Implementation: **Phase 4** (T4.07)
"""

from __future__ import annotations

from typing import Any, TypedDict

from ex04.shared.types_metrics import TokenMetrics
from ex04.shared.types_results import Suspect


class AgentState(TypedDict, total=False):
    """LangGraph state for the bug investigation workflow.

    This TypedDict flows through all agent nodes. Each node reads
    relevant fields and returns updates via standard LangGraph reduction
    operators (e.g. `operator.add` for lists, last-write-wins for strings).

    Attributes:
        bug_report: The original bug description provided by the user.
        graph_context: Summary of the code graph structure.
        vault_context: Relevant vault notes and navigation results.
        suspects: Ranked list of suspect code locations.
        inspected_code: Code snippets fetched during inspection.
        root_cause: Identified root cause of the bug.
        proposed_fix: Suggested code fix to resolve the bug.
        fix_applied: Whether the proposed fix was successfully applied.
        test_results: Dictionary of test execution results.
        token_usage: Token metrics accumulated during the investigation.
    """

    bug_report: str
    graph_context: str
    vault_context: str
    suspects: list[Suspect]
    inspected_code: str
    root_cause: str
    proposed_fix: str
    fix_applied: bool
    test_results: dict[str, Any]
    token_usage: TokenMetrics
