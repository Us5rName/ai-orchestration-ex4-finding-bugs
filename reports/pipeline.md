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
