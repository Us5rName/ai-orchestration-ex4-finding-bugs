"""Tests for ArtifactStore — immutable evidence lifecycle.

Traceability: [PRD-AP §Invariants], [TODO T7.09]
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04.shared.artifact_store import ArtifactOverwriteError, ArtifactStore, sanitize_artifact
from ex04.shared.types_experiment import RunManifest


def _make_manifest(run_id: str = "test-001") -> RunManifest:
    return RunManifest(
        run_id=run_id,
        mode="naive",
        provider="openai",
        model="gpt-4o",
        target_identifier="test-target",
    )


def test_save_manifest_creates_file(tmp_path: Path) -> None:
    """Saving a manifest creates a JSON file in manifests dir."""
    store = ArtifactStore(tmp_path / "artifacts")
    manifest = _make_manifest("run-001")
    path = store.save_manifest(manifest)
    assert path.exists()
    assert path.suffix == ".json"


def test_save_manifest_creates_run_dir(tmp_path: Path) -> None:
    """Saving a manifest creates the run directory."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.save_manifest(_make_manifest("run-002"))
    run_dir = tmp_path / "artifacts" / "runs" / "run-002"
    assert run_dir.is_dir()


def test_overwrite_protection(tmp_path: Path) -> None:
    """Saving the same run_id twice raises ArtifactOverwriteError."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.save_manifest(_make_manifest("run-003"))
    with pytest.raises(ArtifactOverwriteError):
        store.save_manifest(_make_manifest("run-003"))


def test_load_manifest(tmp_path: Path) -> None:
    """Loading a saved manifest returns a dict with expected fields."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.save_manifest(_make_manifest("run-004"))
    loaded = store.load_manifest("run-004")
    assert loaded["run_id"] == "run-004"
    assert loaded["mode"] == "naive"


def test_load_manifest_missing_raises(tmp_path: Path) -> None:
    """Loading a non-existent run_id raises FileNotFoundError."""
    store = ArtifactStore(tmp_path / "artifacts")
    with pytest.raises(FileNotFoundError):
        store.load_manifest("nonexistent")


def test_list_runs_empty(tmp_path: Path) -> None:
    """list_runs returns empty list when no runs exist."""
    store = ArtifactStore(tmp_path / "artifacts")
    assert store.list_runs() == []


def test_list_runs_after_saves(tmp_path: Path) -> None:
    """list_runs returns all saved run IDs sorted."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.save_manifest(_make_manifest("run-b"))
    store.save_manifest(_make_manifest("run-a"))
    assert store.list_runs() == ["run-a", "run-b"]


def test_sanitize_removes_api_key() -> None:
    """sanitize_artifact redacts api_key fields."""
    data = {"api_key": "sk-secret123", "model": "gpt-4"}
    result = sanitize_artifact(data)
    assert result["api_key"] == "<redacted>"
    assert result["model"] == "gpt-4"


def test_sanitize_removes_home_path_value() -> None:
    """sanitize_artifact redacts values containing /home/... paths."""
    data = {"path": "/home/devuser/project", "name": "test"}
    result = sanitize_artifact(data)
    assert result["path"] == "<redacted>"
    assert result["name"] == "test"


def test_sanitize_removes_token_key() -> None:
    """sanitize_artifact redacts credential token key names."""
    data = {"auth_token": "bearer-xyz", "count": 42}
    result = sanitize_artifact(data)
    assert result["auth_token"] == "<redacted>"
    assert result["count"] == 42


def test_sanitize_preserves_token_telemetry() -> None:
    """Token usage counts are evidence, not credentials."""
    data = {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}
    assert sanitize_artifact(data) == data


def test_sanitize_nested_dict() -> None:
    """sanitize_artifact processes nested dicts recursively."""
    data = {"config": {"api_key": "secret", "model": "gpt-4o"}}
    result = sanitize_artifact(data)
    assert result["config"]["api_key"] == "<redacted>"
    assert result["config"]["model"] == "gpt-4o"


def test_config_hash_deterministic() -> None:
    """config_hash returns identical result for identical configs."""
    cfg = {"provider": "openai", "model": "gpt-4o", "max_tokens": 1000}
    h1 = ArtifactStore.config_hash(cfg)
    h2 = ArtifactStore.config_hash(cfg)
    assert h1 == h2
    assert len(h1) == 64
