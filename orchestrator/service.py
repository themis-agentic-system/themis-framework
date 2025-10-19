"""Application service coordinating registered legal agents."""

from __future__ import annotations

from typing import Any

from orchestrator.state import OrchestratorState


class OrchestratorService:
    """Skeleton service that wires agent planning and execution."""

    def __init__(self) -> None:
        self.state = OrchestratorState()

    async def plan(self, matter: dict[str, Any]) -> dict[str, Any]:
        """Create a placeholder plan until the planner is implemented."""
        return {
            "status": "planned",
            "inputs": matter,
            "steps": [
                {"agent": "lda", "task": "Extract facts and figures."},
                {"agent": "dea", "task": "Apply doctrinal analysis."},
                {"agent": "lsa", "task": "Craft negotiation strategy."},
            ],
        }

    async def execute(self, matter: dict[str, Any]) -> dict[str, Any]:
        """Execute the placeholder plan returning mocked artifacts."""
        plan = await self.plan(matter)
        return {
            "status": "complete",
            "plan": plan,
            "artifacts": {
                "timeline": "TODO: generate timeline exhibit",
                "demand_letter": "TODO: generate demand letter",
            },
        }
