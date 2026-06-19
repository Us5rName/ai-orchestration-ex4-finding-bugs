# 11. Traceability Matrix

[← Back to Home](./Home.md) | [Prev: Project Structure](./10-Project-Structure.md) | [Next: Revision History →](./12-Revision-History.md)

---

Maps every PRD requirement to its architectural location:

| PRD Requirement | Module | File |
|---|---|---|
| FR-1.1 Grphify execution | Graph Service | `services/graph/runner.py` |
| FR-1.2 Parse graph.json | Graph Service | `services/graph/parser.py` |
| FR-1.3 Community clustering | Graph Service | `services/graph/analyzer.py` |
| FR-1.4 Entity relationships | Graph Service | `services/graph/parser.py` |
| FR-1.5 God Node detection | Graph Service | `services/graph/analyzer.py` |
| FR-2.1 Obsidian vault | Vault Service | `services/vault/builder.py` |
| FR-2.2 index.md | Vault Service | `services/vault/builder.py` |
| FR-2.3 hot.md | Vault Service | `services/vault/builder.py` |
| FR-2.4 Component notes | Vault Service | `services/vault/note_manager.py` |
| FR-2.5 Internal links | Vault Service | `services/vault/note_manager.py` |
| FR-3.1 Block diagram | Analysis Service | `services/analysis/diagram_gen.py` |
| FR-3.2 OOP schema | Analysis Service | `services/analysis/diagram_gen.py` |
| FR-3.3 Engineering understanding | Analysis Service | `services/analysis/reverse_engineer.py` |
| FR-4.1 LangGraph workflow | Agent Service | `services/agent/workflow.py` |
| FR-4.2 Graph-guided approach | Agent Service | `services/agent/nodes/knowledge.py` |
| FR-4.3 Context reduction | Agent Service | `services/agent/state.py` |
| FR-4.4 Bug investigation | Agent Service | `services/agent/nodes/analysis.py` |
| FR-4.5 Fix proposal | Agent Service | `services/agent/nodes/fix.py` |
| FR-4.6 Test verification | Agent Service | `services/agent/nodes/verify.py` |
| FR-5.1 Real code fix | Agent Service | `services/agent/nodes/fix.py` |
| FR-5.2 Before/after evidence | Analysis Service | `services/analysis/bug_report.py` |
| FR-5.3 Knowledge-level changes | Vault Service | `services/vault/note_manager.py` |
| FR-6.1 Naive baseline | Comparison Service | `services/comparison/naive_runner.py` |
| FR-6.2 Graph-guided mode | Comparison Service | `services/comparison/graph_guided_runner.py` |
| FR-6.3 Token comparison | Comparison Service | `services/comparison/metrics.py` |
| FR-7.1 Original extension | Agent Service | `services/agent/nodes/suspect.py` |
| NFR-1 85% coverage | All | `tests/` |
| NFR-2 Zero Ruff | All | `pyproject.toml` |
| NFR-3 150-line limit | All | All files ≤ 150 lines |
| NFR-4 No hardcoding | Shared | `shared/config.py`, `config/*.json` |
| NFR-5 SDK-first | SDK | `sdk/sdk.py` |
| NFR-6 Gatekeeper | Shared | `shared/gatekeeper.py` |
| NFR-7 Docstrings | All | All modules |
| NFR-8 uv only | All | `pyproject.toml`, `uv.lock` |
| NFR-9 DRY | All | Shared utilities |

---

**Navigation**: [← Back to Home](./Home.md) | [Prev: Project Structure](./10-Project-Structure.md) | [Next: Revision History →](./12-Revision-History.md)
