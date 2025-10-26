from copy import deepcopy
from typing import Any

from agents.dea import DEAAgent
from agents.lda import LDAAgent
from agents.lsa import LSAAgent


class Orchestrator:
    """Simple orchestrator that runs LDA -> DEA -> LSA in sequence."""

    def __init__(self, agents: dict[str, Any] | None = None) -> None:
        self.agents = agents or {
            "lda": LDAAgent(),
            "dea": DEAAgent(),
            "lsa": LSAAgent(),
        }
        self._default_plan = [
            (
                "lda",
                "Extract facts and figures",
                [{"name": "facts", "description": "Structured facts"}],
            ),
            (
                "dea",
                "Apply doctrinal analysis",
                [{"name": "legal_analysis", "description": "Legal analysis output"}],
            ),
            (
                "lsa",
                "Craft strategy",
                [{"name": "strategy", "description": "Strategy output"}],
            ),
        ]

    async def run_matter(self, matter: dict[str, Any]) -> dict[str, Any]:
        artifacts: dict[str, Any] = {}
        propagated: dict[str, Any] = {}

        for agent_name, _, expected_artifacts in self._default_plan:
            agent = self.agents.get(agent_name)
            if agent is None:
                raise ValueError(f"Agent '{agent_name}' is not registered.")

            input_matter = deepcopy(matter)
            input_matter.update(propagated)

            result = await agent.run(input_matter)
            artifacts[agent_name] = result

            # Maintain backwards compatibility by providing raw outputs under
            # the agent name while also surfacing the advertised artifact keys
            # for downstream agents.
            propagated[agent_name] = result
            for artifact in expected_artifacts or []:
                name = artifact.get("name") if isinstance(artifact, dict) else None
                if not name:
                    continue
                value = result.get(name)
                if value is None:
                    value = _find_nested_artifact(result, name)
                if value is not None:
                    propagated[name] = value

        return {"artifacts": artifacts}


def _find_nested_artifact(payload: dict[str, Any], artifact_name: str) -> Any:
    """Locate an artifact nested within dictionaries of the payload."""

    for value in payload.values():
        if isinstance(value, dict):
            if artifact_name in value:
                return value[artifact_name]
            nested = _find_nested_artifact(value, artifact_name)
            if nested is not None:
                return nested
    return None
