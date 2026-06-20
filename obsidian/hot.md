# Hot Notes — Active Bug Investigation

> **Evidence class**: Representative deterministic fixture

## Bug Summary

**Target**: `andela/buggy-python` — `buggy.py`
**Symptom**: `IndexError: list index out of range` when input list is empty
**Root cause hypothesis**: Loop uses `range(1, len(items))` but accesses `items[i-1]`
without guarding against empty list. When `items` is empty, `len(items) == 0`
and the range is `range(1, 0)` which is empty — but a separate check on line 14
accesses `items[0]` unconditionally.

## Suspected Symbols (ranked by centrality)

1. `process_data` — `buggy.py:14-28` — degree=4 (highest)
2. `validate_input` — `buggy.py:5-12` — degree=2
3. `BuggyModule` — `buggy.py:1-30` — degree=6

## Graph Evidence

```
BuggyModule --contains--> process_data
BuggyModule --contains--> validate_input
process_data --calls--> validate_input
main --calls--> process_data
```

## Proposed Fix

```python
# Before (buggy):
def process_data(items):
    first = items[0]  # IndexError when items is empty
    ...

# After (fixed):
def process_data(items):
    if not items:
        return []
    first = items[0]
    ...
```

## Source Anchors

- `buggy.py:14` — unchecked `items[0]` access
- `buggy.py:5-12` — `validate_input` does not check for empty list

## Before/After Knowledge

| Aspect | Pre-fix | Post-fix |
|---|---|---|
| Vault note | This file | Updated with fix confirmation |
| Graph | See `artifacts/pre_fix/` | See `artifacts/post_fix/` |
| Failure reproduced | Yes | N/A (fixture) |
