# Evidence Matrix

| Field | Value |
|---|---|
| Version | 1.00 |
| Date | 2026-06-20 |
| Scope | Phase 6-8 finalization evidence |

## Evidence Classes

| Class | Meaning | Examples |
|---|---|---|
| Deterministic keyless evidence | Reproducible without provider credentials or live target execution | unit tests, validation scripts, docs sync |
| Representative deterministic fixture | Committed artifact that demonstrates schema or workflow shape only | `artifacts/manifests/*`, `obsidian/*`, `notebooks/walkthrough.ipynb` |
| Generated documentation | Derived from canonical docs or authored finalization docs | `docs/plan-wiki/*`, `docs/todo-wiki/*`, `docs/PROMPTS.md` |
| Blocked operation | Required live operation that could not be truthfully executed in this environment | live Graphify extraction, provider-backed investigation |

## Requirement Mapping

| Requirement | Implementation | Verification | Evidence | Status | Limitation |
|---|---|---|---|---|---|
| P6-I02 prompt registry | `docs/PROMPTS.md` | docs review, docs sync | prompt templates | Complete | Templates only; not historical executions |
| P6-I03 comparison contracts | `src/ex04/shared/types_experiment.py`, `src/ex04/shared/artifact_store.py` | `tests/unit/services/comparison/test_fairness.py`, `tests/unit/shared/test_artifact_store.py` | deterministic tests | Complete | Live manifests unavailable |
| P6-I04 distinct runners | `src/ex04/services/comparison/naive_runner.py`, `graph_guided_runner.py` | `tests/unit/services/comparison/test_fairness.py` | deterministic tests | Complete | Provider telemetry unavailable |
| P6-I06 correctness gate | `src/ex04/services/comparison/correctness_gate.py` | `tests/unit/services/comparison/test_correctness_gate.py` | deterministic tests | Complete | Not run against a real target snapshot |
| P6-I07 metrics | `src/ex04/services/comparison/signed_metrics.py` | `tests/unit/services/comparison/test_signed_metrics.py` | deterministic tests | Complete | Token deltas null when telemetry is missing |
| P7-I01 provenance | `src/ex04/shared/artifact_store.py`, `artifacts/pre_fix/provenance.json` | artifact-store tests, manifest validation | fixtures | Complete | Snapshot hash is fixture metadata |
| P7-I02 vault integration | `obsidian/`, `src/ex04/services/vault/` | vault unit tests | representative fixture | Complete | No live vault export in this run |
| P7-I03 graph extensions | `orphan_detector.py`, `patch_impact.py` | `test_orphan_detector.py`, `test_patch_impact.py` | deterministic tests | Complete | Graph reachability is not runtime proof |
| P7-I04 walkthrough | `notebooks/walkthrough.ipynb` | fixture import checks in full suite | notebook fixture | Complete | Notebook is fixture-based |
| P7-I05 live investigation evidence | N/A | N/A | blocked report | Blocked | No provider credentials or target clone |
| P8-I01 CI and validation | `.github/workflows/ci.yml`, `scripts/validate_repo.py` | ruff, mypy, pytest, validation | deterministic checks | Complete | CI remote execution not observed here |
| P8-I02 documentation | `README.md`, this file, `docs/SELF_ASSESSMENT.md` | docs sync and reference review | generated and authored docs | Complete | Live evidence remains blocked |
| P8-I03 visuals | `assets/README.md`, `assets/screenshots/README.md` | docs review | blocked-operation docs | Complete | No real screenshots generated |
| P8-I04 clean clone | `reports/clean_clone_verification.md` | isolated worktree verification | verification report | Complete | Report verifies candidate SHA before the report commit |

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.00 | 2026-06-20 | Initial Phase 6-8 evidence matrix. |
