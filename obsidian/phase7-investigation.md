# Phase 7 Investigation

## Root Cause

foo() stores state in a mutable default argument. The default list is shared between calls, so the second call returns two values.

## Linked Evidence

- [[phase7-before-after|Before/after vault note]]
- [[notes/snippets_foobar_foo|foo() graph node]]
- [[hot|Hot area]]
