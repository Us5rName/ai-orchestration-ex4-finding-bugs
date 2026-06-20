"""Tests for VaultService facade."""

from pathlib import Path

from ex04.services.vault.service import VaultService
from ex04.shared.types import Entity, GraphData


def test_vault_service_build_navigate_update(tmp_path: Path) -> None:
    service = VaultService(tmp_path)
    graph = GraphData(entities=[Entity("OrderService", "class", "order.py")])

    notes = service.build(graph)
    updated = service.update("hot", "OrderService failure")
    matches = service.navigate("OrderService")

    assert notes["index"].exists()
    assert updated == tmp_path / "hot.md"
    assert matches
