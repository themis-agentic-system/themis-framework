"""Integration tests for orchestrator service persistence."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

import asyncio

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


class RecordingAgent:
    """Agent that records the received matter payload for assertions."""

    def __init__(self, name: str, producer: Callable[[dict[str, Any]], dict[str, Any]]):
        self.name = name
        self._producer = producer
        self.seen_inputs: list[dict[str, Any]] = []

    async def run(self, matter: dict[str, Any]) -> dict[str, Any]:
        self.seen_inputs.append(matter)
        payload = self._producer(matter) or {}
        payload.setdefault("agent", self.name)
        return payload


@pytest.fixture
def dummy_agents() -> dict[str, DummyAgent]:
    return {name: DummyAgent(name) for name in ("lda", "dea", "lsa")}


def test_plan_and_execution_are_persisted(tmp_path, dummy_agents):
    database_url = f"sqlite:///{tmp_path/'orchestrator.db'}"
    repository = SQLiteOrchestratorStateRepository(database_url=database_url)
    service = OrchestratorService(agents=dummy_agents, repository=repository)

    matter = {"case": "example"}
    plan = asyncio.run(service.plan(matter))
    plan_id = plan["plan_id"]

    execution = asyncio.run(service.execute(plan_id=plan_id))
    assert execution["status"] == "complete"
    assert set(execution["artifacts"]) == {"lda", "dea", "lsa"}

    reloaded_service = OrchestratorService(
        agents=dummy_agents,
        repository=SQLiteOrchestratorStateRepository(database_url=database_url),
    )

    stored_plan = asyncio.run(reloaded_service.get_plan(plan_id))
    assert stored_plan["plan_id"] == plan_id
    artifacts = asyncio.run(reloaded_service.get_artifacts(plan_id))
    assert set(artifacts) == set(execution["artifacts"])


def test_execute_passes_expected_artifacts_between_agents(tmp_path):
    database_url = f"sqlite:///{tmp_path/'orchestrator.db'}"

    lda_agent = RecordingAgent(
        "lda",
        lambda _: {
            "facts": {
                "fact_pattern_summary": ["Collision occurred at Mission & 5th"],
                "timeline": [
                    {"date": "2024-03-14", "description": "Collision"},
                ],
            }
        },
    )

    def dea_payload(matter: dict[str, Any]) -> dict[str, Any]:
        facts = matter.get("facts") if isinstance(matter.get("facts"), dict) else {}
        summary = facts.get("fact_pattern_summary", []) if isinstance(facts, dict) else []
        return {
            "legal_analysis": {
                "issues": summary,
                "analysis": "Negligence is supported by eyewitness statements.",
            }
        }

    dea_agent = RecordingAgent("dea", dea_payload)

    def lsa_payload(matter: dict[str, Any]) -> dict[str, Any]:
        analysis = (
            matter.get("legal_analysis")
            if isinstance(matter.get("legal_analysis"), dict)
            else {}
        )
        issues = analysis.get("issues", []) if isinstance(analysis, dict) else []
        return {
            "strategy": {
                "recommended_actions": ["Draft demand letter"],
                "negotiation_positions": {"opening": "$150,000"},
                "contingencies": ["File complaint"],
                "risk_assessment": {"unknowns": [], "issues_included": issues},
            }
        }

    lsa_agent = RecordingAgent("lsa", lsa_payload)

    service = OrchestratorService(
        agents={"lda": lda_agent, "dea": dea_agent, "lsa": lsa_agent},
        repository=SQLiteOrchestratorStateRepository(database_url=database_url),
    )

    matter = {"summary": "Example"}
    execution = asyncio.run(service.execute(matter=matter))

    assert execution["status"] == "complete"

    assert lda_agent.seen_inputs == [matter]

    assert dea_agent.seen_inputs, "DEA agent should have received input"
    dea_input = dea_agent.seen_inputs[0]
    assert "facts" in dea_input
    assert dea_input["facts"]["fact_pattern_summary"] == [
        "Collision occurred at Mission & 5th"
    ]

    assert lsa_agent.seen_inputs, "LSA agent should have received input"
    lsa_input = lsa_agent.seen_inputs[0]
    assert "legal_analysis" in lsa_input
    assert lsa_input["legal_analysis"]["issues"] == [
        "Collision occurred at Mission & 5th"
    ]

    # Artifacts should still be persisted under agent names for compatibility.
    assert set(execution["artifacts"].keys()) == {"lda", "dea", "lsa"}
    assert execution["artifacts"]["dea"]["legal_analysis"]["issues"] == [
        "Collision occurred at Mission & 5th"
    ]


def test_missing_plan_raises_error(tmp_path, dummy_agents):
    database_url = f"sqlite:///{tmp_path/'orchestrator.db'}"
    service = OrchestratorService(
        agents=dummy_agents,
        repository=SQLiteOrchestratorStateRepository(database_url=database_url),
    )

    with pytest.raises(ValueError):
        asyncio.run(service.get_plan("unknown-plan"))

    with pytest.raises(ValueError):
        asyncio.run(service.get_artifacts("unknown-plan"))
