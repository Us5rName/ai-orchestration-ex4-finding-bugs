<!-- GENERATED FROM CANONICAL DOCUMENTATION - DO NOT EDIT DIRECTLY -->

# 9. Configuration Schema

[Back to Home](./Home.md)

All configuration is externalized per [PRD NFR-4] and [PRD §6].

### 9.1 `config/setup.json`

```json
{
    "project": {
        "name": "ex04",
        "version": "1.00"
    },
    "provider": {
        "name": "openai",
        "model": "gpt-4o-mini",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": null
    },
    "graphify": {
        "graph_home": "./graph-home",
        "output_subdir": "graphify-out"  # Grphify always writes to <target>/graphify-out/
    },
    "vault": {
        "output_dir": "./obsidian"
    },
    "agent": {
        "max_iterations": 5,
        "max_suspects": 5,
        "context_window_tokens": 8000
    },
    "comparison": {
        "naive_file_limit": 20,
        "guided_context_limit": 4000
    },
    "paths": {
        "target_codebase": "./graph-home/.graphify/repos/andela/buggy-python",
        "reports_dir": "./reports",
        "artifacts_dir": "./artifacts"
    }
}
```

### 9.2 `config/rate_limits.json`

```json
{
    "openai": {
        "requests_per_minute": 60,
        "requests_per_day": 10000,
        "retry_attempts": 3,
        "retry_delay_seconds": 5
    },
    "anthropic": {
        "requests_per_minute": 50,
        "requests_per_day": 5000,
        "retry_attempts": 3,
        "retry_delay_seconds": 5
    }
}
```

### 9.3 `.env-example`

```bash
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_BASE_URL=https://api.anthropic.com
```

---
