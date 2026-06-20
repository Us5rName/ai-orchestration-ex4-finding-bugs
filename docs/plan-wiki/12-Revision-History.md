# 12. Revision History

[← Back to Home](./Home.md) | [Prev: Traceability Matrix](./11-Traceability-Matrix.md)

---

| Version | Date | Author | Change |
|---|---|---|---|
| 1.00 | 2026-06-19 | evya1 | Initial architecture plan |
| 1.01 | 2026-06-19 | evya1 | Add FR-7.4/7.5/7.6 and NFR-10/C8/C9 to traceability matrix; update NFR range to NFR-10 ([PRD §5.7], [PRD §6], [PRD §10.1]) |
| 1.02 | 2026-06-20 | evya1 | Sync fix: add full_pipeline to Ex04SDK OOP Schema class diagram (§6) to match plan-wiki/06-OOP-Schema.md |
| 1.03 | 2026-06-20 | evya1 | Fill missing signatures in §3: added all 6 service interface ABCs (§3.1.1), all 7 agent node classes (§3.5), shared layer Gatekeeper/ConfigManager/TokenTracker signatures, and complete dataclass types (§3.9) — sourced from actual implementation code (Traceability: [CLAUDE.md §3 SDK-First], [CLAUDE.md §4 Golden Rules]) |
| 1.04 | 2026-06-20 | evya1 | Align §3.2/3.3/3.4/3.6/4.1/6/8.1 with actual implementation signatures and types. Traceability: [PLAN §3 Module Design], [PRD §5 Functional Requirements]. |
| 1.05 | 2026-06-20 | evya1 | Add concrete service facade files to §3.2 and §10 project structure, and document `Ex04SDK.from_config()` as the runtime wiring point for Phase 4 facades with Comparison deferred to Phase 6. Traceability: [PRD NFR-5], [PLAN §3.1 Contract-First Rule], [PLAN §3.2 SDK Module]. |
| 1.06 | 2026-06-20 | evya1 | Phase 4/5 integration: document compare_target(), generate_report(), identify_patterns(); add _comparison_inputs.py helper; document cumulative files_read and fix_diff in AgentState; add architecture boundary rules table (§3.2.2); update CLI command syntax in §8.2; add AnalysisServiceInterface.identify_patterns(). Traceability: [PRD FR-6.1], [PLAN §3.2 SDK Module], [PLAN §3.5 Agent Service]. |
| 1.07 | 2026-06-20 | evya1 | Add OrphanDetector (FR-7.5) API: `orphan_detector.py` to Analysis Service (§3.6), `OrphanReport` dataclass (§3.9), `detect_orphans()` to Ex04SDK (§3.2, §8.1), OrphanDetector class to OOP Schema (§6) (Traceability: [PRD FR-7.5], [TODO T6.05]) |

---

**Navigation**: [← Back to Home](./Home.md) | [Prev: Traceability Matrix](./11-Traceability-Matrix.md)
