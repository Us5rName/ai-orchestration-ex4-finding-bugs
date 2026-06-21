# PRD — Graph-Guided Bug Investigation

| Field | Value |
|---|---|
| **Requirement ID** | PRD-GGI |
| **Parent PRD** | [docs/PRD.md](PRD.md) §5.4 (FR-4.x), §5.5 (FR-5.x) |
| **Status** | Active |
| **Date** | 2026-06-20 |

---

## Purpose

Define the contract for graph-guided context acquisition: how the agent selects,
ranks, and navigates source entities using the Graphify graph and Obsidian vault
before asking the LLM to diagnose a bug.

---

## Scope

Covers: graph context construction, vault navigation protocol, source-anchor
linking, ranked-suspect generation, and the integration with the LangGraph agent.

Out of scope: LangGraph node internals, Graphify CLI invocation, vault build logic.

---

## Inputs

| Input | Type | Description |
|---|---|---|
| `bug_report` | `str` | Natural-language bug description |
| `graph_data` | `GraphData` | Parsed Graphify output with entities and relationships |
| `vault_path` | `Path` | Root of generated Obsidian vault |

---

## Outputs

| Output | Type | Description |
|---|---|---|
| `InvestigationResult` | dataclass | Diagnosis, suspects, patch, gate status |
| Source anchors | `list[str]` | `file_path:line_start–line_end` references |
| Ranked suspects | `list[Suspect]` | Entities by centrality score |

---

## Contracts

- Graph entities used must have `file_path` and `line_range` populated (source-anchored).
- Vault notes read must be traceable to vault path (index.md → hot.md → component note).
- The set of entities selected must come exclusively from `graph_data` — no filesystem scan.
- Source-anchor format: `<relative_path>:<start>-<end>` (relative to target root).

---

## Invariants

- The graph is read-only during investigation.
- Vault is read-only during investigation (post-fix update is a separate step).
- `suspected_files` must be a subset of entities in `graph_data`.
- Confidence score is in range [0.0, 1.0].

---

## Failure Behavior

| Condition | Behavior |
|---|---|
| `graph_data` is None | Fall back to vault-only or return result with `limitations` set |
| `vault_path` is None | Omit vault context; log limitation |
| No entities above centrality threshold | Return top-N regardless of threshold |
| Provider unavailable | Return `InvestigationResult` with `telemetry_available=False` |

---

## Security Constraints

- Vault path must not traverse outside target root.
- No absolute machine paths in output anchors.

---

## Measurable Acceptance Criteria

- [ ] `GraphGuidedRunner.run` uses entity names, relationships, and vault notes.
- [ ] `RunMetrics.files_read` counts only vault files used, not all vault files.
- [ ] Source anchors in result map to real line ranges in `graph_data.entities`.
- [ ] Tests confirm graph mode never reads from filesystem directly (only via graph_data).

---

## Alternatives Considered

| Alternative | Reason rejected |
|---|---|
| BFS traversal from bug-keyword match | Keyword matching is brittle; degree centrality is more stable |
| Read all vault notes | Defeats the purpose of focused navigation |

---

## Testing Strategy

- Unit tests: graph context builder with mock graph_data.
- Unit tests: vault context reader with fixture vault structure.
- Integration tests: runner with mock provider, verifying source anchors present.

---

## Evidence Requirements

- `tests/unit/services/comparison/test_graph_guided_runner.py` passes.
- At least one investigation result in `artifacts/runs/` contains non-empty `source_anchors`.

---

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-06-20 | Initial creation for Phase 7 finalization |
