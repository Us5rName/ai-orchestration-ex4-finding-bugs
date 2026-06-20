"""Gate report writer — JSON + Markdown for correctness gate results.

Traceability: [TODO P7-R01], [Correction #7]
"""

from __future__ import annotations

import json
from pathlib import Path

from ex04.shared.types_experiment import GateOutput


def write_gate_reports(gate: GateOutput, artifact_path: Path | None) -> None:
    """Write gate_report.json and gate_report.md to artifact_path.

    Populates gate.report_json_path and gate.report_md_path in-place.
    No-ops when artifact_path is None.
    """
    if artifact_path is None:
        return
    artifact_path.mkdir(parents=True, exist_ok=True)
    json_path = artifact_path / "gate_report.json"
    md_path = artifact_path / "gate_report.md"

    report = {
        "final_verdict": gate.final_verdict,
        "failure_signature_found": gate.failure_signature_found,
        "failure_reproduced": gate.failure_reproduced,
        "reproduction_rc": gate.reproduction_rc,
        "post_fix_rc": gate.post_fix_rc,
        "patch_applied": gate.patch_applied,
        "patch_hash": gate.patch_hash,
        "targeted_test_passed": gate.targeted_test_passed,
        "relevant_suite_passed": gate.relevant_suite_passed,
        "verification_results": gate.verification_results,
        "tests_not_deleted": gate.tests_not_deleted,
        "assertions_not_weakened": gate.assertions_not_weakened,
        "diagnosis_consistent": gate.diagnosis_consistent,
        "path_violations": gate.path_violations,
        "limitations": gate.limitations,
        "evidence_class": gate.evidence_class,
    }
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    md = [
        "# Gate Report",
        f"**Verdict**: {gate.final_verdict}",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| Failure signature found | {gate.failure_signature_found} |",
        f"| Original reproduction rc | {gate.reproduction_rc} |",
        f"| Post-fix reproduction rc | {gate.post_fix_rc} |",
        f"| Patch applied | {gate.patch_applied} |",
        f"| Verification commands | {len(gate.verification_results)} |",
        f"| Tests not deleted | {gate.tests_not_deleted} |",
        f"| Assertions not weakened | {gate.assertions_not_weakened} |",
        f"| Diagnosis consistent | {gate.diagnosis_consistent} |",
    ]
    if gate.limitations:
        md += ["", "## Limitations"] + [f"- {lim}" for lim in gate.limitations]
    md_path.write_text("\n".join(md), encoding="utf-8")

    gate.report_json_path = str(json_path)
    gate.report_md_path = str(md_path)
