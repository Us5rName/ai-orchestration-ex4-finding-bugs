# Phase 7 Pipeline

```mermaid
flowchart LR
    target[Target snapshot] --> graph[Graphify graph]
    graph --> vault[Obsidian vault]
    graph --> agent[Graph-guided agent]
    vault --> agent
    agent --> report[Bug analysis]
    agent --> comparison[Token comparison]
    graph --> diagrams[Reverse-engineering diagrams]
```

The Phase 7 path is keyless and deterministic: Graphify supplies structural
context, the vault renders navigable notes, and the agent/comparison runners
use deterministic provider responses at the gatekeeper boundary.
