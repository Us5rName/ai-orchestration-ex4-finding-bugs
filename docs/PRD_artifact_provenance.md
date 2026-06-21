# PRD — Artifact Provenance and Immutable Evidence Lifecycle

| Field | Value |
|---|---|
| **Requirement ID** | PRD-AP |
| **Parent PRD** | [docs/PRD.md](PRD.md) §9 (Repository Structure) |
| **Status** | Active |
| **Date** | 2026-06-20 |

---

## Purpose

Define the contract for immutable, traceable evidence storage so that every
committed artifact can be connected to its originating run, snapshot, and
configuration.

---

## Scope

Covers: directory layout, provenance records, content hashing, overwrite
protection, manifest schema, and artifact sanitization.

Out of scope: graph or vault content format, LLM provider billing.

---

## Artifact Directory Layout

```
artifacts/
├── pre_fix/          # Pristine pre-fix evidence (graph.json, vault snapshot)
├── post_fix/         # Post-fix evidence for before/after comparison
├── runs/
│   └── <run-id>/     # Per-run: manifest.json, result.json, gate_output.json
│       └── reports/
│           ├── comparison.json
│           ├── comparison.md
│           ├── orphan_report.json      # Planned: T6.05 closure
│           ├── orphan_report.md        # Planned: T6.05 closure
│           ├── graph_diff.json         # Planned: T6.09
│           └── graph_diff.md           # Planned: T6.09
├── manifests/        # Cross-run manifest index
└── self_grade/
    └── <grade-id>/   # Planned: T8.13
        ├── self_grade.json
        └── self_grade.md

reports/              # Legacy authored reports; production reports live under runs/
obsidian/             # Obsidian vault (generated; committed when stable)
assets/               # Real screenshots and diagrams only
```

---

## Provenance Record Schema

Every `artifacts/manifests/<run-id>_manifest.json` must contain:

| Field | Type | Description |
|---|---|---|
| `run_id` | str | UUID or timestamp-based unique ID |
| `timestamp` | str (ISO-8601) | When the run started |
| `mode` | str | `naive` or `graph_guided` |
| `provider` | str | Provider name |
| `model` | str | Model identifier |
| `target_identifier` | str | Repository or snapshot name |
| `target_commit` | str | Commit SHA of target (when available) |
| `target_snapshot_hash` | str | SHA-256 of target directory (when computed) |
| `config_hash` | str | Full SHA-256 of the controlled request payload |
| `prompt_version` | str | Prompt registry ID used |
| `input_tokens` | int \| null | From provider response |
| `output_tokens` | int \| null | From provider response |
| `total_tokens` | int \| null | Sum of above |
| `estimated_cost_usd` | float \| null | Only when real pricing data available |
| `model_calls` | int | Number of provider calls |
| `tool_calls` | int | Number of tool invocations |
| `files_read` | int | Source files read |
| `bytes_read` | int | Bytes read from source |
| `source_anchors` | list[str] | `file:start-end` references used |
| `iterations` | int | Agent iterations |
| `duration_seconds` | float | Wall-clock time |
| `diagnosis_status` | str | `unverified` / `grounded_candidate` / `rejected` |
| `patch_status` | str | `applied` / `not_applied` / `skipped` |
| `correctness_gate_status` | str | `not_requested` / `not_run` / `passed` / `failed` / `blocked` / `inconclusive` |
| `limitations` | list[str] | Known limitations of this run |
| `telemetry_available` | bool | Whether provider telemetry was returned |
| `extension_report_paths` | list[str] \| null | Relative paths to extension reports (orphan, weakness, etc.) |
| `graph_diff_json_path` | str \| null | Relative path to `graph_diff.json` (planned T6.09) |
| `graph_diff_markdown_path` | str \| null | Relative path to `graph_diff.md` (planned T6.09) |
| `pre_graph_hash` | str \| null | SHA-256 of pre-fix graph.json |
| `post_graph_hash` | str \| null | SHA-256 of post-fix graph.json |
| `graph_diff_hash` | str \| null | SHA-256 of graph_diff.json |
| `self_grade_config_hash` | str \| null | SHA-256 of self-grade rubric configuration (planned T8.13) |

**Note**: Self-grade artifacts (`artifacts/self_grade/<grade-id>/`) are repository-assessment artifacts. They are not attributed to either the naive or graph-guided comparison mode.

---

## Invariants

- Manifest files are write-once, and trace/report files reject overwrites.
- No secrets, API keys, or personal paths appear in any committed artifact.
- Every real run manifest maps to an `artifacts/runs/<run-id>/` directory.
- Fixture files are clearly labeled with `"evidence_class": "fixture"` in their JSON.

---

## Failure Behavior

| Condition | Behavior |
|---|---|
| Overwrite attempted on existing run dir | Raise `ArtifactOverwriteError` |
| Provider telemetry unavailable | Record `telemetry_available: false`; tokens set to `null` |
| Cost unavailable | Record `estimated_cost_usd: null` |
| Target commit unknown | Record `target_commit: "unknown"` |

---

## Security Constraints

- `sanitize_artifact(data)` removes credential keys such as API keys, secrets,
  passwords, auth/access/refresh tokens, plus personal `/home` or `/Users`
  paths. Token telemetry fields such as `input_tokens` remain numeric evidence.
- Sanitizer must be tested with known-sensitive fixture data.

---

## Measurable Acceptance Criteria

- [ ] `ArtifactStore.save_manifest` raises `ArtifactOverwriteError` on duplicate manifest ID.
- [ ] All provenance JSON files validate against the schema above.
- [ ] Sanitizer removes personal paths and keys from test fixtures.
- [ ] `artifacts/runs/` exists and is committed (may contain fixture runs).
- [ ] Tests in `tests/unit/` cover overwrite protection and sanitization.

---

## Alternatives Considered

| Alternative | Reason rejected |
|---|---|
| Flat artifacts/ directory | Makes before/after comparison harder to navigate |
| Git LFS for large artifacts | Adds complexity; artifacts should be small JSON/Markdown |

---

## Testing Strategy

- Unit tests: `ArtifactStore` overwrite protection, schema validation, sanitizer.
- Integration tests: full run saves a valid manifest that round-trips JSON.

---

## Evidence Requirements

- `artifacts/manifests/` contains at least one fixture manifest.
- `tests/unit/shared/test_artifact_store.py` passes.

---

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-06-20 | Initial creation for Phase 7 finalization |
| 1.1 | 2026-06-21 | Align manifest naming, full controlled hashes, token telemetry preservation, and production report layout. |
| 1.2 | 2026-06-21 | Add planned artifact paths for extension reports (T6.05), graph-diff (T6.09), and self-grade (T8.13); add planned provenance fields `extension_report_paths`, `graph_diff_json_path`, `graph_diff_markdown_path`, `pre_graph_hash`, `post_graph_hash`, `graph_diff_hash`, `self_grade_config_hash`; clarify self-grade artifacts are not attributed to comparison modes. Traceability: [PRD §5.7 FR-7.5, FR-7.4], [PRD §5.8 FR-8.4]. |
