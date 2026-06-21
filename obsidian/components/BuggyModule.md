# BuggyModule

> **Evidence class**: Representative deterministic fixture
> **Source anchor**: `buggy.py:1-30`

## Overview

`BuggyModule` is the central class in `buggy.py`. It contains `process_data`
and `validate_input`, and is the entry point called from `main`.

## Graph Centrality

- Degree: 6 (highest in graph)
- Community: cluster_1 (with `process_data`, `validate_input`, `main`)
- Relationships: 4 outgoing, 2 incoming

## Methods

| Method | Lines | Degree | Bug-relevant |
|---|---|---|---|
| `process_data` | 14-28 | 4 | **Yes** — unchecked index access |
| `validate_input` | 5-12 | 2 | Partial — no empty-list check |
| `__init__` | 2-4 | 1 | No |

## Navigation

- [[../hot]] — Active investigation context
- [[../index]] — Vault home
