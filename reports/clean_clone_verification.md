# Clean-Clone Verification Report

| Field | Value |
|---|---|
| Verified candidate SHA | `36a53a8` |
| Verification worktree | `/tmp/ex04-clean-clone-verify` |
| Date | 2026-06-20 |
| OS | Linux pop-os 6.17.4-76061704-generic x86_64 |
| Python | Python 3.12.13 |
| uv | uv 0.11.23 |

## Results

| Check | Command | Exit Code | Outcome |
|---|---|---|---|
| Dependency sync | `uv sync --all-groups` | 0 | Created isolated `.venv`; installed 85 packages |
| Keyless import | `uv run python -c "import ex04; print('import ok')"` | 0 | `import ok` |
| Ruff | `uv run ruff check .` | 0 | All checks passed |
| mypy | `uv run mypy src` | 0 | Success: no issues found in 76 source files |
| pytest | `uv run pytest --cov=src/ex04 --cov-report=term-missing --cov-fail-under=85` | 0 | 412 passed |
| Coverage | same pytest command | 0 | 97.16%; required 85% reached |
| Documentation sync | `uv run python scripts/check_docs_sync.py` | 0 | `plan-wiki` and `todo-wiki` in sync |
| Repository validation | `uv run python scripts/validate_repo.py` | 0 | Repository validation passed; checked 76 files |

All `uv run` commands printed a warning that the parent shell had
`VIRTUAL_ENV=/home/dev-pop-os/ai-orchestration-ex4-finding-bugs/.venv`; uv
ignored it and used the clean worktree `.venv`.

## Blocked Operations

| Operation | Status | Reason |
|---|---|---|
| Live Graphify extraction | Blocked | No target clone/live extraction was run in the clean worktree |
| Live provider investigation | Blocked | No valid provider credentials were available without disclosure |
| Real token/cost telemetry | Blocked | Requires live provider responses |
| Real screenshots | Blocked | No live UI/tool output was produced |

## Limitations

This report verifies the candidate before the report itself was committed. After
committing this report, report-only checks must be rerun in the main worktree.
