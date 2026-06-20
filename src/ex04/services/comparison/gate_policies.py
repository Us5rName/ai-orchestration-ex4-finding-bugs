"""AST-based policy checks and directory helpers for the correctness gate.

Detects test deletion, assertion weakening, and test disabling without
executing any code — pure static analysis via ast.parse().

Traceability: [TODO P7-R01], [Correction #7]
"""

from __future__ import annotations

import ast
import re
from pathlib import Path


def count_test_functions(source: str) -> int:
    """Count test functions (def test_*) in source via ast.parse."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0
    return sum(
        1 for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
    )


def count_assertions(source: str) -> int:
    """Count assert statements in source via ast.parse."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0
    return sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assert))


def has_skip_markers_added(pre: str, post: str) -> bool:
    """Return True if @pytest.mark.skip was added in post vs. pre."""
    return len(re.findall(r"@pytest\.mark\.skip", post)) > len(
        re.findall(r"@pytest\.mark\.skip", pre)
    )


def check_test_file_integrity(
    pre_source: str, post_source: str
) -> tuple[bool, bool, bool, list[str]]:
    """Check one test file for deletions, weakening, and disabling.

    Returns:
        (tests_ok, assertions_ok, no_new_skips, issues)
    """
    pre_t, post_t = count_test_functions(pre_source), count_test_functions(post_source)
    pre_a, post_a = count_assertions(pre_source), count_assertions(post_source)
    new_skips = has_skip_markers_added(pre_source, post_source)
    issues: list[str] = []
    if post_t < pre_t:
        issues.append(f"Test count decreased: {pre_t} → {post_t}.")
    if post_a < pre_a:
        issues.append(f"Assertion count decreased: {pre_a} → {post_a}.")
    if new_skips:
        issues.append("@pytest.mark.skip added — tests disabled.")
    return post_t >= pre_t, post_a >= pre_a, not new_skips, issues


def extract_changed_paths(patch_diff: str) -> list[str]:
    """Extract file paths modified by a unified diff patch."""
    return re.findall(r"^\+\+\+ b/(.+)", patch_diff, re.MULTILINE)


def check_path_policy(
    changed_paths: list[str], allowed: list[str], prohibited: list[str]
) -> list[str]:
    """Return list of violations against path policies."""
    violations: list[str] = []
    for path in changed_paths:
        if prohibited and any(pat in path for pat in prohibited):
            violations.append(f"Patch modifies prohibited path: {path}")
        if allowed and not any(pat in path for pat in allowed):
            violations.append(f"Patch modifies non-allowed path: {path}")
    return violations


def snapshot_python_files(directory: Path) -> dict[str, str]:
    """Read all Python files in directory into a relative-path→source dict."""
    return {
        str(f.relative_to(directory)): f.read_text(encoding="utf-8", errors="replace")
        for f in directory.rglob("*.py")
    }


def check_test_dir_integrity(
    pre: dict[str, str], post: dict[str, str]
) -> tuple[bool, bool, list[str]]:
    """Check all test files for deletions, weakening, and disabling.

    Returns:
        (tests_ok, assertions_ok, issues)
    """
    ok_t = ok_a = True
    issues: list[str] = []
    for fname, pre_src in pre.items():
        if "test_" not in fname and not fname.startswith("test"):
            continue
        tests_ok, asserts_ok, _, file_iss = check_test_file_integrity(
            pre_src, post.get(fname, "")
        )
        issues.extend(file_iss)
        ok_t = ok_t and tests_ok
        ok_a = ok_a and asserts_ok
    return ok_t, ok_a, issues
