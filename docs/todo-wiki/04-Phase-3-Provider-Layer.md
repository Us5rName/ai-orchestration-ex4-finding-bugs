<!-- GENERATED FROM CANONICAL DOCUMENTATION - DO NOT EDIT DIRECTLY -->

# 4. Phase 3 — Provider Layer

[Back to Home](./Home.md)

**Goal**: Provider-agnostic LLM abstraction. Fully testable with mocks — no real API calls needed for unit tests.

### T3.01 — Implement Provider Interface

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.8 Provider Layer — interface.py], [ADR-002] |
| **PRD Reference** | [PRD §1.3] no vendor lock-in |
| **Estimate** | 20 min |

**Definition of Done**:

- [ ] `ProviderInterface` ABC with `chat()` and `count_tokens()` abstract methods
- [ ] `ProviderResponse` dataclass with fields: `text`, `input_tokens`, `output_tokens`, `model`, `provider`, `timestamp`
- [ ] `Message` TypedDict with `role` and `content`
- [ ] Full docstrings on all symbols

**Independent Verification**:

```bash
uv run python -c "from ex04.providers.interface import ProviderInterface, ProviderResponse, Message; print('OK')"
```

---

### T3.02 — Implement OpenAI Provider

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.8 Provider Layer — openai_provider.py] |
| **Estimate** | 60 min |

**Definition of Done**:

- [ ] `OpenAIProvider` implements `ProviderInterface`
- [ ] `chat()` maps to OpenAI API, returns `ProviderResponse` with token counts
- [ ] `count_tokens()` uses tiktoken library
- [ ] API key loaded from environment variable (configurable)
- [ ] Error handling: retries on rate limit, timeout, API errors
- [ ] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/providers/test_openai_provider.py -v --cov=ex04.providers.openai_provider --cov-report=term-missing
# Uses mocked OpenAI client — no real API calls
```

---

### T3.03 — Implement Anthropic Provider

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P1 |
| **PLAN Reference** | [PLAN §3.8 Provider Layer — anthropic_provider.py] |
| **Estimate** | 60 min |

**Definition of Done**:

- [ ] `AnthropicProvider` implements `ProviderInterface`
- [ ] `chat()` maps to Anthropic API, returns `ProviderResponse` with token counts
- [ ] `count_tokens()` uses Anthropic tokenizer
- [ ] API key loaded from environment variable (configurable)
- [ ] Error handling: retries on rate limit, timeout, API errors
- [ ] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/providers/test_anthropic_provider.py -v --cov=ex04.providers.anthropic_provider --cov-report=term-missing
# Uses mocked Anthropic client — no real API calls
```

---

### T3.04 — Implement Provider Factory

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.8 Provider Layer — factory.py] |
| **Estimate** | 30 min |

**Definition of Done**:

- [ ] `ProviderFactory.create(name, config)` returns appropriate `ProviderInterface`
- [ ] Supports `openai` and `anthropic` provider names
- [ ] Raises `ValueError` for unknown provider
- [ ] Raises `RuntimeError` if required API key missing
- [ ] File ≤ 150 lines

**Independent Verification**:

```bash
uv run pytest tests/unit/providers/test_factory.py -v --cov=ex04.providers.factory --cov-report=term-missing
# Tests factory routing without real API calls
```

---

### T3.05 — Provider Layer `__init__.py`

| Attribute | Value |
|---|---|
| **Status** | Done |
| **Priority** | P0 |
| **PLAN Reference** | [PLAN §3.8 Provider Layer] |
| **Estimate** | 5 min |

**Independent Verification**:

```bash
uv run python -c "from ex04.providers import ProviderInterface, ProviderFactory; print('OK')"
```

---
