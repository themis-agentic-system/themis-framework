"""Agent protocol definitions for Themis."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol


class AgentProtocol(Protocol):
    """Minimal interface that all orchestrated agents must satisfy."""

    name: str

    async def run(self, matter: dict[str, Any]) -> dict[str, Any]:
        """Execute the agent given the current matter context."""


class BaseAgent(ABC):
    """Helper base class implementing shared plumbing for agents."""

    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    async def run(self, matter: dict[str, Any]) -> dict[str, Any]:
        """Execute the agent logic."""
        raise NotImplementedError

    def _build_response(
        self,
        *,
        core: dict[str, Any],
        provenance: dict[str, Any],
        unresolved_issues: list[str],
    ) -> dict[str, Any]:
        """Merge common response fields with validation safeguards.

        Every agent response must expose provenance information describing
        the materials or tools used as well as an explicit list of
        unresolved issues.  The unresolved list may be empty when the agent
        has nothing to escalate, but it must always be present to ensure the
        orchestrator can reason about follow-up work.
        """

        if not isinstance(provenance, dict) or not provenance:
            raise ValueError(
                f"{self.name} agent requires non-empty provenance metadata",
            )
        if not isinstance(unresolved_issues, list):
            raise ValueError(
                f"{self.name} agent must provide a list of unresolved issues",
            )

        return {
            "agent": self.name,
            **core,
            "provenance": provenance,
            "unresolved_issues": unresolved_issues,
        }
