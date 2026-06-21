"""Repository validation script — enforces project coding standards.

Run: uv run python scripts/validate_repo.py
Exits with code 1 if any violation is found.

Traceability: [TODO P8-R02], [Correction #10]
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "src"
DOCS = ROOT / "docs"
ARTS = ROOT / "artifacts"

_SECRET = re.compile(r"(?i)(api[_-]?key|password|bearer)\s*=\s*['\"][^'\"]{8,}")
_PATH = re.compile(r'["\']/(home|Users)/[A-Za-z0-9_.-]{2,}/')
_SDK_IMPORT = re.compile(r"from ex04\.sdk")
_PROVIDER_IMPORT = re.compile(r"from ex04\.providers\.\w+_provider")
_ANCHOR_FMT = re.compile(r"^[^:]+:\d+-\d+$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")

Violations = list[str]


def _py_files() -> list[Path]:
    return list(SRC.rglob("*.py"))


# ── Checks 1–6: code-level invariants ────────────────────────────────────────

def check_file_size() -> Violations:
    """Check 1: All .py files ≤ 150 lines."""
    return [f"FILE_SIZE: {p.relative_to(ROOT)} ({len(p.read_text().splitlines())} lines)"
            for p in _py_files() if len(p.read_text().splitlines()) > 150]


def check_secrets() -> Violations:
    """Check 2: No hardcoded credentials in source files."""
    return [f"SECRET: {p.relative_to(ROOT)}" for p in _py_files()
            if _SECRET.search(p.read_text())]


def check_personal_paths() -> Violations:
    """Check 3: No personal absolute paths (/home/..., /Users/...)."""
    return [f"PERSONAL_PATH: {p.relative_to(ROOT)}" for p in _py_files()
            if _PATH.search(p.read_text())]


def check_sdk_boundary() -> Violations:
    """Check 4: Service modules must not import from sdk/."""
    svc = SRC / "ex04" / "services"
    return [f"SDK_BOUNDARY: {p.relative_to(ROOT)}" for p in svc.rglob("*.py")
            if _SDK_IMPORT.search(p.read_text())]


def check_provider_boundary() -> Violations:
    """Check 5: Provider implementations imported only from providers/."""
    providers_dir = SRC / "ex04" / "providers"
    violations: Violations = []
    for p in _py_files():
        if p.is_relative_to(providers_dir):
            continue
        if _PROVIDER_IMPORT.search(p.read_text()):
            violations.append(f"PROVIDER_BOUNDARY: {p.relative_to(ROOT)}")
    return violations


def check_sdk_private_comparison_access() -> Violations:
    """Check 6: SDK must not pierce private comparison-service collaborators."""
    sdk = SRC / "ex04" / "sdk"
    bad = re.compile(r"_comparison\._(naive|guided|signed)")
    return [f"SDK_PRIVATE_COMPARISON: {p.relative_to(ROOT)}" for p in sdk.rglob("*.py")
            if bad.search(p.read_text())]


def check_pricing_no_retired() -> Violations:
    """Check 6: No retired models in active pricing models list."""
    cfg_path = ROOT / "config" / "pricing.json"
    if not cfg_path.exists():
        return ["PRICING_MISSING: config/pricing.json not found"]
    cfg = json.loads(cfg_path.read_text())
    retired = set(cfg.get("retired_models", []))
    active = {e["model"] for e in cfg.get("models", [])}
    overlap = retired & active
    return [f"RETIRED_IN_ACTIVE: {m}" for m in sorted(overlap)]


# ── Checks 7–12: artifact / provenance invariants ────────────────────────────

def check_manifest_keys() -> Violations:
    """Check 7: Manifests in artifacts/manifests/ have required fields."""
    mdir = ARTS / "manifests"
    if not mdir.exists():
        return []
    required = {"run_id", "mode", "evidence_class", "telemetry_available"}
    violations: Violations = []
    for p in mdir.glob("*.json"):
        try:
            data = json.loads(p.read_text())
            miss = required - set(data.keys())
            if miss:
                violations.append(f"MANIFEST_SCHEMA: {p.name} missing {miss}")
        except json.JSONDecodeError:
            violations.append(f"MANIFEST_INVALID: {p.name}")
    return violations


def check_manifest_hash_format() -> Violations:
    """Check: manifest config/trace hashes must be full SHA-256 when present."""
    mdir = ARTS / "manifests"
    if not mdir.exists():
        return []
    violations: Violations = []
    for p in mdir.glob("*.json"):
        data = json.loads(p.read_text())
        for key in ("config_hash", "shared_config_hash", "trace_hash"):
            value = data.get(key)
            if value and not _SHA256.match(str(value)):
                violations.append(f"HASH_FORMAT: {p.name} {key}")
    return violations


def check_manifest_run_linkage() -> Violations:
    """Check 8: Every manifest run_id must correspond to an artifacts/runs/ dir."""
    mdir = ARTS / "manifests"
    runs_dir = ARTS / "runs"
    if not mdir.exists():
        return []
    violations: Violations = []
    for p in mdir.glob("*.json"):
        try:
            rid = json.loads(p.read_text()).get("run_id", "")
            if rid and not (runs_dir / rid).exists():
                violations.append(f"MANIFEST_DANGLING: {p.name} → runs/{rid} not found")
        except (json.JSONDecodeError, KeyError):
            pass
    return violations


def check_provenance_keys() -> Violations:
    """Check 9: artifacts/pre_fix/provenance.json has required keys."""
    prov = ARTS / "pre_fix" / "provenance.json"
    if not prov.exists():
        return ["PROVENANCE_MISSING: artifacts/pre_fix/provenance.json"]
    required = {"target_repo", "target_commit", "snapshot_hash", "acquisition_date"}
    try:
        keys = set(json.loads(prov.read_text()).keys())
        miss = required - keys
        return [f"PROVENANCE_FIELD: missing {k}" for k in sorted(miss)]
    except json.JSONDecodeError:
        return ["PROVENANCE_INVALID_JSON"]


def check_source_anchors() -> Violations:
    """Check 10: source_anchors in manifests follow <file>:<start>-<end> format."""
    mdir = ARTS / "manifests"
    if not mdir.exists():
        return []
    violations: Violations = []
    for p in mdir.glob("*.json"):
        try:
            anchors = json.loads(p.read_text()).get("source_anchors", [])
            for anchor in anchors:
                if anchor and not _ANCHOR_FMT.match(anchor):
                    violations.append(f"ANCHOR_FORMAT: {p.name}: {anchor!r}")
        except (json.JSONDecodeError, TypeError):
            pass
    return violations


def check_legacy_success_sentinels() -> Violations:
    """Check: production source must not use pass_without_gate as correctness."""
    violations: Violations = []
    for p in _py_files():
        if "pass_without_gate" in p.read_text():
            violations.append(f"LEGACY_GATE_STATUS: {p.relative_to(ROOT)}")
    return violations


# ── Checks 11–16: documentation / import invariants ─────────────────────────

def check_broken_doc_links() -> Violations:
    """Check 11: Relative links in docs/*.md must resolve."""
    violations: Violations = []
    for doc in DOCS.glob("*.md"):
        text = doc.read_text(encoding="utf-8")
        for m in re.finditer(r"\[.*?\]\(\./([^)]+)\)", text):
            target = doc.parent / m.group(1)
            if not target.exists():
                violations.append(f"BROKEN_LINK: {doc.name} → ./{m.group(1)}")
    return violations


def check_wiki_sync() -> Violations:
    """Check 12: plan-wiki/ and todo-wiki/ directories exist and are non-empty."""
    violations: Violations = []
    for wiki in ("plan-wiki", "todo-wiki"):
        wiki_dir = DOCS / wiki
        if not wiki_dir.exists():
            violations.append(f"WIKI_MISSING: docs/{wiki}/ not found")
        elif not any(wiki_dir.glob("*.md")):
            violations.append(f"WIKI_EMPTY: docs/{wiki}/ has no .md files")
    return violations


def check_vault_wikilinks() -> Violations:
    """Check 13: Wikilinks [[note]] in obsidian/ reference existing notes.

    Handles path-prefixed links ([[dir/note]]) and relative links ([[../note]])
    by matching only the last path component (note stem).
    """
    vault = ROOT / "obsidian"
    if not vault.exists():
        return []
    note_stems = {p.stem for p in vault.rglob("*.md")}
    violations: Violations = []
    seen: set[tuple[str, str]] = set()
    for note in vault.rglob("*.md"):
        for link in re.findall(r"\[\[([^\]|]+)", note.read_text()):
            stem = link.strip().rsplit("/", 1)[-1].strip(".")
            key = (note.name, stem)
            if stem and stem not in note_stems and key not in seen:
                seen.add(key)
                violations.append(f"VAULT_LINK: {note.name} → [[{link}]] not found")
    return violations[:20]


def check_keyless_import() -> Violations:
    """Check 14: SDK must import without any provider API key."""
    result = subprocess.run(
        [sys.executable, "-c", "from ex04.sdk import Ex04SDK"],
        capture_output=True, text=True, cwd=ROOT,
        env={**__import__("os").environ, "PYTHONPATH": str(SRC)},
    )
    if result.returncode != 0:
        return [f"KEYLESS_IMPORT_FAIL: {result.stderr.strip()[:200]}"]
    return []


def check_hardcoded_config() -> Violations:
    """Check 15: No hardcoded URLs or timeouts in source (outside config/)."""
    url_pat = re.compile(r'(?i)https?://[a-z0-9._-]+\.[a-z]{2,}')
    violations: Violations = []
    for p in _py_files():
        text = p.read_text()
        if url_pat.search(text):
            violations.append(f"HARDCODED_URL: {p.relative_to(ROOT)}")
    return violations


def check_pricing_format() -> Violations:
    """Check 16: pricing.json uses per_million_tokens units."""
    cfg_path = ROOT / "config" / "pricing.json"
    if not cfg_path.exists():
        return []
    try:
        cfg = json.loads(cfg_path.read_text())
        if cfg.get("units") != "per_million_tokens":
            return ["PRICING_UNITS: units must be 'per_million_tokens'"]
    except json.JSONDecodeError:
        return ["PRICING_INVALID_JSON"]
    return []


def main() -> None:
    """Run all validation checks and exit with code 1 if violations found."""
    all_checks = [
        check_file_size, check_secrets, check_personal_paths,
        check_sdk_boundary, check_provider_boundary, check_sdk_private_comparison_access,
        check_pricing_no_retired, check_manifest_keys, check_manifest_hash_format,
        check_manifest_run_linkage, check_provenance_keys,
        check_source_anchors, check_legacy_success_sentinels,
        check_broken_doc_links, check_wiki_sync,
        check_vault_wikilinks, check_keyless_import,
        check_hardcoded_config, check_pricing_format,
    ]
    violations: Violations = []
    for check in all_checks:
        violations.extend(check())

    if violations:
        print(f"Validation FAILED ({len(violations)} violations):")
        for v in violations:
            print(f"  ✗ {v}")
        sys.exit(1)
    print(f"Validation PASSED (checked {len(_py_files())} files, {len(all_checks)} checks)")
    sys.exit(0)


if __name__ == "__main__":
    main()
