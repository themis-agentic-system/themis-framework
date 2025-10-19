"""Shared orchestrator state and memory primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OrchestratorState:
    """In-memory state for orchestration scaffolding."""

    memory: dict[str, Any] = field(default_factory=dict)
    plans: dict[str, dict[str, Any]] = field(default_factory=dict)
    executions: dict[str, dict[str, Any]] = field(default_factory=dict)

    def remember(self, key: str, value: Any) -> None:
        """Persist miscellaneous information into the shared memory."""
        self.memory[key] = value

    def recall(self, key: str, default: Any | None = None) -> Any | None:
        """Retrieve a value stored in memory."""
        return self.memory.get(key, default)

    def remember_plan(self, plan_id: str, plan: dict[str, Any]) -> None:
        """Persist a plan definition for later execution."""
        self.plans[plan_id] = plan

    def recall_plan(self, plan_id: str) -> dict[str, Any] | None:
        """Retrieve a plan definition by identifier."""
        return self.plans.get(plan_id)

    def remember_execution(self, plan_id: str, execution: dict[str, Any]) -> None:
        """Persist the results of executing a plan."""
        self.executions[plan_id] = execution

    def recall_execution(self, plan_id: str) -> dict[str, Any] | None:
        """Retrieve an execution record by the associated plan identifier."""
        return self.executions.get(plan_id)
