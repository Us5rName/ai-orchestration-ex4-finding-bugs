<!-- GENERATED FROM CANONICAL DOCUMENTATION - DO NOT EDIT DIRECTLY -->

# 1. Phase Overview

[Back to Home](./Home.md)

Each phase consists of **independent, verifiable tasks**. Tasks are independently verifiable and parallel by default, except where explicit task-level dependencies are documented. Tasks within a phase may run in parallel unless a task-level dependency is listed in the task definition or in [PLAN §3 Task Dependency Policy].

```mermaid
graph LR
    P1["Phase 1<br/>Foundation"] --> P2["Phase 2<br/>Shared Layer"]
    P2 --> P3["Phase 3<br/>Provider Layer"]
    P3 --> P4["Phase 4<br/>Services"]
    P4 --> P5["Phase 5<br/>SDK + CLI"]
    P5 --> P6["Phase 6<br/>Comparison"]
    P6 --> P7["Phase 7<br/>End-to-End"]
    P7 --> P8["Phase 8<br/>Final Check"]
```

| Phase | Deliverable | Independent Verification |
|---|---|---|
| **Phase 1** | Project structure, config, `.env` | `uv run ruff check` passes, structure matches [PLAN §10] |
| **Phase 2** | Shared layer fully tested | Unit tests for gatekeeper, config, version, types pass in isolation |
| **Phase 3** | Provider abstraction working | Mock-based tests verify `ProviderInterface` contract without real API |
| **Phase 4** | All services implemented | Each service testable with mocked dependencies |
| **Phase 5** | SDK orchestrates services | Integration test: SDK calls all services through mocks |
| **Phase 6** | Comparison produces metrics | Naive and guided runners produce comparable `RunMetrics` |
| **Phase 7** | Full pipeline executes | End-to-end test with real target codebase produces reports |
| **Phase 8** | Submission ready | [PRD §12 Final Checklist] passes |

---
