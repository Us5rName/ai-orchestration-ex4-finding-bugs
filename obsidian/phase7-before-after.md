# Phase 7 Before/After

## Before

`foo(bar=[])` reused the same list across calls.

## After

`foo(bar=None)` allocates a fresh list when the caller does not pass one.

## Verification

- Passed: `True`
- Report: `reports/bug_analysis.md`
