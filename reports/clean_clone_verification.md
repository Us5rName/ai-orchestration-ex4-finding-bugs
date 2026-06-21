# Clean-Clone Verification Report

| Field | Value |
|---|---|
| Verified candidate SHA | `5f363c2b28068c36e6abf10f047fe32e2a534a1d` |
| Date | 2026-06-21 |
| Python | Python 3.12.13 |
| uv | 0.11.23 |
| Evidence classification | deterministic |

## Results

| Check | Command | Exit Code | Result |
|---|---|---:|---|
| Dependency sync | `uv sync --all-groups` | 0 | 104 packages installed in clean `.venv` |
| Ruff | `uv run ruff check .` | 0 | All checks passed |
| mypy | `uv run mypy src/ex04 --ignore-missing-imports` | 0 | No issues in 93 source files |
| pytest + coverage | `uv run pytest --cov=src/ex04 --cov-report=term-missing --cov-fail-under=85` | 0 | 531 passed; 95.35% coverage |
| Repository validator | `uv run python scripts/validate_repo.py` | 0 | Validation PASSED; 93 files; 19 checks |
| Documentation sync | `uv run python scripts/check_docs_sync.py` | 0 | plan-wiki and todo-wiki in sync |
| Keyless import | `uv run python -c "from ex04.sdk import Ex04SDK; print('keyless import ok')"` | 0 | keyless import ok |
| CLI smoke | `uv run python -m ex04 --help` | 0 | CLI help rendered |
| Python file-size scan | `find src -type f -name '*.py' ...` | 0 | no source file over 150 lines |
| Artifact hashes | `find artifacts ... \| sha256sum` | 0 | hashes listed below |

The clean clone was created at `/tmp/ex04-clean-verify` from the local Git
object database with `git clone --no-local`, then checked out to the exact
candidate SHA. The parent shell exposed a `VIRTUAL_ENV` from the main workspace;
`uv` ignored it and created/used the clean clone `.venv`.

## Artifact Hashes

| SHA-256 | Artifact |
|---|---|
| `ef14d06c2d6bd83053fa4b2631ad66d113d3c38f6c66cdae39fc2fcbf58dc0c2` | `artifacts/manifests/fixture-001_manifest.json` |
| `e0b13f4d2094825374616c306831bb4b0554715a4c4f049202a2000c63f32709` | `artifacts/manifests/fixture-naive-001_manifest.json` |
| `3b9031095b400f480a268a6e2145fb0f8b7f664081b18ace047a159026806d54` | `artifacts/pre_fix/graphify-out/graph.json` |
| `7ab6274366e2d541ff34b63a7e66215b713ce4f885d8cdbbb43e8a4a351142a2` | `artifacts/pre_fix/provenance.json` |
| `ba41fb363df74ba8ae377848068a7b2cef9700a80af3501940f4631ccd5f6bdd` | `artifacts/runs/fixture-001/result.json` |

## Blocked Live Operations

| Operation | Status | Reason |
|---|---|---|
| Live provider-backed investigation | blocked | No valid provider credentials were available without disclosure. |
| Real token/cost telemetry | blocked | Requires live provider responses. |
| Graphify docs corpus extraction | blocked | Docs corpus extraction requires an API key; code-only extraction fixture remains deterministic. |
| Real screenshots | blocked | No live UI/tool workflow output was produced. |
