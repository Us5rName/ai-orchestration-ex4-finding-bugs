# Evidence Matrix

| Field | Value |
|---|---|
| Version | 1.04 |
| Date | 2026-06-21 |
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
| P8-R02 validator | `scripts/validate_repo.py` | `tests/integration/test_validator_failures.py` | 19-check validator; 10 failure tests | Complete | Deterministic keyless evidence |
| P8-R05 target provenance | `artifacts/pre_fix/provenance.json`, `artifacts/pre_fix/graphify-out/graph.json` | provenance review | Real clone + Graphify run (code-only) | Complete | Graphify ran on snippets/ subdirectory (no API key); README extraction (docs) requires API key |
| P8-R06 charts | `assets/charts/*.png`, `assets/diagrams/architecture.md` | visual review | Fixture-labeled charts; Mermaid diagram | Complete | Token chart blocked; files/iterations from fixtures |
| P8-R07 notebook | `notebooks/comparison_analysis.ipynb` | `tests/unit/notebook/test_notebook_imports.py` | SDK-based, keyless notebook | Complete | No live LLM execution; fixture data only |
| P6-R07 SDK ops | `src/ex04/sdk/_comparison_ops.py` | `tests/unit/sdk/test_sdk_operations.py` | 7 new SDK operations; 8 tests | Complete | Deterministic keyless evidence |
| P6-R08 CLI delegation | `src/ex04/__main__.py` | `tests/unit/sdk/test_cli.py` | investigate-naive/graph subcommands; 6 boundary tests | Complete | Deterministic keyless evidence |
| P7-R04 comparison reports | `src/ex04/services/comparison/report_gen.py` | `tests/unit/services/comparison/test_comparison_reports.py` | JSON + MD reports; 4 tests | Complete | Deterministic keyless evidence |
| P6-R10 canonical request | `ComparisonRequest.controlled_config_hash()` | request/fairness tests | full SHA-256 config hash; all fields classified | Complete | Deterministic keyless evidence |
| P6-R11 budgets/traces | `budget.py`, `trace.py` | `test_budget_trace.py` | cumulative counters; immutable JSONL trace hash | Complete | Deterministic keyless evidence |
| P6-R12 runner migration | naive and graph runners | runner/fairness tests | canonical request/result path; no parsed-output correctness shortcut | Complete | Deterministic keyless evidence |
| P6-R13 production fairness | `ComparisonService.run_comparison()` | comparison-service tests | distinct derived mode requests checked before provider calls | Complete | Deterministic keyless evidence |
| P6-R14 SDK/CLI boundary | SDK mixin and CLI | SDK/CLI tests | public service delegation; no private runner access | Complete | Deterministic keyless evidence |
| P7-R06 correctness gate | `CorrectnessGate` | gate tests | original reproduction, post-fix rc, verification-command verdicts | Complete | Deterministic keyless evidence |
| P7-R07 manifests/reports | artifact store, report writer | artifact/report tests | token telemetry preserved; full hashes; persisted reports/manifests | Complete | Deterministic keyless evidence |
| P8-R10 CI/regression gates | CI workflow, validator, impact BFS | validator and impact tests | Node 24 action pins; 19-check validator; zero-depth BFS fix | Complete | Deterministic keyless evidence |
| T7.07 → FR-7.5 (Orphan Detection core) | `src/ex04/services/analysis/orphan_detector.py`, SDK `detect_orphans()` | `tests/unit/services/analysis/test_orphan_detector.py` | deterministic tests | Complete (core) | Report persistence (T6.05 closure) and artifact paths remain pending |
| T6.05 → FR-7.5 (Orphan Detection closure) | report persistence to `artifacts/runs/<run-id>/reports/orphan_report.{json,md}` | closure verification | artifact paths | In Progress | Core implementation (T7.07) is Done; closure work remains |

| T4.19a → enriched graph models | `src/ex04/shared/types_graph_enums.py`, `src/ex04/shared/types.py`, `src/ex04/services/graph/_parser_helpers.py`, `src/ex04/services/graph/parser.py` | `tests/unit/services/graph/test_graph_models.py` (71 tests) | ConfidenceState/EdgeDirection enums; enriched Entity/Relationship; validated parser | Done | Deterministic keyless evidence; commit b078da9 |
| T4.19 → GraphReader facade | `src/ex04/services/graph/reader.py` | `tests/unit/services/graph/test_reader.py` (52 tests) | O(1) indexed edge lookup; deterministic ordering; immutable public results; EdgeDirection; from_path delegation | Done | Deterministic keyless evidence; commit 5011543 |
| T5.03 → comparison parity | `src/ex04/services/comparison/context_bundle.py`, `call_service.py`, `prompt_builder.py`, `parity.py` | `tests/unit/services/comparison/test_call_service.py`, `test_context_bundle.py`, `test_prompt_builder.py`, `test_parity.py` (111 tests) | one prompt envelope; atomic call path; SHA-256 parity fingerprint; pre-call mismatch rejection | Done | Deterministic keyless evidence; commits 25b1c2d, d63d13f |

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.00 | 2026-06-20 | Initial Phase 6-8 evidence matrix. |
| 1.01 | 2026-06-21 | Add P8-R02/05/06/07, P6-R07/08, P7-R04 rows. Update Graphify status (real run complete). |
| 1.02 | 2026-06-21 | Add P6-R10 through P8-R10 repair rows and update coverage to 531 tests / 95.35%. |
| 1.04 | 2026-06-21 | Sync header version to 1.04 per corrective commit; no evidence rows changed in this commit. Traceability: [PRD-EXT §EXT-1].
| 1.03 | 2026-06-21 | Add T7.07→FR-7.5 (core complete) and T6.05→FR-7.5 (closure in progress) rows; distinguish core implementation evidence from closure/report-persistence evidence. Traceability: [TODO T6.05], [PRD-EXT §EXT-1]. |
| 1.05 | 2026-06-21 | Add Wave 1 evidence rows: T4.19a (graph model enrichment), T4.19 (GraphReader facade), T5.03 (comparison parity). 659 tests / 96.51% coverage. Traceability: [PLAN ADR-007, ADR-008], [PRD §5.7 FR-7.7], [PRD §5.6 FR-6.4]. |
