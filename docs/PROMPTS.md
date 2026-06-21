# Phase 6–8 Prompt Registry — EX04

| Field | Value |
|---|---|
| **Version** | 1.0 |
| **Date** | 2026-06-20 |
| **Status** | Active |

All prompts in this registry are **newly authored** for Phase 6–8 reproducibility
unless explicitly marked otherwise. A prompt is marked "Used in Current Session"
only when it was actually executed during the 2026-06-20 finalization session.

---

## Traceability Table

| Prompt ID | Phase/Task | Purpose | Inputs | Output Schema | Status | Used in Current Session |
|---|---|---|---|---|---|---|
| P6-CMP-01 | P6/T6.08 | Controlled comparison design | Bug report, config | `ComparisonReport` | Template | No |
| P6-NAI-01 | P6/T6.01 | Naive investigation execution | Bug report, source files | `RunMetrics` | Template | No |
| P6-GGI-01 | P6/T6.02 | Graph-guided investigation execution | Bug report, graph, vault | `RunMetrics` | Template | No |
| P6-DIA-01 | P6/T6.06 | Structured diagnosis generation | Investigation context | `InvestigationResult` | Template | No |
| P6-GAT-01 | P6/T6.06 | Correctness gate review | Patch, test results | `GateOutput` | Template | No |
| P7-PRV-01 | P7/T7.09 | Artifact provenance validation | Manifest JSON | Pass/Fail | Template | No |
| P7-GRF-01 | P7/T7.02 | Graphify output interpretation | `graph.json` | Ranked entities | Template | No |
| P7-VLT-01 | P7/T7.02 | Obsidian vault navigation | vault path | Note excerpts | Template | No |
| P7-ORP-01 | P7/T7.07 | Orphan analysis interpretation | `OrphanReport` | Summary | Template | No |
| P7-IMP-01 | P7/T7.08 | Patch impact analysis | `ImpactReport` | Summary | Template | No |
| P8-EVD-01 | P8/T8.12 | Evidence and metrics audit | Run manifests | Audit summary | Template | No |
| P8-SYN-01 | P8/T8.10 | Documentation synchronization audit | Wikis vs. canonical | Sync status | Template | No |
| P8-REA-01 | P8/T8.08 | README evidence audit | README.md | Gap list | Template | No |
| P8-CLN-01 | P8/T8.12 | Clean-clone verification | Fresh clone results | Verification report | Template | No |
| P8-SUB-01 | P8/T8.05 | Final submission-readiness review | All artifacts | Readiness verdict | Template | No |

---

## Prompt Entries

---

### P6-CMP-01 — Controlled Comparison Design

| Field | Value |
|---|---|
| **Prompt ID** | P6-CMP-01 |
| **Title** | Controlled Comparison Design |
| **Phase** | 6 |
| **Task ID** | T6.08 |
| **Classification** | Prompt template |
| **Purpose** | Define and validate a fair apples-to-apples comparison between naive and graph-guided investigation modes. |
| **Intended agent/role** | Comparison orchestration service |
| **Required inputs** | Bug report, target snapshot path, graph_data, vault_path, shared config |
| **Expected structured output** | `ComparisonReport` with `ComparisonMetrics` and `narrative` |
| **Constraints** | Both modes must receive identical provider, model, system prompt, and token budget. |
| **Prohibited behavior** | Must not give graph data to naive mode. Must not give raw source dump to graph-guided mode. |
| **Acceptance criteria** | Fairness invariants pass in `test_fairness.py`. |
| **Version** | 1.0 — 2026-06-20 |
| **Status** | Template (not yet executed against live provider) |
| **Used in current session** | No |

**Prompt body**:
```
You are investigating a bug in a Python codebase.

Bug report:
{bug_report}

{context}

Respond with a structured JSON diagnosis:
{
  "root_cause": "<one-sentence root cause>",
  "suspected_files": ["<file>:<line>", ...],
  "suspected_symbols": ["<symbol_name>", ...],
  "proposed_patch": "<diff or description>",
  "confidence": <0.0–1.0>,
  "limitations": ["<limitation>", ...]
}

Do not fabricate token counts or test results.
```

---

### P6-NAI-01 — Naive Investigation Execution

| Field | Value |
|---|---|
| **Prompt ID** | P6-NAI-01 |
| **Title** | Naive Investigation Execution |
| **Phase** | 6 |
| **Task ID** | T6.01 |
| **Classification** | Prompt template |
| **Purpose** | Instruct the naive runner to diagnose a bug using only raw source file content. |
| **Intended agent/role** | `NaiveRunner` |
| **Required inputs** | `bug_report`, `source_files` (list of Path) |
| **Expected structured output** | `RunMetrics` |
| **Constraints** | No graph data, no vault notes, no pre-computed rankings. |
| **Prohibited behavior** | Must not access `graph_data`, `vault_path`, or any graph-derived context. |
| **Acceptance criteria** | `NaiveRunner.run` returns valid `RunMetrics` with `telemetry_available` set. |
| **Version** | 1.0 — 2026-06-20 |
| **Status** | Template |
| **Used in current session** | No |

**Prompt body**:
```
Find and fix this bug by reading the provided source files:

Bug report:
{bug_report}

Source files:
{source_context}

Respond with JSON matching the diagnosis schema.
```

---

### P6-GGI-01 — Graph-Guided Investigation Execution

| Field | Value |
|---|---|
| **Prompt ID** | P6-GGI-01 |
| **Title** | Graph-Guided Investigation Execution |
| **Phase** | 6 |
| **Task ID** | T6.02 |
| **Classification** | Prompt template |
| **Purpose** | Instruct the graph-guided runner to diagnose a bug using graph entities and vault navigation. |
| **Intended agent/role** | `GraphGuidedRunner` |
| **Required inputs** | `bug_report`, `graph_data`, `vault_path` |
| **Expected structured output** | `RunMetrics` |
| **Constraints** | Must use entity names, relationships, and vault notes (index.md, hot.md). |
| **Prohibited behavior** | Must not dump entire source codebase. Graph context must be traceable to source anchors. |
| **Acceptance criteria** | Source anchors present in result; `files_read` counts only vault notes used. |
| **Version** | 1.0 — 2026-06-20 |
| **Status** | Template |
| **Used in current session** | No |

**Prompt body**:
```
Investigate this bug using the code graph and knowledge vault:

Bug report:
{bug_report}

Graph entities (ranked by centrality):
{graph_context}

Vault notes:
{vault_context}

Respond with JSON matching the diagnosis schema. Include source anchors
(file:line-range) for each suspected location.
```

---

### P6-DIA-01 — Structured Diagnosis Generation

| Field | Value |
|---|---|
| **Prompt ID** | P6-DIA-01 |
| **Title** | Structured Diagnosis Generation |
| **Phase** | 6 |
| **Task ID** | T6.06 |
| **Classification** | Prompt template |
| **Purpose** | Extract a validated `InvestigationResult` from an LLM response. |
| **Intended agent/role** | Agent analysis node |
| **Required inputs** | LLM response text, graph context |
| **Expected structured output** | `InvestigationResult` with all required fields |
| **Constraints** | Must not accept empty `root_cause`. Confidence must be in [0.0, 1.0]. |
| **Prohibited behavior** | Must not fabricate token counts or test results. |
| **Acceptance criteria** | Output validates against `InvestigationResult` schema. |
| **Version** | 1.0 — 2026-06-20 |
| **Status** | Template |
| **Used in current session** | No |

---

### P6-GAT-01 — Correctness Gate Review

| Field | Value |
|---|---|
| **Prompt ID** | P6-GAT-01 |
| **Title** | Deterministic Correctness Gate Review |
| **Phase** | 6 |
| **Task ID** | T6.06 |
| **Classification** | Prompt template |
| **Purpose** | Validate that a candidate patch satisfies the correctness gate without weakening assertions. |
| **Intended agent/role** | `CorrectnessGate` |
| **Required inputs** | Patch diff, target snapshot path, test command |
| **Expected structured output** | `GateOutput` JSON |
| **Constraints** | Must run patch in isolated disposable copy, not in pristine snapshot. |
| **Prohibited behavior** | Must not delete tests or weaken assertions to obtain a pass. |
| **Acceptance criteria** | `GateOutput.final_verdict` is `pass` only when targeted test passes. |
| **Version** | 1.0 — 2026-06-20 |
| **Status** | Template |
| **Used in current session** | No |

---

### P7-PRV-01 — Artifact Provenance Validation

| Field | Value |
|---|---|
| **Prompt ID** | P7-PRV-01 |
| **Title** | Artifact Provenance Validation |
| **Phase** | 7 |
| **Task ID** | T7.09 |
| **Classification** | Prompt template |
| **Purpose** | Validate that a run manifest contains all required provenance fields and no secrets. |
| **Intended agent/role** | `ArtifactStore` / CI validation script |
| **Required inputs** | `RunManifest` JSON |
| **Expected structured output** | `{"valid": true/false, "missing_fields": [...], "sensitive_fields": [...]}` |
| **Constraints** | Must check for personal paths and API key patterns. |
| **Prohibited behavior** | Must not mark a manifest valid if `telemetry_available` is missing. |
| **Acceptance criteria** | All required fields present, no sensitive data detected. |
| **Version** | 1.0 — 2026-06-20 |
| **Status** | Template |
| **Used in current session** | No |

---

### P7-GRF-01 — Graphify Output Interpretation

| Field | Value |
|---|---|
| **Prompt ID** | P7-GRF-01 |
| **Title** | Graphify Output Interpretation |
| **Phase** | 7 |
| **Task ID** | T7.02 |
| **Classification** | Prompt template |
| **Purpose** | Interpret `graph.json` to extract ranked entity suspects and dependency paths for investigation. |
| **Intended agent/role** | Graph-guided runner context builder |
| **Required inputs** | `GraphData` (entities, relationships, communities) |
| **Expected structured output** | List of `{"name": str, "score": float, "source_anchor": str}` |
| **Constraints** | Score must come from centrality computation, not arbitrary ranking. |
| **Prohibited behavior** | Must not return all entities unranked. |
| **Acceptance criteria** | Top-N entities have non-null `source_anchor` values. |
| **Version** | 1.0 — 2026-06-20 |
| **Status** | Template |
| **Used in current session** | No |

---

### P7-VLT-01 — Obsidian Vault Navigation

| Field | Value |
|---|---|
| **Prompt ID** | P7-VLT-01 |
| **Title** | Obsidian Vault Navigation |
| **Phase** | 7 |
| **Task ID** | T7.02 |
| **Classification** | Prompt template |
| **Purpose** | Navigate vault from index.md → hot.md → component notes to extract focused bug context. |
| **Intended agent/role** | `VaultNavigator` |
| **Required inputs** | `vault_path`, bug keywords |
| **Expected structured output** | List of note excerpts with wikilink paths |
| **Constraints** | Must follow wikilink chain; must not read all notes indiscriminately. |
| **Prohibited behavior** | Must not return more than 5 notes per navigation pass. |
| **Acceptance criteria** | `navigate_from_index` returns non-empty list for non-empty vault. |
| **Version** | 1.0 — 2026-06-20 |
| **Status** | Template |
| **Used in current session** | No |

---

### P7-ORP-01 — Orphan Analysis Interpretation

| Field | Value |
|---|---|
| **Prompt ID** | P7-ORP-01 |
| **Title** | Orphan or Weak-Component Analysis |
| **Phase** | 7 |
| **Task ID** | T7.07 |
| **Classification** | Prompt template |
| **Purpose** | Interpret `OrphanReport` to identify disconnected modules and generate documentation stubs. |
| **Intended agent/role** | `OrphanDetector` / analysis service |
| **Required inputs** | `OrphanReport` |
| **Expected structured output** | Markdown summary of orphan nodes and weak components |
| **Constraints** | Must include disclaimer that low connectivity does not imply a defect. |
| **Prohibited behavior** | Must not claim that orphan nodes are definitely buggy. |
| **Acceptance criteria** | Output includes `limitations` section. |
| **Version** | 1.0 — 2026-06-20 |
| **Status** | Template |
| **Used in current session** | No |

---

### P7-IMP-01 — Patch Impact Analysis

| Field | Value |
|---|---|
| **Prompt ID** | P7-IMP-01 |
| **Title** | Patch Impact Analysis |
| **Phase** | 7 |
| **Task ID** | T7.08 |
| **Classification** | Prompt template |
| **Purpose** | Interpret `ImpactReport` to communicate transitive dependents and testing scope. |
| **Intended agent/role** | `PatchImpactAnalyzer` / analysis service |
| **Required inputs** | `ImpactReport`, changed symbols list |
| **Expected structured output** | Markdown impact summary with depth-annotated paths |
| **Constraints** | Must include disclaimer that reachability does not prove runtime impact. |
| **Prohibited behavior** | Must not claim that all transitive dependents are definitely broken. |
| **Acceptance criteria** | Output includes `limitations` section; paths are depth-annotated. |
| **Version** | 1.0 — 2026-06-20 |
| **Status** | Template |
| **Used in current session** | No |

---

### P8-EVD-01 — Evidence and Metrics Audit

| Field | Value |
|---|---|
| **Prompt ID** | P8-EVD-01 |
| **Title** | Evidence and Metrics Audit |
| **Phase** | 8 |
| **Task ID** | T8.12 |
| **Classification** | Prompt template |
| **Purpose** | Audit all committed artifacts to confirm truthfulness and classify each evidence item. |
| **Intended agent/role** | Reviewer / CI script |
| **Required inputs** | `artifacts/manifests/`, `reports/` |
| **Expected structured output** | List of `{"artifact": str, "evidence_class": str, "issues": [...]}` |
| **Constraints** | Every artifact must have an evidence class. No fabricated evidence. |
| **Prohibited behavior** | Must not classify a fixture as live evidence. |
| **Acceptance criteria** | All artifacts have non-null `evidence_class`. |
| **Version** | 1.0 — 2026-06-20 |
| **Status** | Template |
| **Used in current session** | No |

---

### P8-SYN-01 — Documentation Synchronization Audit

| Field | Value |
|---|---|
| **Prompt ID** | P8-SYN-01 |
| **Title** | Documentation Synchronization Audit |
| **Phase** | 8 |
| **Task ID** | T8.10 |
| **Classification** | Prompt template |
| **Purpose** | Verify that plan-wiki/Home.md and todo-wiki/Home.md match their canonical sources. |
| **Intended agent/role** | `scripts/check_docs_sync.py` |
| **Required inputs** | `docs/PLAN.md`, `docs/TODO.md`, `docs/plan-wiki/Home.md`, `docs/todo-wiki/Home.md` |
| **Expected structured output** | `{"in_sync": true/false, "out_of_sync_files": [...]}` |
| **Constraints** | Comparison must be byte-for-byte deterministic. |
| **Prohibited behavior** | Must not mark wikis in sync when canonical docs have changed. |
| **Acceptance criteria** | `check_docs_sync.py` exits 0 when wikis match generated output. |
| **Version** | 1.0 — 2026-06-20 |
| **Status** | Template |
| **Used in current session** | No |

---

### P8-REA-01 — README Evidence Audit

| Field | Value |
|---|---|
| **Prompt ID** | P8-REA-01 |
| **Title** | README Evidence Audit |
| **Phase** | 8 |
| **Task ID** | T8.08 |
| **Classification** | Prompt template |
| **Purpose** | Verify every factual claim in README.md maps to code, test, or committed artifact. |
| **Intended agent/role** | Reviewer / final check |
| **Required inputs** | `README.md`, `artifacts/`, `reports/`, test results |
| **Expected structured output** | List of `{"claim": str, "evidence": str, "status": "supported"/"unsupported"}` |
| **Constraints** | Percentage improvement claims require evidence proof. |
| **Prohibited behavior** | Must not mark a claim supported without a traceable artifact or test. |
| **Acceptance criteria** | All README factual claims have status "supported". |
| **Version** | 1.0 — 2026-06-20 |
| **Status** | Template |
| **Used in current session** | No |

---

### P8-CLN-01 — Clean-Clone Verification

| Field | Value |
|---|---|
| **Prompt ID** | P8-CLN-01 |
| **Title** | Clean-Clone Verification |
| **Phase** | 8 |
| **Task ID** | T8.12 |
| **Classification** | Prompt template |
| **Purpose** | Verify the final candidate branch installs and passes all keyless checks in a fresh worktree. |
| **Intended agent/role** | CI / submission reviewer |
| **Required inputs** | Branch SHA, fresh git worktree |
| **Expected structured output** | `reports/clean_clone_verification.md` |
| **Constraints** | Must record exact command outputs. Must not sanitize real failures. |
| **Prohibited behavior** | Must not claim success if `pytest --cov-fail-under=85` exits non-zero. |
| **Acceptance criteria** | Report committed; all keyless checks pass with 0 failures. |
| **Version** | 1.0 — 2026-06-20 |
| **Status** | Template |
| **Used in current session** | No |

---

### P8-SUB-01 — Final Submission-Readiness Review

| Field | Value |
|---|---|
| **Prompt ID** | P8-SUB-01 |
| **Title** | Final Submission-Readiness Review |
| **Phase** | 8 |
| **Task ID** | T8.05 |
| **Classification** | Prompt template |
| **Purpose** | Produce an evidence-based self-assessment of submission readiness. |
| **Intended agent/role** | Documentation reviewer |
| **Required inputs** | All P0 task statuses, test results, coverage, ruff, mypy, artifact index |
| **Expected structured output** | Structured self-assessment with: verified strengths, completed requirements, limitations, blocked ops, known risks |
| **Constraints** | Must not claim guaranteed full marks. Must not claim completion of blocked live work. |
| **Prohibited behavior** | Must not fabricate evidence. Must not claim submission-ready if any P0 is incomplete. |
| **Acceptance criteria** | All P0 tasks are Complete or explicitly reported as Blocked. |
| **Version** | 1.0 — 2026-06-20 |
| **Status** | Template |
| **Used in current session** | No |

---

## AI-Use Disclosure

| Category | Detail |
|---|---|
| **Prompts newly authored** | All 15 prompts above were authored for Phase 6–8 reproducibility on 2026-06-20. |
| **Prompts reconstructed** | None — all entries are templates created during this finalization, not post-hoc reconstructions. |
| **Prompts actually used** | None executed against a live provider in this session. All are Prompt templates. |
| **Tools assisting implementation** | Claude Code (claude-sonnet-4-6) assisted with implementation, documentation, and test generation. |
| **Tools assisting review** | Claude Code assisted with prohibited-reference audit and synchronization checks. |
| **Deterministic outputs** | All test results, coverage numbers, and ruff/mypy outputs are deterministic. |
| **Live operations blocked** | Graphify extraction on real target, live LLM provider runs, actual cost/token data — all blocked (no credentials in CI). |

---

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-06-20 | Initial Phase 6–8 prompt registry (15 entries, all templates) |
