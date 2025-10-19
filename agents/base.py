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
