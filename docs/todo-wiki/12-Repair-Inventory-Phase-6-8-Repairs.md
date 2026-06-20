<!-- GENERATED FROM CANONICAL DOCUMENTATION - DO NOT EDIT DIRECTLY -->

# 12. Repair Inventory (Phase 6–8 Repairs)

[Back to Home](./Home.md)

Stable repair task IDs for post-submission truthfulness repairs. Source: `/plan` session
2026-06-21 ([ASSIGNMENT.md §Deliverables]).

| Task ID | Status | Description | Files Affected | Priority |
|---|---|---|---|---|
| P8-R03 | Complete | Add repair task IDs to TODO/PLAN; regenerate wikis | `docs/TODO.md`, `docs/PLAN.md`, `docs/todo-wiki/*`, `docs/plan-wiki/*` | P0 |
| P6-R01 | Complete | Add `ComparisonRequest` with full controlled-experiment contract | `src/ex04/shared/types_request.py` (new) | P0 |
| P6-R02 | Complete | Add `StructuredEvidence` + `InvestigationRunRecord` types | `src/ex04/shared/types_investigation.py` (new) | P0 |
| P6-R06 | Complete | Remove `MetricsCalculator` clamp; wire `SignedMetricsCalculator` | `metrics.py`, `service.py` | P0 |
| P6-R03 | Complete | Replace `NaiveRunner` full-dump with bounded navigation | `naive_runner.py` | P0 |
| P6-R04 | Complete | Add bug-report-sensitive ranking; extract `ranking.py` | `graph_guided_runner.py`, `ranking.py` (new) | P0 |
| P6-R05 | Complete | Add `FairnessEnforcer`; wire into `ComparisonService` | `fairness.py` (new), `service.py` | P0 |
| P7-R01 | Complete | Implement real policy checks in `CorrectnessGate` | `correctness_gate.py` | P0 |
| P7-R02 | Complete | Add `pricing.json`; wire cost lookup into `ComparisonService` | `config/pricing.json` (new) | P0 |
| P7-R03 | Complete | Add missing fields to `RunManifest` | `types_experiment.py` | P0 |
| P8-R01 | Complete | Fix CI: `setup-uv` action, mypy step, fatal docs-sync | `.github/workflows/ci.yml` | P0 |
| P8-R02 | Complete | Expand repository validator with 4 new checks | `scripts/validate_repo.py` | P0 |
| P8-R05 | Complete | Pin real target commit, compute snapshot hash, run Graphify | `artifacts/pre_fix/provenance.json` | P0 |
| P8-R04 | Complete | Update README, evidence matrix, PROMPTS.md disclosure | `README.md`, `docs/EVIDENCE_MATRIX.md`, `docs/PROMPTS.md` | P1 |

**Definition of Done (per task)**: Implementation committed with task ID in subject; relevant tests pass; `ruff check` and `mypy` clean; file under 150 lines.

---
