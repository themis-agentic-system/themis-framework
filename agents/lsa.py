"""Stub implementation for the LSA agent."""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent


class LSAAgent(BaseAgent):
    """Placeholder implementation to be filled in with domain logic."""

    def __init__(self) -> None:
        super().__init__(name="lsa")

    async def run(self, matter: dict[str, Any]) -> dict[str, Any]:
        """Return a mocked response illustrating expected structure."""
        return {
            "agent": self.name,
            "summary": "TODO: implement lsa reasoning",
            "inputs": matter,
        }
