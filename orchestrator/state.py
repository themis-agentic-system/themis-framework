"""Shared orchestrator state and memory primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OrchestratorState:
    """In-memory state for orchestration scaffolding."""

    memory: dict[str, Any] = field(default_factory=dict)

    def remember(self, key: str, value: Any) -> None:
        """Persist information into the shared memory."""
        self.memory[key] = value

    def recall(self, key: str, default: Any | None = None) -> Any | None:
        """Retrieve a value stored in memory."""
        return self.memory.get(key, default)
