"""Registry for tools that agents can call."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class ToolRegistry:
    """Lightweight registry used during scaffolding."""

    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, tool: Callable[..., Any]) -> None:
        """Register a callable tool by name."""
        self._tools[name] = tool

    def get(self, name: str) -> Callable[..., Any]:
        """Retrieve a tool or raise a `KeyError`."""
        return self._tools[name]

    def available(self) -> list[str]:
        """List registered tool names."""
        return sorted(self._tools)
