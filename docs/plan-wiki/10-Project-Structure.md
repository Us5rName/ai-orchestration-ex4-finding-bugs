# 10. Project Structure (Final)

[← Back to Home](./Home.md) | [Prev: Configuration Schema](./09-Configuration-Schema.md) | [Next: Traceability Matrix →](./11-Traceability-Matrix.md)

---

```
code/
├── pyproject.toml
├── uv.lock
├── README.md
├── ASSIGNMENT.md                 # Homework specification
├── .env-example                  # Secret placeholders
├── config/
│   ├── setup.json                # Application configuration
│   └── rate_limits.json          # API rate limits
├── src/
│   └── ex04/
│       ├── __init__.py
│       ├── sdk/
│       │   └── sdk.py            # Single SDK entry point (DI)
│       ├── services/
│       │   ├── graph/
│       │   │   ├── __init__.py
│       │   │   ├── interface.py  # [ADR-005] Contract for parallel dev
│       │   │   ├── runner.py     # [PRD FR-1.1] Grphify execution
│       │   │   ├── parser.py     # [PRD FR-1.1] Graph parsing
│       │   │   └── analyzer.py   # [PRD FR-1.4-1.5] Graph analysis
│       │   ├── vault/
│       │   │   ├── __init__.py
│       │   │   ├── interface.py  # [ADR-005] Contract for parallel dev
│       │   │   ├── builder.py    # [PRD FR-2.2-2.3] Vault creation
│       │   │   ├── navigator.py  # [PRD FR-2.5] Vault navigation
│       │   │   └── note_manager.py  # [PRD FR-2.4] Note management
│       │   ├── agent/
│       │   │   ├── __init__.py
│       │   │   ├── interface.py  # [ADR-005] Contract for parallel dev
│       │   │   ├── workflow.py   # [PRD FR-4.1] LangGraph assembly
│       │   │   ├── state.py      # [PRD FR-4.3] State schema
│       │   │   └── nodes/
│       │   │       ├── __init__.py
│       │   │       ├── knowledge.py   # [PRD FR-4.2] Knowledge load
│       │   │       ├── analysis.py    # [PRD FR-4.4] Bug analysis
│       │   │       ├── suspect.py     # [PRD FR-4.4] Suspect ranking
│       │   │       ├── inspect.py     # [PRD FR-4.2] Code inspection
│       │   │       ├── rootcause.py   # [PRD FR-4.4] Root cause
│       │   │       ├── fix.py         # [PRD FR-4.5] Fix generation
│       │   │       └── verify.py      # [PRD FR-4.6] Verification
│       │   ├── analysis/
│       │   │   ├── __init__.py
│       │   │   ├── interface.py  # [ADR-005] Contract for parallel dev
│       │   │   ├── reverse_engineer.py  # [PRD FR-3.1-3.2]
│       │   │   ├── diagram_gen.py       # [PRD FR-3.3]
│       │   │   └── bug_report.py        # [PRD FR-5.2]
│       │   └── comparison/
│       │       ├── __init__.py
│       │       ├── interface.py  # [ADR-005] Contract for parallel dev
│       │       ├── naive_runner.py      # [PRD FR-6.1]
│       │       ├── graph_guided_runner.py  # [PRD FR-6.2]
│       │       ├── metrics.py           # [PRD FR-6.3]
│       │       └── report_gen.py        # [PRD FR-6.3]
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── interface.py    # ProviderInterface ABC
│       │   ├── openai_provider.py
│       │   ├── anthropic_provider.py
│       │   └── factory.py      # ProviderFactory
│       └── shared/
│           ├── __init__.py
│           ├── gatekeeper.py   # API Gatekeeper [PRD NFR-6]
│           ├── config.py       # Config Manager [PRD NFR-4]
│           ├── version.py      # Version 1.00 [PRD NFR]
│           ├── token_tracker.py # Token tracking
│           └── types.py        # Shared data types
├── obsidian/                     # Obsidian vault
├── graph-home/                   # Grphify workspace
│   ├── .graphify/
│   │   └── repos/
│   │       └── andela/
│   │           └── buggy-python/
│   └── graphify-out/             # Grphify output (graph.json, GRAPH_REPORT.md, etc.)
├── reports/                      # Analysis reports
├── tests/
│   ├── unit/
│   └── integration/
└── docs/
    ├── PRD.md
    ├── PLAN.md                   # This document
    └── TODO.md
```

---

**Navigation**: [← Back to Home](./Home.md) | [Prev: Configuration Schema](./09-Configuration-Schema.md) | [Next: Traceability Matrix →](./11-Traceability-Matrix.md)
