# 1. Architecture Overview

[← Back to Home](./Home.md) | [Next: C4 Model →](./02-C4-Model.md)

---

## 1.1 Design Philosophy

This system implements the requirements defined in **[PRD §2.1 Goals G1-G7]** and **[PRD §5 Functional Requirements FR-1 through FR-7]**. The architecture is designed around three core principles:

| Principle | Description | PRD Reference |
|---|---|---|
| **Provider-Agnostic** | LLM provider is abstracted behind `ProviderInterface` — no hardcoded vendor coupling | Aligns with [PRD §10.1 Constraints] flexibility needs |
| **SDK-First** | All business logic flows through a single SDK entry point; CLI/REST are thin presentation layers | [PRD §5.4 FR-4.1] workflow definition |
| **Modular Independence** | Each service is an independent building block with validated I/O contracts | Supports [PRD §2.2 KPIs] for testability and coverage |

## 1.2 High-Level Architecture

```mermaid
graph TD
    subgraph Consumers["External Consumers"]
        CLI[CLI]
        REST[REST API]
    end

    subgraph SDK["SDK Layer - Single Entry Point"]
        SDK[Ex04SDK]
    end

    subgraph Domain["Domain Services"]
        GRAPH[Graph Service]
        VAULT[Vault Service]
        AGENT[Agent Service]
        ANALYSIS[Analysis Service]
        COMPARISON[Comparison Service]
    end

    subgraph Providers["Provider Abstraction Layer"]
        PI[ProviderInterface]
        OPENAI[OpenAI Provider]
        ANTHROPIC[Anthropic Provider]
    end

    subgraph Infra["Infrastructure"]
        GATE[API Gatekeeper]
        CONFIG[Config Manager]
        FS[File System]
    end

    CLI --> SDK
    REST --> SDK

    SDK --> GRAPH
    SDK --> VAULT
    SDK --> AGENT
    SDK --> ANALYSIS
    SDK --> COMPARISON

    GRAPH --> FS
    VAULT --> FS
    AGENT --> PI
    COMPARISON --> PI

    PI --> OPENAI
    PI --> ANTHROPIC

    AGENT --> GATE
    COMPARISON --> GATE

    GATE --> CONFIG
```

---

**Navigation**: [← Back to Home](./Home.md) | [Next: C4 Model →](./02-C4-Model.md)
