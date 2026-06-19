# 2. Phase 1 — Foundation

[← Back to Home](./Home.md)

**Goal**: Establish project structure, configuration, and tooling. No business logic yet — pure infrastructure.

## Tasks

| Task | Link |
|---|---|
| T1.01 — Create Project Directory Structure | See below |
| T1.02 — Create Configuration Files | See below |
| T1.03 — Configure `pyproject.toml` | See below |
| T1.04 — Create Base Data Types | See below |
| T1.05 — Define All Service Interfaces (Contract Layer) | See below |
| T1.06 — Create Mock Implementations for All Services | See below |

---

### T1.01 — Create Project Directory Structure

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §10 Project Structure] |
| **PRD Reference** | [PRD §9 Recommended Repository Structure] |
| **Estimate** | 15 min |

**Definition of Done**:

- [ ] All directories from [PLAN §10] exist
- [ ] All `__init__.py` files created in Python packages
- [ ] Empty stub files created for every module listed in [PLAN §3 Module Design]

**Independent Verification**:

```bash
find src/ex04 -type f -name "*.py" | sort
# Expected: 30+ Python files matching PLAN §10 structure
```

---

### T1.02 — Create Configuration Files

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §9 Configuration Schema] |
| **PRD Reference** | [PRD NFR-4] no hardcoding |
| **Estimate** | 20 min |

**Definition of Done**:

- [ ] `config/setup.json` created with schema from [PLAN §9.1]
- [ ] `config/rate_limits.json` created with schema from [PLAN §9.2]
- [ ] `.env-example` created with placeholders from [PLAN §9.3]
- [ ] `.gitignore` updated to exclude `.env`, `__pycache__`, `.venv`

**Independent Verification**:

```bash
python3 -c "import json; json.load(open('config/setup.json'))"
python3 -c "import json; json.load(open('config/rate_limits.json'))"
# Both should exit 0 (valid JSON)
```

---

### T1.03 — Configure `pyproject.toml`

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §9 Configuration Schema] |
| **PRD Reference** | [PRD NFR-8] uv only, [PRD NFR-2] zero Ruff |
| **Estimate** | 20 min |

**Definition of Done**:

- [ ] `pyproject.toml` has Ruff linter configuration
- [ ] `pyproject.toml` has pytest configuration with coverage ≥ 85%
- [ ] Dependencies listed: `langgraph`, `graphifyy`, `openai`, `anthropic`, `pydantic`
- [ ] `uv sync` succeeds and creates virtual environment

**Independent Verification**:

```bash
uv sync
uv run ruff check --select E,F,W,I --no-fix .
uv run pytest --version
```

---

### T1.04 — Create Base Data Types

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.9 Shared Layer — types.py] |
| **PRD Reference** | [PRD NFR-7] docstrings |
| **Estimate** | 30 min |

**Definition of Done**:

- [ ] `src/ex04/shared/types.py` contains all data classes from [PLAN §3.9]:
  - `TokenMetrics`
  - `GraphData`, `Entity`, `Relationship`, `Community`
  - `RunMetrics`
  - `ComparisonMetrics`
  - `ProviderResponse`
  - `Suspect`
  - `InvestigationResult`
  - `ComparisonReport`
- [ ] Every class has full docstring with I/O contract
- [ ] All types use `dataclass` or `TypedDict`

**Independent Verification**:

```bash
uv run python -c "from ex04.shared.types import TokenMetrics, GraphData, RunMetrics; print('OK')"
# Should import without errors
```

---

### T1.05 — Define All Service Interfaces (Contract Layer)

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.1.1 Service Interfaces], [ADR-006] |
| **PRD Reference** | [PRD §5 Functional Requirements — contracts] |
| **Estimate** | 60 min |

**Why this task exists**: This is the **gate for parallel development**. Once these interfaces are defined, every other module can work against them independently — no one blocks anyone ([PLAN §3.1.2 Parallel Development Schedule]).

**Definition of Done**:

- [ ] `services/graph/interface.py` — `GraphServiceInterface` ABC with methods from [PLAN §3.3]
- [ ] `services/vault/interface.py` — `VaultServiceInterface` ABC with methods from [PLAN §3.4]
- [ ] `services/agent/interface.py` — `AgentServiceInterface` ABC with methods from [PLAN §3.5]
- [ ] `services/analysis/interface.py` — `AnalysisServiceInterface` ABC with methods from [PLAN §3.6]
- [ ] `services/comparison/interface.py` — `ComparisonServiceInterface` ABC with methods from [PLAN §3.7]
- [ ] Each interface only imports from `shared/types.py` (zero cross-service imports)
- [ ] Each method has docstring with I/O contract

**Independent Verification**:

```bash
uv run python -c "
from ex04.services.graph.interface import GraphServiceInterface
from ex04.services.vault.interface import VaultServiceInterface
from ex04.services.agent.interface import AgentServiceInterface
from ex04.services.analysis.interface import AnalysisServiceInterface
from ex04.services.comparison.interface import ComparisonServiceInterface
print('All interfaces importable — parallel work can begin')
"
```

---

### T1.06 — Create Mock Implementations for All Services

| Attribute | Value |
|---|---|
| **Status** | Not Started |
| **Priority** | P0 |
| **PLAN Reference** | [ADR-006 Contract-First Parallel Development] |
| **Estimate** | 60 min |

**Why this task exists**: Mock implementations let developers test their modules **before** real implementations exist. Agent developer can work against `MockGraphService` while Graph is still being built ([PLAN §3.1.2]).

**Definition of Done**:

- [ ] `tests/mocks/mock_graph_service.py` — implements `GraphServiceInterface` with synthetic data
- [ ] `tests/mocks/mock_vault_service.py` — implements `VaultServiceInterface` with synthetic data
- [ ] `tests/mocks/mock_agent_service.py` — implements `AgentServiceInterface` with canned responses
- [ ] `tests/mocks/mock_analysis_service.py` — implements `AnalysisServiceInterface` with canned outputs
- [ ] `tests/mocks/mock_comparison_service.py` — implements `ComparisonServiceInterface` with canned metrics
- [ ] `tests/mocks/mock_provider.py` — implements `ProviderInterface` with canned responses
- [ ] `tests/mocks/__init__.py` — exports all mocks
- [ ] Every mock passes basic sanity check (returns non-None, correct types)

**Independent Verification**:

```bash
uv run pytest tests/unit/test_mocks.py -v
# Verifies every mock implements its interface correctly
```

---

**Source**: Extracted from [`docs/TODO.md`](../TODO.md) §2.
