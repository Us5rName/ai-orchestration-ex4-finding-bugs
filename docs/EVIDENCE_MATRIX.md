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
| P8-R02 validator | `scripts/validate_repo.py` | `tests/integration/test_validator_failures.py` | 16-check validator; 10 failure tests | Complete | Deterministic keyless evidence |
| P8-R05 target provenance | `artifacts/pre_fix/provenance.json`, `artifacts/pre_fix/graphify-out/graph.json` | provenance review | Real clone + Graphify run (code-only) | Complete | Graphify ran on snippets/ subdirectory (no API key); README extraction (docs) requires API key |
| P8-R06 charts | `assets/charts/*.png`, `assets/diagrams/architecture.md` | visual review | Fixture-labeled charts; Mermaid diagram | Complete | Token chart blocked; files/iterations from fixtures |
| P8-R07 notebook | `notebooks/comparison_analysis.ipynb` | `tests/unit/notebook/test_notebook_imports.py` | SDK-based, keyless notebook | Complete | No live LLM execution; fixture data only |
| P6-R07 SDK ops | `src/ex04/sdk/_comparison_ops.py` | `tests/unit/sdk/test_sdk_operations.py` | 7 new SDK operations; 8 tests | Complete | Deterministic keyless evidence |
| P6-R08 CLI delegation | `src/ex04/__main__.py` | `tests/unit/sdk/test_cli.py` | investigate-naive/graph subcommands; 6 boundary tests | Complete | Deterministic keyless evidence |
| P7-R04 comparison reports | `src/ex04/services/comparison/report_gen.py` | `tests/unit/services/comparison/test_comparison_reports.py` | JSON + MD reports; 4 tests | Complete | Deterministic keyless evidence |

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.00 | 2026-06-20 | Initial Phase 6-8 evidence matrix. |
| 1.01 | 2026-06-21 | Add P8-R02/05/06/07, P6-R07/08, P7-R04 rows. Update Graphify status (real run complete). |
