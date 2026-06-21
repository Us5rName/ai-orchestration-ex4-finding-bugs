<!-- GENERATED FROM CANONICAL DOCUMENTATION - DO NOT EDIT DIRECTLY -->

# 7. Phase 6 — Comparison Service

[Back to Home](./Home.md)

**Goal**: Implement token comparison (naive vs. graph-guided).

### T6.01 — Naive Runner

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.7 Comparison Service — naive_runner.py] |
| **PRD Reference** | [PRD FR-6.1] |
| **Estimate** | 60 min |

**Definition of Done**:

- [x] `NaiveRunner.run(bug_report, source_files)` dumps all code context
- [x] Makes LLM calls via Gatekeeper without graph guidance
- [x] Tracks: tokens used, files read, iterations, time elapsed
- [x] Returns `RunMetrics`

**Independent Verification**:

```bash
uv run pytest tests/unit/services/comparison/test_naive_runner.py -v
# Uses mock provider — no real API calls
```

---

### T6.02 — Graph-Guided Runner

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.7 Comparison Service — graph_guided_runner.py] |
| **PRD Reference** | [PRD FR-6.2] |
| **Estimate** | 60 min |

**Definition of Done**:

- [x] `GraphGuidedRunner.run(bug_report, graph, vault)` navigates via graph + vault first
- [x] Makes focused LLM calls via Gatekeeper
- [x] Tracks: tokens used, files read, iterations, time elapsed
- [x] Returns `RunMetrics`

**Independent Verification**:

```bash
uv run pytest tests/unit/services/comparison/test_graph_guided_runner.py -v
# Uses mock provider — no real API calls
```

---

### T6.03 — Metrics Calculator

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.7 Comparison Service — metrics.py] |
| **PRD Reference** | [PRD FR-6.3] |
| **Estimate** | 30 min |

**Definition of Done**:

- [x] `compare(naive, guided)` calculates savings percentages
- [x] Computes: `token_savings_pct`, `file_read_savings_pct`, `iteration_savings_pct`
- [x] Returns `ComparisonMetrics`
- [x] Handles edge cases: zero tokens, equal runs

**Independent Verification**:

```bash
uv run pytest tests/unit/services/comparison/test_metrics.py -v
```

---

### T6.04 — Comparison Report Generator

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P1 |
| **PLAN Reference** | [PLAN §3.7 Comparison Service — report_gen.py] |
| **PRD Reference** | [PRD FR-6.3] |
| **Estimate** | 30 min |

**Definition of Done**:

- [x] `generate(metrics)` produces Markdown comparison report
- [x] Includes side-by-side table of naive vs. guided metrics
- [x] Includes savings percentages
- [ ] Saves to `reports/` directory

**Independent Verification**:

```bash
uv run pytest tests/unit/services/comparison/test_report_gen.py -v
```

---

### T6.05 — Orphan Detection Closure (FR-7.5)

| Attribute | Value |
|---|---|
| **Status** | **In Progress** — core implementation and SDK exposure exist; report persistence, README documentation, explicit evidence mapping, and closure verification remain |
| **Priority** | P1 |
| **Execution Order** | 4th of 6 remaining tasks |
| **PLAN Reference** | [PLAN §3.6 Analysis Service], [PLAN §11 Traceability Matrix — FR-7.5] |
| **PRD Reference** | [PRD §5.7 FR-7.5], [PRD-EXT §EXT-1] |
| **Traceability** | T6.05 → FR-7.5 → T7.07 (OrphanDetector implementation, Done) |
| **Depends On** | T7.07 OrphanDetector (Done); optionally T4.19 for GraphReader integration |
| **Estimate** | 60 min (closure only; core implementation exists) |

**Selected Extension**: FR-7.5 Orphan Detection (formally selected for T6.05).

**What already exists (T7.07 Done)**:
- `src/ex04/services/analysis/orphan_detector.py` — OrphanDetector with detect(), generate_stub(), detect_and_report()
- `Ex04SDK.detect_orphans(graph_data, output_dir)` — SDK exposure
- `tests/unit/services/analysis/test_orphan_detector.py` — unit tests

**Remaining closure work**:
1. Confirm or complete the public SDK path to `detect_orphans`.
2. Add deterministic JSON report to `artifacts/runs/<run-id>/reports/orphan_report.json`.
3. Add Markdown report to `artifacts/runs/<run-id>/reports/orphan_report.md` (rendered from JSON).
4. Persist reports through the artifact/provenance layer (ArtifactStore).
5. After T4.19: reuse GraphReader for graph access where appropriate.
6. Add orphan report paths to run manifest (`extension_report_paths`).
7. Add README usage section only after artifacts exist.
8. Update evidence matrix with truthful evidence paths.
9. Verify: happy path, empty graph, invalid threshold/input, and deterministic ordering all tested.

**Tests to verify or add**:
- [x] Happy path (T7.07)
- [x] Empty graph (T7.07)
- [x] Isolated nodes (T7.07)
- [x] Threshold edge cases (T7.07)
- [ ] JSON report persisted to expected path
- [ ] Markdown report derived from JSON
- [ ] Deterministic ordering across two runs on same input
- [ ] Invalid threshold raises ValueError

**Non-goals**:
- Do not claim orphans are defects.
- Do not add README section before artifacts exist.
- Do not mark T6.05 Done until all closure items are verified.

**Definition of Done** (T6.05 is Done only when):
- [ ] FR-7.5 formally selected and explicitly traceable: T6.05 → FR-7.5 → T7.07.
- [ ] Existing implementation and SDK exposure verified.
- [ ] JSON and Markdown reports produced and persisted.
- [ ] Happy, empty, invalid, and deterministic test cases pass.
- [ ] README documents real usage and artifact paths with actual examples.
- [ ] Evidence matrix points to actual tests and artifacts.
- [ ] Limitations are explicit in the report.

**Independent Verification**:

```bash
uv run pytest tests/unit/services/analysis/test_orphan_detector.py -v
```

---

### T6.06 — Deterministic Correctness Gate

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.7 Comparison Service] |
| **PRD Reference** | [PRD-CE] Measurable Acceptance Criteria |
| **Estimate** | 45 min |

**Definition of Done**:

- [x] `CorrectnessGate` validates patch against original failure reproduction
- [x] Gate distinguishes: reproduced-failure / patch-applied / targeted-test / suite / policy / final verdict
- [x] Machine-readable JSON and human-readable Markdown output
- [x] `tests/unit/services/comparison/test_correctness_gate.py` passes

**Independent Verification**:

```bash
uv run pytest tests/unit/services/comparison/test_correctness_gate.py -v
```

---

### T6.07 — Run Ledgers and Metrics Reports

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P1 |
| **PLAN Reference** | [PLAN §3.7 Comparison Service] |
| **PRD Reference** | [PRD-CE] Run Ledgers |
| **Estimate** | 45 min |

**Definition of Done**:

- [x] `RunManifest` dataclass covers all required provenance fields
- [x] `ArtifactStore.save_manifest` writes JSON to `artifacts/manifests/`
- [x] Overwrite protection raises `ArtifactOverwriteError`
- [x] Signed deltas and negative savings preserved
- [x] `tests/unit/shared/test_artifact_store.py` passes

**Independent Verification**:

```bash
uv run pytest tests/unit/shared/test_artifact_store.py -v
```

---

### T6.08 — Fairness Invariant Tests

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.7 Comparison Service] |
| **PRD Reference** | [PRD-CE] Contracts and Fairness Invariants |
| **Estimate** | 30 min |

**Definition of Done**:

- [x] Tests verify both modes receive identical config, bug report, provider, model
- [x] Tests verify naive mode does not use graph data
- [x] Tests verify graph-guided mode uses entity names and vault notes
- [x] `tests/unit/services/comparison/test_fairness.py` passes

**Independent Verification**:

```bash
uv run pytest tests/unit/services/comparison/test_fairness.py -v
```

---

### T6.09 — Full Graph-Diff Comparison Report Section

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P1 |
| **Execution Order** | 5th of 6 remaining tasks (after T4.19 GraphReader) |
| **PLAN Reference** | [PLAN §3.7 Comparison Service], [PLAN ADR-007] |
| **PRD Reference** | [PRD §5.7 FR-7.4], [PRD-CE §Graph-Diff Report Integration], [PRD-AP §Artifact Layout] |
| **Depends On** | T4.19 GraphReader (operates on GraphReader/GraphData, not raw JSON) |
| **Estimate** | 90 min |

**Purpose**: Produce a full typed pre/post structural comparison of graph entities, relationships, and communities. The diff operates on `GraphReader`/`GraphData` — it must not load raw JSON independently.

**Planned package**: `src/ex04/services/comparison/graph_diff/`

```
__init__.py
models.py          — GraphDiffResult, entity/relationship/community change models, typed status values
canonicalize.py    — stable identity normalization for entities and relationships
differ.py          — GraphDiffer: produce typed diff from two GraphData objects
community_matcher.py — deterministic community matching by entity-membership overlap (Jaccard)
renderer.py        — render GraphDiffResult to JSON and Markdown artifacts
```

**Entity classification**:
```
added | removed | changed | unchanged
```

**Relationship classification**:
```
added | removed | changed | unchanged
```
Relationship identity: (source entity ID, target entity ID, relationship type, direction).
Non-identity attributes (confidence, weight, source anchor, metadata) determine `changed`.

**Community classification**:
```
preserved | expanded | contracted | split | merged | added | removed
```
Community comparison must NOT use raw numeric community IDs (they can change between graph generations).
Use deterministic entity-membership overlap (Jaccard similarity + deterministic tie-breaking).

**Post-fix graph status values**:
```python
class PostGraphStatus(Enum):
    AVAILABLE = "available"
    UNCHANGED = "unchanged"
    BLOCKED = "blocked"
    MISSING = "missing"
    INVALID = "invalid"
```

A missing or invalid post-fix graph must NOT destroy the comparison report.
The comparison token metrics remain available regardless of graph-diff availability.

**Planned artifacts**:
- `artifacts/runs/<run-id>/reports/graph_diff.json` — canonical machine-readable diff
- `artifacts/runs/<run-id>/reports/graph_diff.md` — rendered from JSON
- Paths and SHA-256 hashes included in run manifest (`graph_diff_json_path`, `graph_diff_markdown_path`, `graph_diff_hash`, `pre_graph_hash`, `post_graph_hash`)

**Implementation subtasks**:
1. Create `models.py` with all typed change models and `PostGraphStatus`.
2. Create `canonicalize.py` for stable entity and relationship identity normalization.
3. Create `differ.py` — `GraphDiffer` consuming two `GraphData` objects via `GraphReader`.
4. Create `community_matcher.py` — Jaccard-based community matching with tie-breaking.
5. Create `renderer.py` — JSON and Markdown rendering with provenance fields.
6. Wire into comparison service to optionally include diff when graph snapshots available.

**Tests required** (`tests/unit/services/comparison/test_graph_diff.py`):
- Changed graph: verify entity/relationship/community classifications.
- Unchanged graph: all entries classified as `unchanged`.
- Missing post-fix graph: `MISSING` status, comparison metrics still available.
- Invalid post-fix graph: `INVALID` status with error details.
- Community matching: no raw ID dependence; entity-membership overlap used.
- Deterministic ordering: same result across two calls on same input.
- Artifact persistence: JSON and Markdown written to expected paths.

**Non-goals**:
- Do not include repository-specific assertions (fixed Polygon node names, etc.) in the diff engine.
- Do not load raw JSON graphs independently (always go through GraphReader/GraphData).
- Do not block comparison report on graph-diff failure.

**Definition of Done** (T6.09 is Done only when):
- [ ] Entities, relationships, and communities receive complete classifications.
- [ ] Stable identity and change semantics are implemented.
- [ ] Community matching does not depend on raw IDs.
- [ ] Missing/blocked/invalid post-graph states are typed and rendered honestly.
- [ ] JSON and Markdown artifacts are persisted and hashed.
- [ ] Comparison results remain available when graph diff is unavailable.
- [ ] Unit, rendering, artifact, and integration tests pass.

**Independent Verification**:

```bash
uv run pytest tests/unit/services/comparison/test_graph_diff.py tests/unit/services/comparison/test_comparison_reports.py -v
```

---
