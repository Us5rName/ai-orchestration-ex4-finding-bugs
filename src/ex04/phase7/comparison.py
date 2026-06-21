"""Phase 7 token-comparison execution."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from ex04.phase7.gatekeeper import Phase7Gatekeeper
from ex04.phase7.investigation import BUG_REPORT
from ex04.services.comparison.service import ComparisonService
from ex04.services.graph.parser import GraphParser
from ex04.shared.types_experiment import ComparisonOutcome
from ex04.shared.types_request import ComparisonRequest

TARGET_COMMIT = "887009334e17556880f62d58315f96c2b305aa05"


def run_phase7_comparison(
    target_path: Path,
    graph_path: Path,
    vault_path: Path,
    artifact_root: Path,
) -> ComparisonOutcome:
    """Run and persist the Phase 7 naive-vs-graph comparison."""
    graph_data = GraphParser().parse(graph_path)
    source_files = sorted((target_path / "snippets").glob("*.py"))
    request = ComparisonRequest(
        target_repo="andela/buggy-python",
        target_commit=TARGET_COMMIT,
        bug_id="mutable-default-foo",
        bug_report=BUG_REPORT,
        target_snapshot_path=str(target_path),
        provider="phase7",
        model="phase7-deterministic",
        run_id="phase7-comparison",
        artifact_root=str(artifact_root),
        evidence_class="deterministic",
        system_prompt="Diagnose the bug and return grounded JSON.",
        prompt_version="phase7-comparison-v1",
        max_files=20,
        max_tool_calls=30,
        token_budget=8000,
    )
    return cast(
        ComparisonOutcome,
        ComparisonService(Phase7Gatekeeper(), "phase7").run_comparison(
            request,
            source_files,
            graph_data,
            vault_path,
        ),
    )
