# Comparison Report

> **Evidence Class: DETERMINISTIC** — Deterministic keyless evidence.

## Signed Delta Table

| Metric | Naive | Graph-guided | Delta |
|---|---:|---:|---:|
| Tokens | 662 | 222 | -440 |
| Files read | 1 | 2 | 1 |
| Iterations | 1 | 1 | 0 |
| Duration (s) | 0.001 | 0.001 | 0.000 |

## Correctness

| Mode | Parser | Gate |
|---|---|---|
| Naive | parsed_ok | not_requested |
| Graph-guided | parsed_ok | not_requested |

## Limitations


*Report SHA-256: `02283fb2f6329e1d5c89c53fd4ab0cedb9f5f1804b48327ac501a68eb9b6520b`*
