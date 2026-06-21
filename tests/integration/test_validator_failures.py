"""Failure-mode tests for validate_repo.py.

For each validator check, creates a temporary fixture that violates it
and asserts that the validator exits with code != 0.

Traceability: [TODO P8-R02], [Correction #10]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "validate_repo.py"


def _run_check(check_fn: str, fixture_code: str, tmp_path: Path) -> int:
    """Run one isolated check function against a minimal fixture.

    Writes fixture_code to a temp .py file, patches SRC to tmp_path in the
    check, then asserts exit code.
    """
    script = f"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(r'{REPO_ROOT}') / 'scripts'))

# Override ROOT/SRC to point at tmp_path fixture
import validate_repo as vr
tmp = Path(r'{tmp_path}')
vr.ROOT = tmp
vr.SRC = tmp / 'src'
vr.DOCS = tmp / 'docs'
vr.ARTS = tmp / 'artifacts'

violations = vr.{check_fn}()
if violations:
    print('\\n'.join(violations))
    sys.exit(1)
sys.exit(0)
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True,
    )
    return result.returncode


def _write_py(path: Path, content: str, rel: str = "src/ex04/module.py") -> Path:
    target = path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    return target


def test_file_size_violation(tmp_path: Path) -> None:
    """check_file_size returns non-zero when a file has > 150 lines."""
    big = _write_py(tmp_path, "\n".join([f"x_{i} = {i}" for i in range(160)]))
    assert big.read_text().count("\n") > 150
    rc = _run_check("check_file_size", "", tmp_path)
    assert rc != 0


def test_secret_violation(tmp_path: Path) -> None:
    """check_secrets returns non-zero when API key is hardcoded."""
    _write_py(tmp_path, 'api_key = "sk-abcdefgh12345678"\n')
    rc = _run_check("check_secrets", "", tmp_path)
    assert rc != 0


def test_personal_path_violation(tmp_path: Path) -> None:
    """check_personal_paths returns non-zero when /home/user/... appears."""
    _write_py(tmp_path, 'CONFIG = "/home/dev-pop-os/myconfig/settings.json"\n')
    rc = _run_check("check_personal_paths", "", tmp_path)
    assert rc != 0


def test_sdk_boundary_violation(tmp_path: Path) -> None:
    """check_sdk_boundary returns non-zero when a service imports from sdk."""
    _write_py(tmp_path, "from ex04.sdk import Ex04SDK\n",
              "src/ex04/services/bad_service.py")
    rc = _run_check("check_sdk_boundary", "", tmp_path)
    assert rc != 0


def test_pricing_no_retired_violation(tmp_path: Path) -> None:
    """check_pricing_no_retired returns non-zero when retired model is in active list."""
    cfg = {
        "models": [{"provider": "anthropic", "model": "claude-3-haiku-20240307",
                    "input_price": 0.25, "output_price": 1.25}],
        "retired_models": ["claude-3-haiku-20240307"],
    }
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "pricing.json").write_text(json.dumps(cfg))
    rc = _run_check("check_pricing_no_retired", "", tmp_path)
    assert rc != 0


def test_manifest_keys_violation(tmp_path: Path) -> None:
    """check_manifest_keys returns non-zero when required fields are missing."""
    art_dir = tmp_path / "artifacts" / "manifests"
    art_dir.mkdir(parents=True)
    (art_dir / "bad_manifest.json").write_text(json.dumps({"run_id": "x"}))
    rc = _run_check("check_manifest_keys", "", tmp_path)
    assert rc != 0


def test_provenance_keys_violation(tmp_path: Path) -> None:
    """check_provenance_keys returns non-zero when required keys are missing."""
    art_dir = tmp_path / "artifacts" / "pre_fix"
    art_dir.mkdir(parents=True)
    (art_dir / "provenance.json").write_text(json.dumps({"evidence_class": "fixture"}))
    rc = _run_check("check_provenance_keys", "", tmp_path)
    assert rc != 0


def test_vault_wikilink_violation(tmp_path: Path) -> None:
    """check_vault_wikilinks returns non-zero when wikilink target doesn't exist."""
    vault = tmp_path / "obsidian"
    vault.mkdir()
    (vault / "index.md").write_text("See [[NonExistentNote]] for details.\n")
    rc = _run_check("check_vault_wikilinks", "", tmp_path)
    assert rc != 0


def test_pricing_format_violation(tmp_path: Path) -> None:
    """check_pricing_format returns non-zero when units field is wrong."""
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "pricing.json").write_text(json.dumps({"units": "per_call", "models": []}))
    rc = _run_check("check_pricing_format", "", tmp_path)
    assert rc != 0


def test_source_anchor_format_violation(tmp_path: Path) -> None:
    """check_source_anchors returns non-zero when anchor format is invalid."""
    art_dir = tmp_path / "artifacts" / "manifests"
    art_dir.mkdir(parents=True)
    manifest = {
        "run_id": "x",
        "mode": "naive",
        "evidence_class": "fixture",
        "telemetry_available": False,
        "source_anchors": ["bad-anchor-format"],
    }
    (art_dir / "test_manifest.json").write_text(json.dumps(manifest))
    rc = _run_check("check_source_anchors", "", tmp_path)
    assert rc != 0
