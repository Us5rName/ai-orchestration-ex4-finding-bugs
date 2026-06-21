<!-- GENERATED FROM CANONICAL DOCUMENTATION - DO NOT EDIT DIRECTLY -->

# 8. Phase 7 — End-to-End Execution

[Back to Home](./Home.md)

**Goal**: Run the full pipeline on the target codebase.

### T7.01 — Run Grphify on Target Codebase

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §4.1 End-to-End Workflow] |
| **PRD Reference** | [PRD G1] |
| **Estimate** | 30 min |

**Definition of Done**:

- [x] Grphify runs on `graph-home/.graphify/repos/andela/buggy-python/snippets`
- [x] `graph.json` produced in `graph-home/graphify-out/`
- [x] `GRAPH_REPORT.md` produced
- [x] Graph data validated (13 entities, 11 relationships, 3 communities)
- [x] **Note (C9)**: `andela/buggy-python` is the selected target; BugsInPy isolation is not applicable.

**Independent Verification**:

```bash
uv run python -c "from ex04.sdk import Ex04SDK; sdk = Ex04SDK.from_config('config/setup.json'); r = sdk.run_graphify('graph-home/.graphify/repos/andela/buggy-python'); print(r)"
ls -la graph-home/graphify-out/graph.json
```

---

### T7.02 — Build Obsidian Vault

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §4.1 End-to-End Workflow] |
| **PRD Reference** | [PRD G2] |
| **Estimate** | 20 min |

**Definition of Done**:

- [ ] `obsidian/index.md` exists with proper navigation structure
- [ ] `obsidian/hot.md` exists with bug-focused context
- [ ] At least 2 component notes exist
- [ ] Wikilinks are valid (target notes exist)

**Independent Verification**:

```bash
ls -la obsidian/*.md
grep -c '\[\[' obsidian/index.md  # Should be > 0 (has wikilinks)
```

---

### T7.03 — Execute Bug Investigation

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §4.1 End-to-End Workflow] |
| **PRD Reference** | [PRD G4-G5] |
| **Estimate** | 30 min + LLM cost |

**Definition of Done**:

- [ ] LangGraph workflow executes from knowledge load to verification
- [ ] Bug is identified with root cause description
- [ ] Fix is applied to target code
- [ ] Tests pass after fix
- [ ] `reports/bug_analysis.md` generated

**Independent Verification**:

```bash
uv run python -c "from ex04.sdk import Ex04SDK; sdk = Ex04SDK.from_config('config/setup.json'); r = sdk.investigate_bug('...'); print(r)"
cat reports/bug_analysis.md
```

---

### T7.04 — Execute Token Comparison

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §4.2 Comparison Workflow] |
| **PRD Reference** | [PRD G6] |
| **Estimate** | 30 min + LLM cost |

**Definition of Done**:

- [ ] Both naive and graph-guided runs complete
- [ ] `ComparisonMetrics` shows token savings ≥ 30%
- [ ] `artifacts/runs/<run-id>/reports/comparison.md` generated
- [ ] Report includes side-by-side metrics table

**Independent Verification**:

```bash
uv run python -c "from ex04.sdk import Ex04SDK; sdk = Ex04SDK.from_config('config/setup.json'); r = sdk.run_comparison('...'); print(r)"
find artifacts/runs -path "*/reports/comparison.md" -print
```

---

### T7.05 — Generate Reverse Engineering Artifacts

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.6 Analysis Service] |
| **PRD Reference** | [PRD G3] |
| **Estimate** | 20 min |

**Definition of Done**:

- [ ] Architectural block diagram generated (Mermaid)
- [ ] OOP schema generated (Mermaid)
- [ ] Diagrams saved to `reports/` and embedded in `README.md`

**Independent Verification**:

```bash
ls reports/*.md
grep -c 'mermaid' reports/*.md
```

---

### T7.06 — Update Obsidian After Investigation

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P1 |
| **PLAN Reference** | [PLAN §3.4 Vault Service] |
| **PRD Reference** | [PRD FR-5.3] before/after knowledge level |
| **Estimate** | 20 min |

**Definition of Done**:

- [ ] Bug investigation findings added to vault as new notes
- [ ] `hot.md` updated with fix details
- [ ] Before/after comparison documented in vault

**Independent Verification**:

```bash
ls -la obsidian/*.md  # New files should exist after investigation
```

---

### T7.07 — Orphan Detector Extension (FR-7.5)

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §11 Traceability Matrix — FR-7.5] |
| **PRD Reference** | [PRD-EXT] EXT-1 |
| **Estimate** | 45 min |

**Definition of Done**:

- [x] `OrphanDetector.detect(graph_data, min_connections)` returns `OrphanReport`
- [x] `Ex04SDK.detect_orphans` exposes operation
- [x] Unit tests: empty graph, isolated nodes, threshold edge cases
- [x] `tests/unit/services/analysis/test_orphan_detector.py` passes

**Independent Verification**:

```bash
uv run pytest tests/unit/services/analysis/test_orphan_detector.py -v
```

---

### T7.08 — Patch-Impact Analyzer Extension (FR-7.6)

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §11 Traceability Matrix — FR-7.6] |
| **PRD Reference** | [PRD-EXT] EXT-2 |
| **Estimate** | 45 min |

**Definition of Done**:

- [x] `PatchImpactAnalyzer.analyze(graph_data, changed_symbols, max_depth)` returns `ImpactReport`
- [x] `Ex04SDK.analyze_patch_impact` exposes operation
- [x] Unit tests: no changed symbols, cycle handling, depth limit
- [x] `tests/unit/services/analysis/test_patch_impact.py` passes

**Independent Verification**:

```bash
uv run pytest tests/unit/services/analysis/test_patch_impact.py -v
```

---

### T7.09 — Artifact Provenance and ArtifactStore

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §4.1 End-to-End Workflow] |
| **PRD Reference** | [PRD-AP] |
| **Estimate** | 30 min |

**Definition of Done**:

- [x] `ArtifactStore` implements overwrite protection
- [x] `RunManifest` schema covers all PRD-AP fields
- [x] Sanitizer removes secrets and personal paths
- [x] `artifacts/manifests/` directory committed with fixture

**Independent Verification**:

```bash
uv run pytest tests/unit/shared/test_artifact_store.py -v
ls artifacts/manifests/
```

---

### T7.10 — Deterministic Fixtures and Walkthrough Notebook

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P1 |
| **PLAN Reference** | [PLAN §4.1 End-to-End Workflow] |
| **PRD Reference** | [PRD §8 Deliverables] |
| **Estimate** | 60 min |

**Definition of Done**:

- [x] Fixture vault in `obsidian/` with `index.md` and `hot.md`
- [x] Fixture investigation result in `artifacts/runs/fixture-001/`
- [x] Walkthrough notebook `notebooks/walkthrough.ipynb` loads committed evidence
- [x] Notebook remains viewable without a paid provider

**Independent Verification**:

```bash
ls obsidian/ && ls artifacts/runs/
uv run jupyter nbconvert --to notebook --execute notebooks/walkthrough.ipynb 2>/dev/null || echo "nbconvert optional"
```

---
