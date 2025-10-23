"""Application service coordinating registered legal agents."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import uuid4

from agents.base import AgentProtocol
from agents.dea import DEAAgent
from agents.lsa import LSAAgent
from agents.lda import LDAAgent
from orchestrator.storage.sqlite_repository import SQLiteOrchestratorStateRepository


class OrchestratorService:
    """Service responsible for planning and executing agent workflows."""

    def __init__(
        self,
        agents: dict[str, AgentProtocol] | None = None,
        repository: SQLiteOrchestratorStateRepository | None = None,
    ) -> None:
        self.repository = repository or SQLiteOrchestratorStateRepository()
        self.state = self.repository.load_state()
        self.agents = agents or {
            "lda": LDAAgent(),
            "dea": DEAAgent(),
            "lsa": LSAAgent(),
        }
        self._default_plan = (
            (
                "lda",
                "Extract facts and figures from the supplied matter payload.",
                [
                    {
                        "name": "facts",
                        "description": "Structured fact pattern including timeline, parties, and key details.",
                    }
                ],
            ),
            (
                "dea",
                "Apply doctrinal analysis over the fact pattern to surface legal issues.",
                [
                    {
                        "name": "legal_analysis",
                        "description": "Structured doctrinal analysis tying issues to supporting authorities.",
                    }
                ],
            ),
            (
                "lsa",
                "Craft negotiation and settlement strategy leveraging prior analysis.",
                [
                    {
                        "name": "strategy",
                        "description": "Recommended course of action with positions, contingencies, and risks.",
                    }
                ],
            ),
        )

    async def plan(self, matter: dict[str, Any]) -> dict[str, Any]:
        """Create an executable plan across the registered agents."""

        self.state = self.repository.load_state()
        plan_id = str(uuid4())
        steps: list[dict[str, Any]] = []
        previous_step_id: str | None = None

        for index, (agent_name, description, expected_artifacts) in enumerate(self._default_plan, start=1):
            step_id = f"step-{index}"
            dependencies = [previous_step_id] if previous_step_id else []
            steps.append(
                {
                    "id": step_id,
                    "agent": agent_name,
                    "description": description,
                    "status": "pending",
                    "inputs": {
                        "matter": matter,
                        "dependencies": dependencies,
                    },
                    "dependencies": dependencies,
                    "expected_artifacts": expected_artifacts,
                }
            )
            previous_step_id = step_id

        plan: dict[str, Any] = {
            "plan_id": plan_id,
            "status": "planned",
            "matter": matter,
            "steps": steps,
        }

        self.state.remember_plan(plan_id, deepcopy(plan))
        self.repository.save_state(self.state)
        return plan

    async def execute(
        self,
        matter: dict[str, Any] | None = None,
        plan_id: str | None = None,
    ) -> dict[str, Any]:
        """Execute a plan by invoking each registered agent in order."""

        self.state = self.repository.load_state()
        if plan_id is not None:
            plan = self.state.recall_plan(plan_id)
            if plan is None:
                raise ValueError(f"Plan '{plan_id}' does not exist")
            if matter is not None:
                plan["matter"] = matter
                self.state.remember_plan(plan_id, deepcopy(plan))
                self.repository.save_state(self.state)
        else:
            if matter is None:
                raise ValueError("Matter payload is required when no plan_id is provided")
            plan = await self.plan(matter)
            plan_id = plan["plan_id"]

        plan_matter = deepcopy(plan.get("matter", {}))
        steps_results: list[dict[str, Any]] = []
        artifacts: dict[str, Any] = {}
        propagated: dict[str, Any] = {}
        overall_status = "complete"

        for step in plan["steps"]:
            agent_name = step["agent"]
            agent = self.agents.get(agent_name)
            step_result: dict[str, Any] = {
                "id": step["id"],
                "agent": agent_name,
                "dependencies": step.get("dependencies", []),
                "expected_artifacts": step.get("expected_artifacts", []),
            }

            if agent is None:
                step_result["status"] = "failed"
                step_result["error"] = f"Agent '{agent_name}' is not registered"
                overall_status = "failed"
                step["status"] = "failed"
                step["error"] = step_result["error"]
                steps_results.append(step_result)
                continue

            produced_artifacts: dict[str, Any] = {}

            try:
                agent_input = deepcopy(plan_matter)
                agent_input.update(propagated)
                output = await agent.run(agent_input)
            except Exception as exc:  # pragma: no cover - defensive programming
                step_result["status"] = "failed"
                step_result["error"] = str(exc)
                overall_status = "failed"
                step["status"] = "failed"
                step["error"] = step_result["error"]
            else:
                step_result["status"] = "complete"
                step_result["output"] = output
                artifacts[agent_name] = output
                propagated[agent_name] = output
                produced_artifacts = _collect_expected_artifacts(
                    output, step.get("expected_artifacts", [])
                )
                if produced_artifacts:
                    propagated.update(produced_artifacts)
                    plan_matter.update(produced_artifacts)
                    step_result["artifacts"] = produced_artifacts
                    step["artifacts"] = produced_artifacts
                step["status"] = "complete"
                step["output"] = output

            steps_results.append(step_result)

        execution_record = {
            "plan_id": plan_id,
            "status": overall_status,
            "steps": steps_results,
            "artifacts": artifacts,
        }

        plan["status"] = overall_status
        self.state.remember_plan(plan_id, deepcopy(plan))
        self.state.remember_execution(plan_id, deepcopy(execution_record))
        self.repository.save_state(self.state)

        return execution_record

    async def get_plan(self, plan_id: str) -> dict[str, Any]:
        """Retrieve a persisted plan by identifier."""

        self.state = self.repository.load_state()
        plan = self.state.recall_plan(plan_id)
        if plan is None:
            raise ValueError(f"Plan '{plan_id}' does not exist")
        return deepcopy(plan)

    async def get_artifacts(self, plan_id: str) -> dict[str, Any]:
        """Retrieve execution artifacts for a given plan identifier."""

        self.state = self.repository.load_state()
        execution = self.state.recall_execution(plan_id)
        if execution is None:
            raise ValueError(f"Execution for plan '{plan_id}' does not exist")
        return deepcopy(execution.get("artifacts", {}))


def _collect_expected_artifacts(
    payload: dict[str, Any], expected_artifacts: list[dict[str, Any]]
) -> dict[str, Any]:
    """Extract advertised artifacts from an agent payload."""

    collected: dict[str, Any] = {}
    for artifact in expected_artifacts or []:
        if not isinstance(artifact, dict):
            continue
        name = artifact.get("name")
        if not name:
            continue
        value = payload.get(name)
        if value is None:
            value = _find_nested_artifact(payload, name)
        if value is not None:
            collected[name] = value
    return collected


def _find_nested_artifact(payload: dict[str, Any], artifact_name: str) -> Any:
    """Locate a nested artifact within the payload."""

    for value in payload.values():
        if isinstance(value, dict):
            if artifact_name in value:
                return value[artifact_name]
            nested = _find_nested_artifact(value, artifact_name)
            if nested is not None:
                return nested
    return None
