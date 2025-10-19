"""Application service coordinating registered legal agents."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import uuid4

from agents.base import AgentProtocol
from agents.dea import DEAAgent
from agents.lda import LDAAgent
from agents.lsa import LSAAgent
from orchestrator.state import OrchestratorState


class OrchestratorService:
    """Service responsible for planning and executing agent workflows."""

    def __init__(self, agents: dict[str, AgentProtocol] | None = None) -> None:
        self.state = OrchestratorState()
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
                        "name": "fact_pattern_summary",
                        "description": "Structured summary of key facts and timeline details.",
                    }
                ],
            ),
            (
                "dea",
                "Apply doctrinal analysis over the fact pattern to surface legal issues.",
                [
                    {
                        "name": "legal_theories",
                        "description": "List of legal theories and supporting authorities.",
                    }
                ],
            ),
            (
                "lsa",
                "Craft negotiation and settlement strategy leveraging prior analysis.",
                [
                    {
                        "name": "negotiation_strategy",
                        "description": "Proposed negotiation framing, demands, and concessions.",
                    }
                ],
            ),
        )

    async def plan(self, matter: dict[str, Any]) -> dict[str, Any]:
        """Create an executable plan across the registered agents."""
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
        return plan

    async def execute(
        self,
        matter: dict[str, Any] | None = None,
        plan_id: str | None = None,
    ) -> dict[str, Any]:
        """Execute a plan by invoking each registered agent in order."""

        if plan_id is not None:
            plan = self.state.recall_plan(plan_id)
            if plan is None:
                raise ValueError(f"Plan '{plan_id}' does not exist")
            if matter is not None:
                plan["matter"] = matter
                self.state.remember_plan(plan_id, deepcopy(plan))
        else:
            if matter is None:
                raise ValueError("Matter payload is required when no plan_id is provided")
            plan = await self.plan(matter)
            plan_id = plan["plan_id"]

        plan_matter = plan.get("matter", {})
        steps_results: list[dict[str, Any]] = []
        artifacts: dict[str, Any] = {}
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

            try:
                output = await agent.run(plan_matter)
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

        return execution_record
