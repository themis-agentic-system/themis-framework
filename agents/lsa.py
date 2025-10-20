"""Implementation of the Legal Strategy Agent (LSA)."""

from __future__ import annotations

from typing import Any, Callable

from agents.base import BaseAgent


class LSAAgent(BaseAgent):
    """Craft negotiation or litigation strategy based on prior analysis."""

    REQUIRED_TOOLS = ("strategy_template", "risk_assessor")

    def __init__(self, *, tools: dict[str, Callable[..., Any]] | None = None) -> None:
        super().__init__(name="lsa")
        default_tools: dict[str, Callable[..., Any]] = {
            "strategy_template": _default_strategy_template,
            "risk_assessor": _default_risk_assessor,
        }
        self.tools = default_tools | (tools or {})
        missing = [tool for tool in self.REQUIRED_TOOLS if tool not in self.tools]
        if missing:
            missing_csv = ", ".join(missing)
            raise ValueError(f"Missing required tools for LSA agent: {missing_csv}")

    async def _run(self, matter: dict[str, Any]) -> dict[str, Any]:
        """Combine facts and legal theories into a strategy recommendation."""

        strategy = self._call_tool("strategy_template", matter)
        risks = self._call_tool("risk_assessor", matter, strategy)

        unresolved: list[str] = []
        if not strategy.get("objectives"):
            unresolved.append("Strategy template could not determine client objectives.")
        if risks.get("unknowns"):
            unresolved.extend(risks["unknowns"])

        plan = {
            "recommended_actions": strategy.get("actions", []),
            "negotiation_positions": strategy.get("positions", {}),
            "contingencies": strategy.get("contingencies", []),
            "risk_assessment": risks,
        }

        provenance = {
            "tools_used": list(self.tools.keys()),
            "assumptions": strategy.get("assumptions", []),
        }

        return self._build_response(
            core={"strategy": plan},
            provenance=provenance,
            unresolved_issues=unresolved,
        )


def _default_strategy_template(matter: dict[str, Any]) -> dict[str, Any]:
    """Draft a negotiation outline from goals and analysis inputs."""

    goals = matter.get("goals", {})
    preferred_outcome = goals.get("settlement") or goals.get("remedy")
    leverage_points = matter.get("strengths", [])
    concessions = matter.get("concessions", [])

    return {
        "objectives": preferred_outcome,
        "actions": [
            "Confirm factual timeline with client",
            "Validate legal theories with doctrinal team",
            "Prepare negotiation brief highlighting leverage",
        ],
        "positions": {
            "opening": preferred_outcome or "Clarify desired settlement range",
            "fallback": goals.get("fallback"),
        },
        "contingencies": [
            "Escalate to litigation counsel if negotiations stall",
            "Reassess damages model upon receipt of new evidence",
        ],
        "leverage_points": leverage_points,
        "proposed_concessions": concessions,
        "assumptions": [
            "Opposing party is open to early resolution",
            "Client authorised exploring structured settlement options",
        ],
    }


def _default_risk_assessor(matter: dict[str, Any], strategy: dict[str, Any]) -> dict[str, Any]:
    """Produce a lightweight qualitative risk profile."""

    weaknesses = matter.get("weaknesses", [])
    evidentiary_gaps = matter.get("evidentiary_gaps", [])
    confidence = max(0, min(100, int(matter.get("confidence_score", 60))))

    unknowns = []
    if not matter.get("counterparty"):
        unknowns.append("Counterparty identity or counsel not specified.")
    if not evidentiary_gaps and "Verify damages model" not in strategy.get("actions", []):
        unknowns.append("Damages analysis tasks not explicitly scheduled.")

    return {
        "confidence": confidence,
        "weaknesses": weaknesses,
        "evidentiary_gaps": evidentiary_gaps,
        "unknowns": unknowns,
    }
