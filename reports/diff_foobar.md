# Before/After Diff: `snippets/foobar.py`

The fix replaces the mutable default list with a `None` sentinel and allocates a fresh list inside the function.

```diff
--- artifacts/runs/phase7-investigation/target/snippets/foobar.py:before
+++ artifacts/runs/phase7-investigation/target/snippets/foobar.py:after
@@ -5,6 +5,8 @@
 """
 
 
-def foo(bar=[]):
+def foo(bar=None):
+    if bar is None:
+        bar = []
     bar.append("baz")
     return bar
```
