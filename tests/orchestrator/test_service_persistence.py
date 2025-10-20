"""Integration tests for orchestrator service persistence."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.append(str(Path(__file__).resolve().parents[2]))

from orchestrator.service import OrchestratorService
from orchestrator.storage.sqlite_repository import SQLiteOrchestratorStateRepository


class DummyAgent:
    """Minimal agent implementation for testing."""

    def __init__(self, name: str) -> None:
        self.name = name

    async def run(self, matter: dict[str, Any]) -> dict[str, Any]:
        return {"agent": self.name, "matter": matter}


@pytest.fixture
def dummy_agents() -> dict[str, DummyAgent]:
    return {name: DummyAgent(name) for name in ("lda", "dea", "lsa")}


@pytest.mark.asyncio
async def test_plan_and_execution_are_persisted(tmp_path, dummy_agents):
    database_url = f"sqlite:///{tmp_path/'orchestrator.db'}"
    repository = SQLiteOrchestratorStateRepository(database_url=database_url)
    service = OrchestratorService(agents=dummy_agents, repository=repository)

    matter = {"case": "example"}
    plan = await service.plan(matter)
    plan_id = plan["plan_id"]

    execution = await service.execute(plan_id=plan_id)
    assert execution["status"] == "complete"
    assert set(execution["artifacts"]) == {"lda", "dea", "lsa"}

    reloaded_service = OrchestratorService(
        agents=dummy_agents,
        repository=SQLiteOrchestratorStateRepository(database_url=database_url),
    )

    stored_plan = await reloaded_service.get_plan(plan_id)
    assert stored_plan["plan_id"] == plan_id
    artifacts = await reloaded_service.get_artifacts(plan_id)
    assert set(artifacts) == set(execution["artifacts"])


@pytest.mark.asyncio
async def test_missing_plan_raises_error(tmp_path, dummy_agents):
    database_url = f"sqlite:///{tmp_path/'orchestrator.db'}"
    service = OrchestratorService(
        agents=dummy_agents,
        repository=SQLiteOrchestratorStateRepository(database_url=database_url),
    )

    with pytest.raises(ValueError):
        await service.get_plan("unknown-plan")

    with pytest.raises(ValueError):
        await service.get_artifacts("unknown-plan")
