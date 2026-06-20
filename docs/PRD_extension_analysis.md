# PRD — Graph-Analysis Extensions

| Field | Value |
|---|---|
| **Requirement ID** | PRD-EXT |
| **Parent PRD** | [docs/PRD.md](PRD.md) §5.7 (FR-7.4–7.6) |
| **Status** | Active |
| **Date** | 2026-06-20 |

---

## Purpose

Define contracts for original graph-analysis extensions that add analytical value
beyond the minimum comparison experiment.

Two extensions are implemented:
1. **EXT-1**: Orphan / weakly-connected-component detection (FR-7.5)
2. **EXT-2**: Graph-based patch-impact analysis (FR-7.6)

---

## EXT-1: Orphan Detection

### Requirement ID: FR-7.5

### Inputs

| Input | Type | Description |
|---|---|---|
| `graph_data` | `GraphData` | Parsed Graphify output |
| `min_connections` | `int` | Threshold below which a node is orphan-candidate (default 0) |

### Outputs

| Output | Type | Description |
|---|---|---|
| `OrphanReport` | dataclass | List of orphan nodes, weak components, summary |

### OrphanReport Schema

```python
@dataclass
class OrphanNode:
    name: str
    kind: str
    file_path: str
    connection_count: int
    source_anchor: str  # "file:start-end"

@dataclass
class WeakComponent:
    component_id: int
    members: list[str]
    size: int

@dataclass
class OrphanReport:
    orphan_nodes: list[OrphanNode]
    weak_components: list[WeakComponent]
    total_entities: int
    orphan_count: int
    weak_component_count: int
    threshold_used: int
    limitations: list[str]
```

### Invariants

- Low connectivity does not imply a defect; the report states this explicitly.
- `source_anchor` uses relative paths.
- An isolated node (degree 0) is always included when `min_connections=0`.

### Acceptance Criteria

- [ ] `OrphanDetector.detect(graph_data, min_connections)` returns `OrphanReport`.
- [ ] Report is exposed via `Ex04SDK.detect_orphans(graph_data, min_connections)`.
- [ ] Unit tests cover: empty graph, fully connected, isolated nodes, threshold edge cases.
- [ ] Output saved to `artifacts/runs/<run-id>/orphan_report.json`.

---

## EXT-2: Patch-Impact Analysis

### Requirement ID: FR-7.6

### Inputs

| Input | Type | Description |
|---|---|---|
| `graph_data` | `GraphData` | Parsed Graphify output |
| `changed_symbols` | `list[str]` | Names of changed entities (from patch) |
| `max_depth` | `int` | BFS traversal depth limit (default 3) |

### Outputs

| Output | Type | Description |
|---|---|---|
| `ImpactReport` | dataclass | Direct + transitive dependents, impact paths, limitations |

### ImpactReport Schema

```python
@dataclass
class ImpactedNode:
    name: str
    kind: str
    file_path: str
    depth: int
    path_from_changed: list[str]
    source_anchor: str

@dataclass
class ImpactReport:
    changed_symbols: list[str]
    direct_dependents: list[ImpactedNode]
    transitive_dependents: list[ImpactedNode]
    affected_test_files: list[str]
    max_depth_used: int
    impact_paths: list[list[str]]
    limitations: list[str]
```

### Invariants

- Graph reachability alone does not prove runtime impact; the report states this.
- `max_depth` caps BFS; nodes beyond depth are not included.
- `affected_test_files` contains only nodes whose `kind == "test"` or `file_path` contains `/test`.

### Acceptance Criteria

- [ ] `PatchImpactAnalyzer.analyze(graph_data, changed_symbols, max_depth)` returns `ImpactReport`.
- [ ] Report is exposed via `Ex04SDK.analyze_patch_impact(graph_data, changed_symbols, max_depth)`.
- [ ] Unit tests cover: no changed symbols, changed symbol not in graph, depth=0, cycle detection.
- [ ] Output saved to `artifacts/runs/<run-id>/impact_report.json`.

---

## Failure Behavior

| Condition | Behavior |
|---|---|
| `graph_data` empty | Return empty report with `limitations` noting empty graph |
| `changed_symbols` not in graph | Return report with empty dependents; log warning |
| Cycle in graph | BFS handles via visited set; no infinite loop |

---

## Security Constraints

- No absolute paths in output; all file references are relative to target root.
- Extension implementations do not make external API calls.

---

## Testing Strategy

- Unit tests for each extension in `tests/unit/services/analysis/`.
- Fixture graph with known topology to verify deterministic output.
- Edge cases: empty graph, single node, cycle, deep traversal.

---

## Evidence Requirements

- `tests/unit/services/analysis/test_orphan_detector.py` passes.
- `tests/unit/services/analysis/test_patch_impact.py` passes.
- Extension SDK operations documented in README with example output.

---

## Alternatives Considered

| Alternative | Reason rejected |
|---|---|
| Dynamic diff (FR-7.4) | Less analytically valuable without real pre/post runs |
| Leiden community detection | Requires external library; connected-components is sufficient |

---

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-06-20 | Initial creation for Phase 6-7 extensions |
