# PRD — Graph-Guided Bug Investigation

| Field | Value |
|---|---|
| **Requirement ID** | PRD-GGI |
| **Parent PRD** | [docs/PRD.md](PRD.md) §5.4 (FR-4.x), §5.5 (FR-5.x) |
| **Status** | Active |
| **Version** | 1.2 |
| **Date** | 2026-06-21 |

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
| `graph_data` | `GraphData \| None` | Parsed Graphify output with entities and relationships. When `None`, investigation falls back to vault-only mode and limitations are recorded. |
| `vault_path` | `Path` | Root of generated Obsidian vault |

---

## Outputs

| Output | Type | Description |
|---|---|---|
| `InvestigationResult` | dataclass | Diagnosis, suspects, patch, gate status |
| Source anchors | `list[str]` | `file_path:line_start–line_end` references |
| Ranked suspects | `list[Suspect]` | Entities by centrality score |

---

## GraphReader as Canonical Graph Access Boundary

All graph-guided context construction shall access graph data exclusively through `GraphReader` — a typed, read-only query facade over parsed `GraphData`. Consumers must not rebuild degree maps, adjacency indexes, or community groupings independently.

`GraphReader` exposes:
- `node(node_id)` — look up a single entity by stable ID
- `all_nodes()` — iterate all entities
- `edges_of(node_id, direction=...)` — direction-aware edge queries (outgoing / incoming / both)
- `top_n_by_degree(n)` — top-N entities by degree with deterministic tie-breaking
- `communities()` — group entities by community membership

**Degree vs. BFS**: Degree ranking and BFS/reachability solve different problems and neither globally replaces the other:
- Degree centrality identifies entities with many direct connections (potentially high-impact nodes).
- BFS/reachability discovers paths and transitive dependencies from a starting point.
- The claim that "degree centrality is simply more stable than BFS" is overstated and is removed from this document.

The context builder shall use degree ranking to prioritize candidate entities, and BFS where transitive dependency traversal is specifically needed.

## Contracts

- Graph entities used must have `file_path` and `line_range` populated (source-anchored).
- Vault notes read must be traceable to vault path (index.md → hot.md → component note).
- The set of entities selected must come exclusively from `graph_data` via `GraphReader` — no unbounded or undisclosed filesystem discovery. Every source read must result from a bounded navigation operation and be recorded in the evidence trace. No independent graph-index reconstruction.
- Source-anchor format: `<relative_path>:<start>-<end>` (relative to target root).
- Direction-aware edge queries must preserve relationship direction and type.

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
| `graph_data` is `None` | Fall back to vault-only context; record limitation "graph_data unavailable — graph-guided ranking disabled"; proceed with vault navigation only |
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
- [ ] Tests confirm graph mode never performs unbounded filesystem discovery — all source reads result from bounded navigation operations recorded in the evidence trace.

---

## Alternatives Considered

| Alternative | Reason rejected |
|---|---|
| BFS traversal as sole ranking strategy | BFS does not rank by importance; degree centrality is better for entity prioritization. However, BFS is retained for path-finding and transitive dependency queries — both are needed. |
| Read all vault notes | Defeats the purpose of focused navigation |
| Rebuild graph indexes in each consumer | Wastes computation; `GraphReader` centralizes index construction at construction time |

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
| 1.2 | 2026-06-21 | Tighten filesystem wording: "no unbounded or undisclosed filesystem discovery" replaces absolute prohibition; reconcile `graph_data` input type as `GraphData | None` with explicit fallback behavior; update acceptance criteria accordingly. Traceability: [PRD §5.4 FR-4.2], [PLAN ADR-007].
| 1.1 | 2026-06-21 | Add `GraphReader` as canonical graph access boundary; clarify degree vs. BFS semantics; remove overstated claim that degree centrality is simply more stable than BFS; add direction-aware edge query contract; prohibit independent graph-index reconstruction in consumers. Traceability: [PRD §5.4 FR-4.2], planned [PLAN ADR-007 GraphReader]. |
