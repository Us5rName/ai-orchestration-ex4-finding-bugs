<!-- GENERATED FROM CANONICAL DOCUMENTATION - DO NOT EDIT DIRECTLY -->

# 12. Repair Inventory (Phase 6–8 Repairs)

[Back to Home](./Home.md)

Stable repair task IDs for post-submission truthfulness repairs. Source: `/plan` session
2026-06-21 ([ASSIGNMENT.md §Deliverables]).

| Task ID | Status | Description | Files Affected | Priority |
|---|---|---|---|---|
| P8-R03 | Complete | Add repair task IDs to TODO/PLAN; regenerate wikis | `docs/TODO.md`, `docs/PLAN.md`, `docs/todo-wiki/*`, `docs/plan-wiki/*` | P0 |
| P6-R10 | Complete | Complete and validate the canonical comparison contract | `src/ex04/shared/types_request.py`, `src/ex04/shared/types_results.py` | P0 |
| P6-R11 | Complete | Introduce shared cumulative budget and trace infrastructure | `src/ex04/services/comparison/budget.py`, `src/ex04/services/comparison/trace.py` | P0 |
| P6-R12 | Complete | Migrate both runners to the canonical request/result path | `src/ex04/services/comparison/naive_runner.py`, `src/ex04/services/comparison/graph_guided_runner.py` | P0 |
| P6-R13 | Complete | Rebuild production comparison orchestration and fairness | `src/ex04/services/comparison/service.py`, `src/ex04/services/comparison/fairness.py` | P0 |
| P6-R14 | Complete | Repair SDK and CLI delegation boundaries | `src/ex04/sdk/`, `src/ex04/__main__.py` | P0 |
| P7-R06 | Complete | Complete correctness-gate execution and verdict semantics | `src/ex04/services/comparison/correctness_gate.py`, `src/ex04/services/comparison/gate_*` | P0 |
| P7-R07 | Complete | Integrate manifests, signed metrics, and reports | `src/ex04/services/comparison/report_gen.py`, `src/ex04/shared/artifact_store.py` | P0 |
| P8-R10 | Complete | Add production-path regression tests and CI repairs | `tests/`, `.github/workflows/ci.yml`, `scripts/validate_repo.py` | P0 |
| P8-R11 | Complete | Reconcile documentation, verify clean clone, and update PR | `docs/`, `README.md`, verification reports | P0 |
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
