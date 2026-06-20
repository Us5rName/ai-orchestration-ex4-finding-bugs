<!-- GENERATED FROM CANONICAL DOCUMENTATION - DO NOT EDIT DIRECTLY -->

# 12. Repair Inventory (Phase 6–8 Architectural Repairs)

[Back to Home](./Home.md)

Stable repair task IDs for post-submission truthfulness repairs to the comparison-service
architecture. Source: `/plan` session 2026-06-21 ([ASSIGNMENT.md §Deliverables]).

| Task ID | Architecture Area | Design Change | Source File |
|---|---|---|---|
| P6-R01 | Experiment Contracts | Add `ComparisonRequest` with target identity, budgets, patch/gate/artifact config | `shared/types_request.py` (new) |
| P6-R02 | Experiment Contracts | Add `StructuredEvidence` + `InvestigationRunRecord` for typed evidence trail | `shared/types_investigation.py` (new) |
| P6-R03 | Comparison Service | Replace `NaiveRunner` full-corpus dump with bounded navigation (budget enforcement) | `comparison/naive_runner.py` |
| P6-R04 | Comparison Service | Replace degree-only ranking with multi-signal (bug-report terms + degree + path + type); extract `ranking.py` | `comparison/ranking.py` (new), `comparison/graph_guided_runner.py` |
| P6-R05 | Comparison Service | Add `FairnessEnforcer` pre-call invariant check + config hash; wire into `ComparisonService` | `comparison/fairness.py` (new), `comparison/service.py` |
| P6-R06 | Metrics | Remove `max(0.0, ...)` clamp in `MetricsCalculator`; wire `SignedMetricsCalculator` as active path | `comparison/metrics.py`, `comparison/service.py` |
| P7-R01 | Correctness Gate | Implement real `_check_prohibited_files`, `_check_tests_not_deleted`, `_check_assertions_not_weakened` (remove defaulted-True policy fields) | `comparison/correctness_gate.py` |
| P7-R02 | Configuration | Add versioned `config/pricing.json`; wire cost lookup into `ComparisonService` | `config/pricing.json` (new) |
| P7-R03 | Manifests | Add `shared_config_hash`, `strategy_hash`, schema/pricing/repo_commit version fields to `RunManifest` | `shared/types_experiment.py` |
| P8-R01 | CI | Use `astral-sh/setup-uv@v5`; add mypy step; make docs-sync fatal | `.github/workflows/ci.yml` |
| P8-R02 | Validation | Add manifest↔run linkage, provenance key check, direct-provider-import boundary, wiki-dir presence checks | `scripts/validate_repo.py` |
| P8-R03 | Documentation | Add stable repair task IDs to TODO/PLAN before implementation | `docs/TODO.md`, `docs/PLAN.md` |
| P8-R04 | Documentation | Update README test count, evidence matrix rows, PROMPTS.md disclosure | `README.md`, `docs/EVIDENCE_MATRIX.md`, `docs/PROMPTS.md` |
| P8-R05 | Provenance | Pin real target commit, compute deterministic snapshot hash, run Graphify | `artifacts/pre_fix/provenance.json` |

**ADR Note**: All P6-R changes preserve existing public interfaces (`ExperimentConfig`, `RunMetrics`, `ComparisonReport`) for backward compatibility. New types are additive ([ADR-005 SDK-First Design]).

---
