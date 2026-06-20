# 7. Phase 6 — Comparison Service

[← Back to Home](./Home.md)

**Goal**: Implement token comparison (naive vs. graph-guided).

## Tasks

| Task | Link |
|---|---|
| T6.01 — Naive Runner | See below |
| T6.02 — Graph-Guided Runner | See below |
| T6.03 — Metrics Calculator | See below |
| T6.04 — Comparison Report Generator | See below |
| T6.05 — Implement an Additional Extension | See below |

---

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
| **Status** | Partial |
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

### T6.05 — Implement an Additional Extension

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P1 |
| **PLAN Reference** | [PLAN §11 Traceability Matrix — FR-7.4/7.5/7.6] |
| **PRD Reference** | [PRD FR-7.4], [PRD FR-7.5], [PRD FR-7.6] |
| **Estimate** | 60 min |

**Goal**: Implement at least one of the three extension candidates beyond the minimum (FR-7.1–7.3). Choose the one that best fits the investigation findings.

**Options** (pick one):

| Option | FR | What to build |
|---|---|---|
| Dynamic diff | FR-7.4 | Compare `hot.md` + `graph.json` snapshots before/after fix; output a focused change summary |
| Orphan detection | FR-7.5 | Walk graph entities with no incoming edges; auto-generate documentation stubs for them |
| Impact report | FR-7.6 | Given a node name, traverse reverse-dependency edges and list all entities that would be affected by a change |

**Definition of Done**:

- [ ] Chosen extension is implemented in its mapped file ([PLAN §11])
- [ ] Extension is callable through the SDK
- [ ] Unit tests cover the happy path and at least one error case
- [ ] Output is included in `reports/` and referenced in README

**Independent Verification**:

```bash
uv run pytest tests/unit/services/comparison/test_diff_gen.py -v      # FR-7.4
# or
uv run pytest tests/unit/services/analysis/test_orphan_detector.py -v # FR-7.5
# or
uv run pytest tests/unit/services/analysis/test_impact_reporter.py -v # FR-7.6
```

---

**Source**: Extracted from [`docs/TODO.md`](../TODO.md) §7.
