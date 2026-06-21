# PRD — Graph-Analysis Extensions

| Field | Value |
|---|---|
| **Requirement ID** | PRD-EXT |
| **Parent PRD** | [docs/PRD.md](PRD.md) §5.7 (FR-7.4–7.6) |
| **Status** | Active |
| **Version** | 1.3 |
| **Date** | 2026-06-21 |

---

## Purpose

Define contracts for original graph-analysis extensions that add analytical value
beyond the minimum comparison experiment.

Two extensions are implemented:
1. **EXT-1**: Orphan / weakly-connected-component detection (FR-7.5) — **selected as the T6.05 additional extension**
2. **EXT-2**: Graph-based patch-impact analysis (FR-7.6) — additional implemented extension

**T6.05 Extension Selection**: FR-7.5 (Orphan Detection) is formally selected as the T6.05 additional extension. Core implementation and SDK exposure exist (T7.07 Done). Closure work remains: report persistence to `artifacts/`, deterministic JSON and Markdown reports, README documentation, explicit evidence mapping, and closure verification.

**T6.05 Current Status**: In Progress — core implementation and SDK exposure exist; report persistence, README documentation, explicit evidence mapping, and closure verification remain.

A planned third extension is described in §EXT-3 below:
3. **EXT-3**: Multi-Signal Weakness Detection (FR-7.7) — planned, not yet implemented

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

### Current (T7.07) Implementation Schema

The following schema is what the existing implementation exposes. It uses mutable lists and a
string source anchor. Do not assume it has immutability or stable-ID semantics it does not
currently possess.

```python
@dataclass
class OrphanNode:
    name: str          # display name (not a stable graph ID)
    kind: str
    file_path: str
    connection_count: int
    source_anchor: str  # "file:start-end" string, not a typed anchor

@dataclass
class WeakComponent:
    component_id: int   # traversal-order integer, not content-derived
    members: list[str]  # mutable list of display names
    size: int

@dataclass
class OrphanReport:
    orphan_nodes: list[OrphanNode]       # mutable list
    weak_components: list[WeakComponent] # mutable list
    total_entities: int
    orphan_count: int
    weak_component_count: int
    threshold_used: int
    limitations: list[str]               # mutable list
```

### Target (T6.05) Closure Schema

The following defines the immutable, typed report DTO that T6.05 must produce. The existing
analysis result (T7.07) shall be **adapted** into this schema — one canonical report model,
no competing public schemas, no second graph-parsing path.

```python
@dataclass(frozen=True, slots=True)
class EvidenceAnchor:
    file_path: str
    start_line: int | None
    end_line: int | None
    entity_id: str | None

@dataclass(frozen=True, slots=True)
class OrphanNodeView:
    entity_id: str           # stable graph node ID (separate from display label)
    label: str               # display name
    kind: str
    connection_count: int
    source_anchor: EvidenceAnchor | None

@dataclass(frozen=True, slots=True)
class WeakComponentView:
    component_id: str        # deterministic, content-derived ID (not traversal-order int)
    member_ids: tuple[str, ...] # immutable tuple of stable entity IDs
    size: int

@dataclass(frozen=True, slots=True)
class OrphanReport:
    orphan_nodes: tuple[OrphanNodeView, ...]       # immutable, deterministically ordered
    weak_components: tuple[WeakComponentView, ...] # immutable, ordered by component_id
    total_entities: int
    orphan_count: int
    weak_component_count: int
    threshold_used: int
    limitations: tuple[str, ...]  # immutable
```

**Key design decisions for T6.05**:
- `entity_id` is the stable graph node ID; `label` is the display name — they are separate fields.
- `EvidenceAnchor` replaces the opaque `"file:start-end"` string.
- All public collections are `tuple` (immutable). No mutable lists in the public DTO.
- `component_id` is content-derived and deterministic, not an integer assigned by traversal order.
- `orphan_nodes` ordered by `entity_id`; `weak_components` ordered by `component_id`; `member_ids` ordered by `entity_id`.
- `limitations` is an immutable tuple.
- JSON is canonical for persisted reports; Markdown is rendered from the canonical JSON, not independently authored.

**Compatibility and migration rule**:

```
The public SDK call shape (Ex04SDK.detect_orphans(graph_data, min_connections)) remains unchanged.
After T4.19, OrphanDetector shall delegate graph queries internally to GraphReader.
T6.05 adapts the existing analysis result into the immutable OrphanReport DTO.
There is one canonical public report schema — the target schema above.
No second graph-parsing path is created.
No competing public report schema is maintained alongside the target schema.
```

### Invariants

- Low connectivity does not imply a defect; the report states this explicitly.
- `source_anchor` uses relative paths.
- An isolated node (degree 0) is always included when `min_connections=0`.

### GraphReader Integration

After T4.19 is implemented, the `OrphanDetector` shall delegate graph queries internally to `GraphReader`.
The public SDK API remains `GraphData`-compatible for backward compatibility.

### Report Artifacts (Closure Work for T6.05)

| Artifact | Path | Description |
|---|---|---|
| JSON report | `artifacts/runs/<run-id>/reports/orphan_report.json` | Machine-readable canonical report |
| Markdown report | `artifacts/runs/<run-id>/reports/orphan_report.md` | Rendered from JSON |

Reports must include: stable entity IDs, deterministic ordering, typed source anchors, threshold used, limitations statement.

### T6.05 Traceability

```
T6.05 (additional extension) → FR-7.5 (Orphan Detection) → T7.07 (OrphanDetector implementation, Done)
```

### Acceptance Criteria

- [x] `OrphanDetector.detect(graph_data, min_connections)` returns `OrphanReport`. *(implemented in T7.07)*
- [x] Report is exposed via `Ex04SDK.detect_orphans(graph_data, min_connections)`. *(implemented in T7.07)*
- [x] Unit tests cover: empty graph, fully connected, isolated nodes, threshold edge cases. *(implemented in T7.07)*
- [ ] `OrphanDetector` delegates graph queries internally to `GraphReader` after T4.19. *(closure work — internal, not public API)*
- [ ] Output saved to `artifacts/runs/<run-id>/reports/orphan_report.json` using the target closure schema (immutable DTOs). *(closure work)*
- [ ] Markdown report saved to `artifacts/runs/<run-id>/reports/orphan_report.md` rendered from canonical JSON. *(closure work)*
- [ ] Reports use stable `entity_id` fields, typed `EvidenceAnchor`, deterministic ordering, immutable tuples. *(closure work)*
- [ ] Component IDs are content-derived and deterministic (not traversal-order integers). *(closure work)*
- [ ] Existing SDK call shape (`detect_orphans(graph_data, min_connections)`) preserved. *(backward compatibility)*
- [ ] Migration/regression tests verify the adapted target schema matches the existing test fixtures. *(closure work)*
- [ ] README documents real usage and artifact paths with actual examples. *(closure work — do not add before artifacts exist)*
- [ ] Evidence matrix updated with truthful evidence paths. *(closure work)*
- [ ] T6.05 → FR-7.5 → T7.07 traceability is explicit in all documentation. *(this document, TODO, PLAN)*

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

## EXT-3: Multi-Signal Weakness Detection (Planned)

### Requirement ID: FR-7.7

**Status**: Planned — not yet implemented. Implementation tracked as T4.20.

### Signals

| # | Signal | Notes |
|---|---|---|
| 1 | High-degree entity | Not automatically a cross-community bridge |
| 2 | Isolated / weakly connected component | Not automatically a defect |
| 3 | Ambiguous / unknown / low-confidence relationship | Missing confidence is unknown, not extracted fact |
| 4 | Broken dependency path | Missing source anchors are source-validation failures, not broken paths |
| 5 | Semantic duplicate | Python analysis must use AST, not regex over source text |

### Key Constraints

- Isolated-component logic shall reuse or adapt existing `OrphanDetector` rather than reimplementing connected-component analysis.
- The detector shall consume `GraphReader` rather than rebuilding graph indexes independently.
- No production hard-coded repository-specific node IDs, file paths, or symbol names.
- Every signal shall be independently testable and configurable.
- Findings shall not claim more than the measured evidence supports (no "this will fail at runtime" from graph reachability alone).

### Planned Package

```
src/ex04/services/analysis/weakness_detector/
    __init__.py
    models.py
    config.py
    detector.py
    ranking.py
    signals_graph.py
    signals_paths.py
    signals_source.py
```

---

## Alternatives Considered

| Alternative | Reason rejected |
|---|---|
| Dynamic diff (FR-7.4) | Less analytically valuable without real pre/post runs |
| Leiden community detection | Requires external library; connected-components is sufficient |
| Regex-based duplicate detection | Not AST-aware; false positives on Python code |

---

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-06-20 | Initial creation for Phase 6-7 extensions |
| 1.1 | 2026-06-21 | Formally select FR-7.5 as T6.05 extension; add T6.05 traceability and closure work definition; add GraphReader integration requirement; update EXT-1 acceptance criteria to distinguish implemented vs. closure-pending items; add §EXT-3 for planned FR-7.7 weakness detection (T4.20). Traceability: [PRD §5.7 FR-7.5, FR-7.7], [TODO T6.05, T7.07, T4.20]. |
| 1.2 | 2026-06-21 | Add version header field; sync date to 2026-06-21; EvidenceAnchor/RelationshipKey/WeaknessFinding typed immutable models referenced in EXT-3 — see PLAN.md for full model. Traceability: [PLAN §3.6 weakness_detector], [TODO T4.20].
| 1.3 | 2026-06-21 | Add explicit Current (T7.07) vs. Target (T6.05) OrphanReport schema distinction; define immutable closure DTOs (EvidenceAnchor, OrphanNodeView, WeakComponentView, OrphanReport) with design decisions; expand T6.05 acceptance criteria with stable IDs, typed anchors, immutable DTOs, deterministic ordering, GraphReader delegation, backward compatibility, migration tests; fix revision-history ordering. Traceability: [PRD §5.7 FR-7.5], [TODO T6.05]. |
