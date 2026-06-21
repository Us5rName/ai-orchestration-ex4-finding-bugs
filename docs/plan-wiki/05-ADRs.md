<!-- GENERATED FROM CANONICAL DOCUMENTATION - DO NOT EDIT DIRECTLY -->

# 5. Architectural Decision Records (ADRs)

[Back to Home](./Home.md)

### ADR-001: LangGraph Over CrewAI

| Field | Value |
|---|---|
| **Status** | Accepted |
| **PRD Reference** | [PRD §1.3 Technology Choices] |
| **Context** | HW allows LangGraph or CrewAI. Need to choose one. |
| **Decision** | Use **LangGraph** as the agent workflow framework. |
| **Rationale** | HW [§6.1] explicitly recommends LangGraph for limited accounts: "העדיפו LangGraph אם אתם עובדים עם חשבון חינמי מוגבל, כי קל יותר לשלוט במספר הקריאות והשלבים." LangGraph provides explicit state machines with deterministic control flow, enabling precise token counting per step. |
| **Consequences** | LangGraph-specific code in Agent Service. CrewAI path not implemented. |

### ADR-002: Provider-Agnostic LLM Abstraction

| Field | Value |
|---|---|
| **Status** | Accepted |
| **PRD Reference** | [PRD §1.3 Technology Choices], [PRD §10.2 Assumptions A3] |
| **Context** | The system needs to call LLM APIs. Hardcoding a specific provider (e.g., OpenAI) couples the system to one vendor and complicates switching for comparison experiments. |
| **Decision** | Abstract all LLM interactions behind `ProviderInterface` (ABC). Concrete implementations per provider. `ProviderFactory` creates instances from config. |
| **Rationale** | Enables switching providers via configuration alone. Facilitates token comparison experiments ([PRD §5.6 FR-6]) where different providers might be tested. Supports [PRD §6 NFR-4] no-hardcoding principle. |
| **Consequences** | Slight overhead of abstraction layer. All LLM calls flow through Gatekeeper → ProviderInterface → concrete provider. |

### ADR-003: Grphify as External Tool, Not Library Import

| Field | Value |
|---|---|
| **Status** | Accepted |
| **PRD Reference** | [PRD §5.1 FR-1] |
| **Context** | Grphify is available as a CLI tool (`graphify`) and as an importable Python library (`from graphify.build import build_from_json`, etc.). It can be invoked via subprocess or imported directly. |
| **Decision** | Invoke Grphify as an external CLI tool via subprocess to build the initial graph. Parse its output files (`graph.json`, `GRAPH_REPORT.md`). The library API (`graphify.query`, `graphify.analyze`) may be used for programmatic graph queries after the graph is built. |
| **Rationale** | Running the initial graph build as a subprocess keeps Grphify's complex extraction pipeline isolated — its failures don't crash the main application. The existing project structure has `graph-home` as a Grphify workspace, suggesting CLI usage. After the graph exists, `graphify query` / `graphify path` / `graphify explain` can be called for targeted investigation. |
| **Consequences** | Graph Service must handle subprocess execution and output parsing. Graph data format depends on Grphify's output schema (`graphify-out/graph.json`). The Agent Service can optionally use `graphify query` for graph-guided investigation. |

### ADR-004: Separate Comparison as Independent Module

| Field | Value |
|---|---|
| **Status** | Accepted |
| **PRD Reference** | [PRD §5.6 FR-6.1 to FR-6.3] |
| **Context** | Token comparison requires running two complete workflows: naive and graph-guided. This could be embedded in the Agent Service or separated. |
| **Decision** | Implement as a separate `Comparison Service` with its own `NaiveRunner` and `GraphGuidedRunner`. |
| **Rationale** | Keeps the comparison experiment isolated and independently testable. Each runner can be executed separately for debugging. The MetricsCalculator provides clear separation of concerns. Aligns with [PRD §4.1 In Scope item 6]. |
| **Consequences** | Both runners need access to Provider layer and may duplicate some agent logic. Mitigated by sharing node implementations where possible. |

### ADR-005: Contract-First Parallel Development

| Field | Value |
|---|---|
| **Status** | Accepted |
| **PRD Reference** | [PRD §4.1 In Scope] — multiple independent services |
| **Context** | The architecture defines 5 domain services (Graph, Vault, Agent, Analysis, Comparison) with cross-dependencies. Without interface separation, developers working on Agent must wait for Graph and Vault implementations to be complete before they can start coding. |
| **Decision** | Every service exposes an `*Interface` ABC. All cross-module imports target only the interface. The SDK performs dependency injection at runtime. Interfaces are defined in Phase 2 — before any implementation begins. |
| **Rationale** | Enables fully parallel development: Agent developer works against `MockGraphService` and `MockVaultService` while the real implementations are built simultaneously. Zero blocking between teams. Also improves testability — every module is testable with mocks from day one. |
| **Consequences** | Slight overhead of maintaining interfaces. SDK becomes the sole wiring point. All `interface.py` files must be created before implementation phases begin ([TODO §2 Phase 1 — T1.04 defines all contracts]). |

### ADR-006: Markdown-Based Vault Over Obsidian API

| Field | Value |
|---|---|
| **Status** | Accepted |
| **PRD Reference** | [PRD §5.2 FR-2] |
| **Context** | Obsidian vault is essentially a directory of Markdown files with internal links. Obsidian has a desktop app and a community API plugin, but neither is required. |
| **Decision** | Treat the vault as a plain Markdown directory. Build notes programmatically as `.md` files with `[[wikilinks]]`. |
| **Rationale** | No runtime dependency on Obsidian software. The vault is readable by Obsidian when opened, but our system only needs to create and read Markdown files. Simpler, more portable, and fully testable. |
| **Consequences** | Cannot use Obsidian's graph view API or plugin ecosystem. Navigation is done by parsing Markdown links, not querying an Obsidian API. |

### ADR-007: GraphReader as Canonical Graph Read/Query Boundary

| Field | Value |
|---|---|
| **Status** | Accepted — implemented (T4.19a + T4.19 Done, commits b078da9 & 5011543) |
| **PRD Reference** | [PRD-GGI §GraphReader], [PRD §5.7 FR-7.7] |
| **Context** | Multiple consumers (graph analysis, weakness detection, orphan analysis, patch-impact analysis, graph-guided context construction, graph diff) each independently query graph data. Without a shared facade, each consumer rebuilds degree maps, adjacency indexes, and community groupings — duplicating computation and creating divergent behavior. |
| **Decision** | `GraphReader` is the canonical typed read-only boundary over parsed `GraphData`. All consumers must use `GraphReader` rather than rebuilding graph indexes independently. `GraphReader` accepts an existing `GraphData` directly, or a path-based constructor that delegates parsing to `GraphParser`. |
| **Rationale** | Centralizes index construction; eliminates redundant computation; ensures deterministic ordering and tie-breaking across all consumers; prevents a second raw-JSON graph parsing path. |
| **Consequences** | Every graph consumer must be updated to use `GraphReader` rather than accessing `GraphData` directly. `GraphReader` must preserve relationship direction, type, and parallel relationships. The existing `Entity` and `Relationship` types must be enriched (T4.19a) to carry stable IDs, confidence, weight, and source anchor before GraphReader can provide full contracts. |
| **Rejected alternatives** | (a) Each consumer builds its own indexes — rejected because of duplication and divergent behavior. (b) `GraphAnalyzer` as the query boundary — rejected because `GraphAnalyzer` performs higher-level analysis; a typed read boundary is a separate concern. |

### ADR-008: Experimental Parity Isolates Context Acquisition as Controlled Treatment

| Field | Value |
|---|---|
| **Status** | Accepted |
| **PRD Reference** | [PRD §5.6 FR-6.4], [PRD-CE §Controlled vs. Treatment] |
| **Context** | The comparison experiment must be scientifically defensible. Both modes must be identical in every respect except the variable being measured. Without explicit parity enforcement, subtle differences in provider configuration, retry policy, or telemetry conversion can contaminate results. |
| **Decision** | The context-acquisition strategy (and its resulting `ContextBundle`) is the sole intentional experimental treatment. All other execution parameters are controlled via a shared `InstrumentedCallService` and a deterministic `ParityFingerprint`. Comparison execution rejects mismatched fingerprints before provider calls. |
| **Rationale** | Makes token savings attributable only to the context strategy — not to differences in prompts, retry behavior, or telemetry recording. Enables falsifiability of the token-efficiency claim. |
| **Consequences** | Both modes must share the same `ApiGatekeeper` boundary, retry policy, budget ledger, trace event factory, correctness gate, and artifact schema. The parity fingerprint must be checked before provider calls. |
| **Rejected alternatives** | Claim parity merely because both paths call the same provider — rejected because subtle differences in system instructions, generation parameters, or retry behavior invalidate the comparison. |

### ADR-009: Self-Grade Scores Are Evidence-Derived and Subject to Mandatory Caps

| Field | Value |
|---|---|
| **Status** | Accepted |
| **PRD Reference** | [PRD §5.8 FR-8.2, FR-8.3], [PRD-SG §Score Calculation] |
| **Context** | A self-grade service could either (a) use pre-configured earned scores, or (b) derive scores from actual check results at run time. Option (a) allows a grade to remain high even when mandatory gates fail. |
| **Decision** | Rubric configuration defines maximum points and policies only — never pre-awarded earned scores. Earned points are computed from PASS/FAIL check results at run time. Mandatory-gate failures apply a score cap that reduces the final score below the raw rubric score. |
| **Rationale** | Makes the grade truthful and reproducible. A failing mandatory gate (e.g., correctness check) should visibly reduce the grade. Pre-configured scores are static; they cannot reflect the actual state of the repository. |
| **Consequences** | Configuration must be validated to reject `earned_points` or `awarded_points` fields. The score calculation pipeline is: check results → earned points → raw score → mandatory cap → final score. |
| **Rejected alternatives** | Pre-configured earned scores — explicitly rejected because the grade can remain high even when mandatory gates fail, making the self-assessment meaningless. |

---
