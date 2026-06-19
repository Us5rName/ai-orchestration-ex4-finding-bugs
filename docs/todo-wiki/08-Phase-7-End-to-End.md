# 8. Phase 7 — End-to-End Execution

[← Back to Home](./Home.md)

**Goal**: Run the full pipeline on the target codebase.

## Tasks

| Task | Link |
|---|---|
| T7.01 — Run Grphify on Target Codebase | See below |
| T7.02 — Build Obsidian Vault | See below |
| T7.03 — Execute Bug Investigation | See below |
| T7.04 — Execute Token Comparison | See below |
| T7.05 — Generate Reverse Engineering Artifacts | See below |
| T7.06 — Update Obsidian After Investigation | See below |

---

### T7.01 — Run Grphify on Target Codebase

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §4.1 End-to-End Workflow] |
| **PRD Reference** | [PRD G1] |
| **Estimate** | 30 min |

**Definition of Done**:

- [ ] Grphify runs on `graph-home/.graphify/repos/andela/buggy-python`
- [ ] `graph.json` produced in `artifacts/`
- [ ] `GRAPH_REPORT.md` produced
- [ ] Graph data validated (non-empty entities and relationships)

**Independent Verification**:

```bash
uv run python -c "from ex04.sdk import Ex04SDK; sdk = Ex04SDK.from_config('config/setup.json'); r = sdk.run_graphify('graph-home/.graphify/repos/andela/buggy-python'); print(r)"
ls -la artifacts/graph.json
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
- [ ] `reports/token_comparison.md` generated
- [ ] Report includes side-by-side metrics table

**Independent Verification**:

```bash
uv run python -c "from ex04.sdk import Ex04SDK; sdk = Ex04SDK.from_config('config/setup.json'); r = sdk.run_comparison('...'); print(r)"
cat reports/token_comparison.md
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

**Source**: Extracted from [`docs/TODO.md`](../TODO.md) §8.
