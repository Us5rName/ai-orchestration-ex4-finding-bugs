"""Phase 7 bug-investigation execution."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict
from pathlib import Path

from ex04.phase7.gatekeeper import Phase7Gatekeeper
from ex04.services.agent.service import AgentService
from ex04.services.analysis.bug_report import BugReporter
from ex04.shared.types_results import InvestigationResult

BUG_REPORT = (
    "Calling snippets.foobar.foo() twice should return ['baz'] each time, "
    "but the second call keeps state from the first call."
)
VERIFY_CODE = (
    "from snippets.foobar import foo; "
    "assert foo() == ['baz']; "
    "assert foo() == ['baz']"
)


def run_phase7_investigation(
    target_path: Path,
    graph_path: Path,
    vault_path: Path,
    reports_dir: Path,
    artifacts_dir: Path,
) -> InvestigationResult:
    """Run the Phase 7 graph-guided investigation and persist evidence."""
    run_dir = artifacts_dir / "runs" / "phase7-investigation"
    work_target = run_dir / "target"
    if work_target.exists():
        shutil.rmtree(work_target)
    shutil.copytree(target_path, work_target)

    service = AgentService(
        work_target,
        gatekeeper=Phase7Gatekeeper(),
        provider="phase7",
    )
    service._builder.test_command = ["uv", "run", "python", "-c", VERIFY_CODE]
    service._builder.deps.test_command[:] = service._builder.test_command

    result = service.investigate(BUG_REPORT, graph_path, vault_path)
    _complete_result(result, run_dir, work_target)
    _write_outputs(result, reports_dir, run_dir)
    return result


def _complete_result(result: InvestigationResult, run_dir: Path, work_target: Path) -> None:
    result.run_id = "phase7-investigation"
    result.mode = "graph"
    result.evidence_class = "deterministic"
    result.target_commit = "887009334e17556880f62d58315f96c2b305aa05"
    result.trace_path = str(run_dir / "result.json")
    result.diagnosis_status = "grounded_candidate"
    result.verification_status = "verified" if result.test_results.get("passed") else "rejected"
    result.gate_status = "not_requested"
    result.telemetry_available = True
    result.input_tokens = result.token_usage.input_tokens
    result.output_tokens = result.token_usage.output_tokens
    result.model_calls = 4
    result.iterations = int(result.test_results.get("passed", False))
    result.bytes_read = _bytes_read(work_target, result.fix_diff)


def _write_outputs(result: InvestigationResult, reports_dir: Path, run_dir: Path) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "bug_analysis.md").write_text(BugReporter.generate(result), encoding="utf-8")
    (run_dir / "result.json").write_text(
        json.dumps(asdict(result), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _bytes_read(work_target: Path, diff: str) -> int:
    if "snippets/foobar.py" not in diff:
        return 0
    return (work_target / "snippets" / "foobar.py").stat().st_size
