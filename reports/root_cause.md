# Root Cause

foo() stores state in a mutable default argument. The default list is shared between calls, so the second call returns two values.

## Evidence

- Suspect: `snippets/foobar.py:8-10`
- Failure mode: repeated calls share the same default list instance.
- Verification: targeted post-fix assertion passed.
