<!-- GENERATED FROM CANONICAL DOCUMENTATION - DO NOT EDIT DIRECTLY -->

# 2. C4 Model

[Back to Home](./Home.md)

### 2.1 C4 Context Diagram

Shows the system in relation to external actors and systems.

```mermaid
graph TD
    USER[("Developer / Student")]
    SYSTEM[("EX04 Agentic Debugging System")]
    OBSIDIAN[("Obsidian Vault")]
    GRAPHHOME[("Grphify Workspace")]
    TARGET[("Target Codebase<br/>andela/buggy-python")]
    LLM[("LLM API Provider<br/>OpenAI / Anthropic")]

    USER -->|"Runs debugging workflow"| SYSTEM
    USER -->|"Views knowledge"| OBSIDIAN
    SYSTEM -->|"Read/Writes vault notes"| OBSIDIAN
    SYSTEM -->|"Extracts graph from code"| GRAPHHOME
    SYSTEM -->|"Analyzes unfamiliar code"| TARGET
    SYSTEM -->|"Makes API calls"| LLM
    GRAPHHOME -->|"Contains source code"| TARGET
```

**Justification**: [PRD §4.1 In Scope] defines the system as analyzing `andela/buggy-python`, building Grphify graphs, managing Obsidian vaults, and calling LLM APIs. [PRD §1.3 Technology Choices] lists all five external systems.

### 2.2 C4 Container Diagram

Shows the high-level containers and technology stack.

```mermaid
graph TD
    subgraph EX04["EX04 Application"]
        SDK[Ex04SDK<br/>Python]
        GRAPH_SVC[Graph Service<br/>Python + Grphify]
        VAULT_SVC[Vault Service<br/>Python]
        AGENT_SVC[Agent Service<br/>Python + LangGraph]
        ANALYSIS_SVC[Analysis Service<br/>Python]
        COMPARISON_SVC[Comparison Service<br/>Python]
        PROVIDER[Provider Abstraction<br/>Python ABC]
        GATE[API Gatekeeper<br/>Python]
    end

    subgraph External
        LLM_EXT[LLM API]
        OBSIDIAN_VAULT[Obsidian Vault<br/>Markdown files]
        GRAPHIFY_OUT[Grphify Output<br/>graph.json, GRAPH_REPORT.md]
        TARGET_CODE[Target Codebase<br/>Python source files]
    end

    SDK --> GRAPH_SVC
    SDK --> VAULT_SVC
    SDK --> AGENT_SVC
    SDK --> ANALYSIS_SVC
    SDK --> COMPARISON_SVC

    GRAPH_SVC --> GRAPHIFY_OUT
    GRAPH_SVC --> TARGET_CODE
    VAULT_SVC --> OBSIDIAN_VAULT
    AGENT_SVC --> PROVIDER
    AGENT_SVC --> GRAPHIFY_OUT
    AGENT_SVC --> OBSIDIAN_VAULT
    AGENT_SVC --> TARGET_CODE
    COMPARISON_SVC --> PROVIDER
    COMPARISON_SVC --> GRAPHIFY_OUT
    COMPARISON_SVC --> OBSIDIAN_VAULT

    PROVIDER --> LLM_EXT
    AGENT_SVC --> GATE
    COMPARISON_SVC --> GATE
```

**Justification**: Each container maps to a functional requirement group: [PRD §5.1 FR-1] → Graph Service, [PRD §5.2 FR-2] → Vault Service, [PRD §5.4 FR-4] → Agent Service, [PRD §5.6 FR-6] → Comparison Service.

### 2.3 C4 Component Diagram

Shows the internal components of the EX04 application.

```mermaid
graph TD
    subgraph SDK_Layer["SDK Layer"]
        SDK[Ex04SDK]
    end

    subgraph Graph_Service["Graph Service"]
        GRAPH_RUNNER[Graph Runner]
        GRAPH_PARSER[Graph Parser]
        GRAPH_ANALYZER[Graph Analyzer]
    end

    subgraph Vault_Service["Vault Service"]
        VAULT_BUILDER[Vault Builder]
        VAULT_NAVIGATOR[Vault Navigator]
        NOTE_MANAGER[Note Manager]
    end

    subgraph Agent_Service["Agent Service"]
        WORKFLOW_BUILDER[Workflow Builder]
        NODE_KNOWLEDGE[Knowledge Load Node]
        NODE_ANALYSIS[Bug Analysis Node]
        NODE_SUSPECT[Suspect Ranking Node]
        NODE_INSPECT[Code Inspection Node]
        NODE_ROOTCAUSE[Root Cause Node]
        NODE_FIX[Fix Generation Node]
        NODE_VERIFY[Verification Node]
    end

    subgraph Analysis_Service["Analysis Service"]
        RE_ENGINEER[Reverse Engineer]
        DIAGRAM_GEN[Diagram Generator]
        BUG_REPORT[Bug Reporter]
    end

    subgraph Comparison_Service["Comparison Service"]
        NAIVE_RUNNER[Naive Runner]
        GRAPH_GUIDED_RUNNER[Graph-Guided Runner]
        METRICS_CALC[Metrics Calculator]
        REPORT_GEN[Report Generator]
    end

    subgraph Provider_Layer["Provider Layer"]
        PROVIDER_IFACE[ProviderInterface]
    end

    subgraph Shared["Shared"]
        GATEKEEPER[API Gatekeeper]
        CONFIG_MGR[Config Manager]
        TOKEN_TRACKER[Token Tracker]
    end

    SDK --> GRAPH_RUNNER
    SDK --> VAULT_BUILDER
    SDK --> WORKFLOW_BUILDER
    SDK --> RE_ENGINEER
    SDK --> NAIVE_RUNNER
    SDK --> GRAPH_GUIDED_RUNNER

    GRAPH_RUNNER --> GRAPH_PARSER
    GRAPH_PARSER --> GRAPH_ANALYZER

    VAULT_BUILDER --> NOTE_MANAGER
    VAULT_BUILDER --> VAULT_NAVIGATOR

    WORKFLOW_BUILDER --> NODE_KNOWLEDGE
    NODE_KNOWLEDGE --> NODE_ANALYSIS
    NODE_ANALYSIS --> NODE_SUSPECT
    NODE_SUSPECT --> NODE_INSPECT
    NODE_INSPECT --> NODE_ROOTCAUSE
    NODE_ROOTCAUSE --> NODE_FIX
    NODE_FIX --> NODE_VERIFY

    RE_ENGINEER --> DIAGRAM_GEN
    RE_ENGINEER --> BUG_REPORT

    NAIVE_RUNNER --> PROVIDER_IFACE
    GRAPH_GUIDED_RUNNER --> PROVIDER_IFACE
    GRAPH_GUIDED_RUNNER --> GRAPH_ANALYZER
    GRAPH_GUIDED_RUNNER --> VAULT_NAVIGATOR
    GRAPH_GUIDED_RUNNER --> METRICS_CALC

    METRICS_CALC --> REPORT_GEN

    NODE_KNOWLEDGE --> GATEKEEPER
    NODE_ANALYSIS --> GATEKEEPER
    NODE_INSPECT --> GATEKEEPER
    NODE_FIX --> GATEKEEPER

    GATEKEEPER --> CONFIG_MGR
    GATEKEEPER --> TOKEN_TRACKER
```

**Justification**: Component decomposition follows [PRD §5.4 FR-4] for the LangGraph workflow with 7 nodes. The naive vs. graph-guided comparison aligns with [PRD §5.6 FR-6.1 to FR-6.3].

---
