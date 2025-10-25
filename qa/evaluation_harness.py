"""Replay harness for evaluating agent transcripts against expectations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from orchestrator.task_graph import TaskGraph


class TranscriptLoader(Protocol):
    async def load(self, case_id: str) -> dict[str, Any]: ...


@dataclass
class EvaluationScenario:
    """Represents a recorded matter execution for regression testing."""

    case_id: str
    expected_signals: dict[str, Any]
    tolerances: dict[str, float] | None = None


class TranscriptEvaluator:
    """Utility that replays saved transcripts through the orchestrator."""

    def __init__(self, loader: TranscriptLoader) -> None:
        self._loader = loader

    async def evaluate(
        self,
        scenario: EvaluationScenario,
        *,
        policy,
    ) -> dict[str, Any]:
        payload = await self._loader.load(scenario.case_id)
        matter = payload.get("matter", {})
        graph = policy.build_graph(matter)
        missing = self._detect_missing_signals(graph, scenario.expected_signals)
        return {
            "case_id": scenario.case_id,
            "missing_signals": missing,
            "graph": graph.as_dict(),
        }

    def _detect_missing_signals(
        self, graph: TaskGraph, expectations: dict[str, Any]
    ) -> dict[str, list[str]]:
        missing: dict[str, list[str]] = {}
        for node in graph.topological_order():
            node_expectations = expectations.get(node.id) or expectations.get(node.phase or "")
            if not node_expectations:
                continue
            absent: list[str] = []
            for signal in node_expectations:
                if signal not in node.exit_signals:
                    absent.append(signal)
            if absent:
                missing[node.id] = absent
        return missing

