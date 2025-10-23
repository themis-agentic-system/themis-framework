import asyncio
from typing import Any, Dict
from copy import deepcopy

from agents.lda import LDAAgentimport asyncio
from typing import Any, Dict
from copy import deepcopy

from agents.lda import LDAAgent
import asyncio
from typing import Any, Dict
from copy import deepcopy
from agents.lda import LDAAgent
from agents.dea import DEAAgent
from agents.lsa import LSAAgent

class Orchestrator:
    """Simple orchestrator that runs LDA → DEA → LSA in sequence."""
    def __init__(self, agents: Dict[str, Any] | None = None) -> None:
        self.agents = agents or {
            "lda": LDAAgent(),
            "dea": DEAAgent(),
            "lsa": LSAAgent(),
        }
        self._default_plan = [
            ("lda", "Extract facts and figures", [{"name": "facts", "description": "Structured facts"}]),
            ("dea", "Apply doctrinal analysis", [{"name": "legal_analysis", "description": "Legal analysis output"}]),
            ("lsa", "Craft strategy", [{"name": "strategy", "description": "Strategy output"}]),
        ]

    async def run_matter(self, matter: Dict[str, Any]) -> Dict[str, Any]:
        artifacts: Dict[str, Any] = {}
        for agent_name, _, _ in self._default_plan:
            agent = self.agents.get(agent_name)
            if agent is None:
                raise ValueError(f"Agent '{agent_name}' is not registered.")
            input_matter = deepcopy(matter)
            # inject prior outputs into the next agent's matter context
            for art_name, art_value in artifacts.items():
                input_matter[art_name] = art_value
            result = await agent.run(input_matter)
            artifacts[agent_name] = result
        return {"artifacts": artifacts}
from agents.dea import DEAAgent
from agents.lsa import LSAAgent

class Orchestrator:
    """Simple orchestrator that runs LDA → DEA → LSA in sequence."""
    def __init__(self, agents: Dict[str, Any] | None = None) -> None:
        self.agents = agents or {
            "lda": LDAAgent(),
            "dea": DEAAgent(),
            "lsa": LSAAgent(),
        }
        self._default_plan = [
            ("lda", "Extract facts and figures", [{"name": "facts", "description": "Structured facts"}]),
            ("dea", "Apply doctrinal analysis", [{"name": "legal_analysis", "description": "Legal analysis output"}]),
            ("lsa", "Craft strategy", [{"name": "strategy", "description": "Strategy output"}]),
        ]

    async def run_matter(self, matter: Dict[str, Any]) -> Dict[str, Any]:
        artifacts: Dict[str, Any] = {}
        for agent_name, _, _ in self._default_plan:
            agent = self.agents.get(agent_name)
            if agent is None:
                raise ValueError(f"Agent '{agent_name}' is not registered.")
            input_matter = deepcopy(matter)
            # inject prior outputs into the next agent's matter context
            for art_name, art_value in artifacts.items():
                input_matter[art_name] = art_value
            result = await agent.run(input_matter)
            artifacts[agent_name] = result
        return {"artifacts": artifacts}
