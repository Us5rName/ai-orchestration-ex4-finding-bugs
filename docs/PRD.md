# Product Requirements Document (PRD) — EX04

| Field | Value |
|---|---|
| **Project** | EX04 — Reverse Engineering, Debugging & Token-Efficient Agentic AI |
| **Version** | 1.00 |
| **Course** | AI Orchestration, שנה 3 |
| **Instructor** | ד"ר יורם סגל |
| **Author** | Lahav |
| **Date** | 2026-06-19 |
| **Status** | Draft |

---

## Table of Contents

1. [Product Overview](#1-product-overview)
   1.1. [Background](#11-background)
   1.2. [Problem Statement](#12-problem-statement)
   1.3. [Technology Choices](#13-technology-choices)
2. [Goals & Success Criteria](#2-goals--success-criteria)
   2.1. [Primary Goals](#21-primary-goals-derived-from-hw-3)
   2.2. [Success Criteria KPIs](#22-success-criteria-kpis)
3. [Research Questions](#3-research-questions)
4. [Scope](#4-scope)
   4.1. [In Scope](#41-in-scope)
   4.2. [Out of Scope](#42-out-of-scope)
5. [Functional Requirements](#5-functional-requirements)
   5.1. [Grphify Integration](#51-grphify-integration)
   5.2. [Obsidian Vault](#52-obsidian-vault)
   5.3. [Reverse Engineering](#53-reverse-engineering)
   5.4. [LangGraph Agent Workflow](#54-langgraph-agent-workflow)
   5.5. [Bug Fix & Before/After](#55-bug-fix--beforeafter)
   5.6. [Token Savings Comparison](#56-token-savings-comparison)
   5.7. [Original Extensions](#57-original-extensions)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [User Roles](#7-user-roles)
8. [Deliverables](#8-deliverables)
9. [Recommended Repository Structure](#9-recommended-repository-structure)
10. [Constraints & Assumptions](#10-constraints--assumptions)
    10.1. [Constraints](#101-constraints)
    10.2. [Assumptions](#102-assumptions)
11. [Glossary](#11-glossary)
12. [Revision History](#12-revision-history)

---

## 1. Product Overview

### 1.1 Background

This project is the implementation of **Assignment 04 (EX04)** of the AI Orchestration course.

> **HW [§1]**: "במטלה זו תתבקשו לחקור בסיס קוד Python שאינכם מכירים, לנתח אותו באמצעות Grphify, לייצג את הידע והממצאים בתוך כספת Obsidian, ולהפעיל סוכן AI מבוסס LangGraph או CrewAI לצורך ניתוח, איתור, תיקון והסבר של באגים."

The system demonstrates how **graph-based code representation**, **hierarchical documentation**, and **knowledge-based navigation** enable understanding of complex systems, performing reverse engineering, and saving tokens compared to naive raw code reading.

### 1.2 Problem Statement

> **HW [§1]**: "העבודה מבוססת על עקרונות מרכזיים מן ההרצאה: בעיית 'Lost in the Middle', דעיקת הקשר בחלונות קונטקסט ארוכים, שימוש ב-index.md וב-hot.md כדיפיי ניווט מרכזיים, והמרת בסיס קוד למבנה ידע גרפי שניתן לחקירה שיטתית."

When debugging an unfamiliar codebase, a naive agent that reads all source files blindly wastes tokens, context window, and API calls. By first constructing a **knowledge graph** (via Grphify) and navigating through an **Obsidian vault** (index.md → hot.md → component notes), an agent can pinpoint bugs with far fewer resources.

### 1.3 Technology Choices

| Dimension | Choice | Rationale |
|---|---|---|
| **Agent Framework** | **LangGraph** | HW [§6.1] recommends LangGraph for free/limited accounts: "העדיפו LangGraph אם אתם עובדים עם חשבון חינמי מוגבל, כי קל יותר לשלוט במספר הקריאות והשלבים." LangGraph provides explicit state machines with controllable step counts. |
| **Graph Extraction** | **Grphify** (graphifyy ≥ 0.8.40) | Required by HW [§5.1]. Produces `graph.json`, community clusters, and Obsidian vault files. |
| **Knowledge Base** | **Obsidian Vault** | Required by HW [§5.1]. Serves as the active knowledge space for navigation. |
| **Target Codebase** | **andela/buggy-python** | Chosen from HW [§2] base repositories. Contains buggy Python scripts designed to test bug identification and fixing capabilities. |
| **Package Manager** | **uv** | Per project rules — mandatory for all dependency management. |

---

## 2. Goals & Success Criteria

### 2.1 Primary Goals (derived from HW [§3])

| # | Goal | HW Citation |
|---|---|---|
| G1 | Build a Grphify graph representation of an unfamiliar Python codebase | HW [§5.1] |
| G2 | Construct a structured Obsidian vault with `index.md`, `hot.md`, and component documentation | HW [§5.1] |
| G3 | Perform reverse engineering: extract architectural block diagram and OOP schema | HW [§5.2] |
| G4 | Build and execute a LangGraph agent for graph-guided bug investigation, identification, and explanation | HW [§5.3] |
| G5 | Fix the identified bug with before/after evidence at both code and knowledge levels | HW [§5.4] |
| G6 | Prove token savings: compare naive baseline vs. graph-guided approach | HW [§5.5] |
| G7 | Implement at least one original extension beyond minimum requirements | HW [§5.6] |

### 2.2 Success Criteria (KPIs)

| KPI | Target |
|---|---|
| Token savings (graph-guided vs. naive) | ≥ 30% reduction in input tokens |
| File reads (graph-guided vs. naive) | ≥ 50% reduction in files read |
| Iterations to root cause | ≤ 3 investigation rounds |
| Bug correctly identified and fixed | Yes — passing test after fix |
| Obsidian vault completeness | `index.md` + `hot.md` + ≥ 2 component notes |
| Reverse engineering deliverables | ≥ 1 architectural block diagram + ≥ 1 OOP schema |
| LangGraph workflow | ≥ 3 distinct nodes with clear state transitions |
| Test coverage | ≥ 85% (project standard) |
| Ruff violations | 0 (project standard) |
| Max file length | ≤ 150 lines (project standard) |

---

## 3. Research Questions

> **HW [§4]**: "במהלך העבודה יש להתייחס במפורש לשאלות הבאות כחלק מן התיעוד."

The following research questions will be answered as part of the project deliverables (README, reports, Obsidian notes):

| # | Question | HW Reference |
|---|---|---|
| RQ1 | What is the actual architecture of the project, and what was discovered that wasn't obvious at first glance? | HW [§4] |
| RQ2 | Which components, modules, classes, or functions are the most central in the system? | HW [§4] |
| RQ3 | Where are the complexity hotspots, shared responsibilities, or "God Nodes"? | HW [§4] |
| RQ4 | How can an architectural block schema and OOP schema be extracted when original documentation is sparse? | HW [§4] |
| RQ5 | How was the bug identified, what was the root cause, and which steps led to it? | HW [§4] |
| RQ6 | What was the advantage of the graph representation and Obsidian navigation vs. linear file reading? | HW [§4] |
| RQ7 | How did the graph-guided AI agent save tokens or reduce unnecessary code reads? | HW [§4] |
| RQ8 | What additional improvements, extensions, or agent mechanisms would be added next? | HW [§4] |

---

## 4. Scope

### 4.1 In Scope

The system will:

1. **Graphify the target codebase** — Run Grphify on `andela/buggy-python` to produce `graph.json`, community clusters, and initial Obsidian notes.

2. **Build an Obsidian vault** — Create a structured knowledge base with:
   - `index.md` — Central entry describing system structure and main navigation paths (HW [§5.1])
   - `hot.md` — Focused context page for the critical bug investigation area (HW [§5.1])
   - Additional Markdown pages documenting key components, tests, findings, suspects, and fix process (HW [§5.1])

3. **Reverse engineer the codebase** — Extract and document:
   - Architectural block diagram describing main system parts and data/control flow between them (HW [§5.2])
   - OOP schema describing classes, usage relationships, composition, inheritance, wrapping, or relevant object patterns (HW [§5.2])

4. **Build a LangGraph debugging agent** with the following workflow nodes:
   - **Knowledge Load** — Load Grphify graph + Obsidian vault into agent context
   - **Bug Analysis** — Analyze bug reports and failed tests using graph knowledge
   - **Suspect Ranking** — Identify candidate modules/functions using graph centrality and proximity
   - **Code Inspection** — Fetch and analyze only the relevant code snippets (not the entire codebase)
   - **Root Cause Identification** — Determine the exact cause of the bug
   - **Fix Generation** — Propose and apply the code fix
   - **Verification** — Run tests to confirm the fix

5. **Fix a real bug** in the target codebase with clear before/after evidence at both code and knowledge levels (HW [§5.4]).

6. **Prove token savings** by running and comparing two scenarios:
   - **Naive baseline**: Agent reads raw source files without focus (HW [§5.5])
   - **Graph-guided**: Agent navigates through Grphify, `index.md`, `hot.md`, and Obsidian pages (HW [§5.5])
   - Comparison metrics: tokens consumed, files read, iterations, quality/speed of reaching root cause (HW [§5.5])

7. **Implement original extensions** beyond minimum requirements (HW [§5.6]).

### 4.2 Out of Scope

| Item | Reason |
|---|---|
| Fixing multiple bugs | HW [§6.1]: "בחרו באג אחד קטן או בינוני, לא מערכת שלמה." |
| Analyzing the entire andela/buggy-python repo exhaustively | HW [§6.2]: "אל תבחרו יותר מדי באגים או פרויקט גדול מדי." |
| Sending all code to the LLM at once | HW [§6.2]: "אל תשלחו ל-LLM את כל הקוד בבת אחת." |
| CrewAI implementation | Chose LangGraph; CrewAI is an alternative in HW [§5.3] but not selected. |

---

## 5. Functional Requirements

### 5.1 Grphify Integration

| ID | Requirement | Priority |
|---|---|---|
| FR-1.1 | The system shall run Grphify on the target codebase (`andela/buggy-python`) to produce `graph.json` | Must |
| FR-1.2 | The system shall produce `index.md` as a central navigation page describing the codebase structure | Must |
| FR-1.3 | The system shall produce `hot.md` as a focused context page for the bug investigation area | Must |
| FR-1.4 | The Grphify output shall include community clustering of code entities | Should |
| FR-1.5 | The Grphify output shall identify entity relationships (imports, calls, dependencies) | Must |

### 5.2 Obsidian Vault

| ID | Requirement | Priority |
|---|---|---|
| FR-2.1 | The Obsidian vault shall serve as an "active knowledge space" not just a file collection (HW [§5.1]) | Must |
| FR-2.2 | `index.md` shall describe system structure and main navigation routes | Must |
| FR-2.3 | `hot.md` shall provide focused context for the critical bug area | Must |
| FR-2.4 | Additional notes shall document key components, tests, investigation findings, suspects, and fix process (HW [§5.1]) | Must |
| FR-2.5 | Notes shall be interconnected with internal links | Should |

### 5.3 Reverse Engineering

| ID | Requirement | Priority |
|---|---|---|
| FR-3.1 | Produce an architectural block diagram showing main system parts and flow between them (HW [§5.2]) | Must |
| FR-3.2 | Produce an OOP schema showing classes, usage, composition, inheritance, or relevant patterns (HW [§5.2]) | Must |
| FR-3.3 | Diagrams must reflect engineering understanding, not just folder/file structure (HW [§5.2]) | Must |

### 5.4 LangGraph Agent Workflow

| ID | Requirement | Priority |
|---|---|---|
| FR-4.1 | The agent shall be built using LangGraph with a state-machine workflow | Must |
| FR-4.2 | The agent MUST operate in a graph-guided approach: first rely on Grphify outputs and Obsidian pages, then request relevant code snippets (HW [§5.3]) | Must |
| FR-4.3 | The workflow must define each step's/agent's role and context reduction mechanisms for efficiency (HW [§5.3]) | Must |
| FR-4.4 | The agent shall investigate, identify, and explain the bug | Must |
| FR-4.5 | The agent shall propose and apply a fix | Must |
| FR-4.6 | The agent shall verify the fix through test execution | Must |

### 5.5 Bug Fix & Before/After

| ID | Requirement | Priority |
|---|---|---|
| FR-5.1 | Perform a real code fix after bug identification (HW [§5.4]) | Must |
| FR-5.2 | Clearly show: what was the problem, why it occurred, what change was made, how fix success was verified (HW [§5.4]) | Must |
| FR-5.3 | Show before/after status at the knowledge level: which pages, nodes, links, or insights were added to Obsidian after investigation and fix (HW [§5.4]) | Must |
| FR-5.4 | Show what changed in the understanding of the architecture (HW [§5.4]) | Should |

### 5.6 Token Savings Comparison

| ID | Requirement | Priority |
|---|---|---|
| FR-6.1 | Implement a naive baseline where the agent works on many raw files without sufficient focus (HW [§5.5]) | Must |
| FR-6.2 | Implement a graph-guided mode where the agent works through Grphify, `index.md`, `hot.md`, and Obsidian pages (HW [§5.5]) | Must |
| FR-6.3 | Compare and report: tokens consumed, files/units read, iterations/rounds, and quality/speed of reaching root cause and fix (HW [§5.5]) | Must |

### 5.7 Original Extensions

| ID | Requirement | Priority |
|---|---|---|
| FR-7.1 | Implement at least one original extension beyond minimum requirements (HW [§5.6]) | Must |
| FR-7.2 | Candidate extension: Rank suspect nodes by centrality and proximity to failed tests (HW [§5.6]) | Should |
| FR-7.3 | Candidate extension: Architecture comparison before/after fix using graphs or schemas (HW [§5.6]) | Could |

---

## 6. Non-Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| NFR-1 | Test coverage ≥ 85% (project standard) | Must |
| NFR-2 | Zero Ruff lint violations (project standard) | Must |
| NFR-3 | No file exceeds 150 lines (project standard) | Must |
| NFR-4 | All configuration externalized to `config/*.json` or `.env` (project standard) | Must |
| NFR-5 | All business logic flows through SDK layer (project standard) | Must |
| NFR-6 | All external API calls flow through Gatekeeper (project standard) | Must |
| NFR-7 | Full docstrings on all modules, classes, functions (project standard) | Must |
| NFR-8 | Use `uv` for all dependency management (project standard) | Must |
| NFR-9 | DRY — no duplicated logic across 2+ files (project standard) | Must |

---

## 7. User Roles

| Role | Description |
|---|---|
| **Developer/Student** | Primary user — builds, runs, and demonstrates the system for the assignment |
| **Grader** | Evaluates the submission against HW [§7-10] deliverables and expectations |

---

## 8. Deliverables

> **HW [§7]**: "ההגשה תהיה מאגר GitHub מלא, הכולל לכל הפחות:"

| # | Deliverable | HW Reference |
|---|---|---|
| D1 | Complete Python solution code | HW [§7] |
| D2 | LangGraph agent workflow implementation | HW [§7] |
| D3 | Grphify outputs (`graph.json`, `GRAPH_REPORT.md`, etc.) | HW [§7] |
| D4 | Complete Obsidian vault with linked Markdown pages, including `index.md` and `hot.md` | HW [§7] |
| D5 | Bug analysis report: problem description, root cause, investigation process, and fix | HW [§7] |
| D6 | Token comparison report between baseline and graph-guided | HW [§7] |
| D7 | Architectural block diagram | HW [§7] |
| D8 | OOP schema | HW [§7] |
| D9 | Before/after proof for code fix and system understanding | HW [§7] |
| D10 | Documentation of extensions and original ideas | HW [§7] |
| D11 | README.md with all HW [§8] requirements (description, research questions, architecture, workflow, Grphify/Obsidian usage, reverse engineering, bug/fix, before/after, token comparison, extensions, run instructions, visual elements) | HW [§8] |

---

## 9. Recommended Repository Structure

> **HW [§9]**: "מבנה אפשרי למאגר ההגשה"

Adapted to project standards:

```
code/
├── pyproject.toml
├── uv.lock
├── README.md
├── ex04.md                       # Homework specification
├── config/
│   └── rate_limits.json          # API rate limit configuration
├── src/
│   └── ex04/
│       ├── __init__.py
│       ├── shared/
│       │   ├── __init__.py
│       │   ├── version.py        # Global version 1.00
│       │   └── gatekeeper.py     # API gatekeeper
│       └── sdk/
│           └── sdk.py            # Single SDK entry point
├── obsidian/                     # Obsidian vault
│   ├── index.md
│   ├── hot.md
│   └── ... (component notes)
├── graph-home/                   # Grphify workspace
│   └── .graphify/
│       └── repos/
│           └── andela/
│               └── buggy-python/
├── reports/                      # Analysis reports
│   ├── bug_analysis.md
│   └── token_comparison.md
├── artifacts/                    # Generated artifacts
│   └── graph.json
├── tests/
│   └── ...
└── docs/
    ├── PRD.md                    # This document
    ├── PLAN.md                   # Architecture plan
    └── TODO.md                   # Task tracking
```

---

## 10. Constraints & Assumptions

### 10.1 Constraints

| # | Constraint | Source |
|---|---|---|
| C1 | Must use LangGraph or CrewAI | HW [§5.3] |
| C2 | Must use Grphify for graph extraction | HW [§5.1] |
| C3 | Must build Obsidian vault with `index.md` + `hot.md` | HW [§5.1] |
| C4 | Must choose a bug from one of the three specified base repositories | HW [§2] |
| C5 | Agent must be graph-guided (Grphify → Obsidian → code snippets), not naive | HW [§5.3] |
| C6 | Must demonstrate token savings with quantitative comparison | HW [§5.5] |
| C7 | Submission must be a complete GitHub repository | HW [§7] |

### 10.2 Assumptions

| # | Assumption |
|---|---|
| A1 | The `andela/buggy-python` repository contains at least one identifiable, fixable bug |
| A2 | Grphify can successfully analyze the target codebase and produce `graph.json` |
| A3 | The available LLM API quota is sufficient for both baseline and graph-guided runs |
| A4 | The target codebase is small enough to analyze within project time constraints (HW [§6.1]) |

---

## 11. Glossary

| Term | Definition |
|---|---|
| **Grphify** | Tool for extracting knowledge graphs from codebases, producing `graph.json`, community clusters, and Obsidian-compatible notes |
| **Obsidian Vault** | Collection of interconnected Markdown files serving as an active knowledge base |
| **`index.md`** | Central navigation page in the Obsidian vault describing the codebase structure |
| **`hot.md`** | Focused context page for the critical area under investigation (bug area) |
| **LangGraph** | Framework for building stateful, multi-actor applications with LLMs using explicit state machines |
| **Lost in the Middle** | Phenomenon where LLMs lose track of important information in the middle of long context windows |
| **Graph-Guided** | Approach where the agent first consults the knowledge graph and documentation before reading raw code |
| **Naive Baseline** | Approach where the agent reads raw source files without graph guidance |
| **God Node** | A code entity (class/function) with excessive responsibilities and connections |
| **Root Cause** | The fundamental origin of a bug, as opposed to its symptoms |

---

## 12. Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.00 | 2026-06-19 | Lahav | Initial PRD creation |
