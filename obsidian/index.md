# EX04 Investigation Vault — Index

> **Evidence class**: Representative deterministic fixture
> **Note**: This vault was built from the `andela/buggy-python` target.
> Live Graphify extraction is required for production use — see T7.01.

## Navigation

- [[hot]] — Bug-focused hot notes (active investigation context)
- [[components/BuggyModule]] — Primary suspect module

## Target

- **Repository**: andela/buggy-python
- **Selected bug**: Off-by-one error in loop boundary condition
- **Reproduction**: `python buggy.py` raises `IndexError` on empty input

## Research Questions Addressed

| # | Question | Status |
|---|---|---|
| RQ5 | Bug identification and root cause | Addressed in [[hot]] |
| RQ6 | Graph-guided vs. naive advantage | See `reports/token_comparison.md` |
| RQ7 | Token savings mechanism | Centrality ranking reduced files read |

## Graph Overview

Entities: 12 total (4 classes, 8 functions)
High-degree nodes: `BuggyModule` (degree=6), `process_data` (degree=4)
Communities: 3 clusters detected

## Wikilinks

- [[hot]]
- [[components/BuggyModule]]
