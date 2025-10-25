"""Tool capability definitions shared across agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(slots=True)
class ToolSpec:
    """Structured description of an agent capability/tool."""

    name: str
    description: str
    fn: Callable[..., Any]
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    resources: dict[str, Any] = field(default_factory=dict)
    streaming: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def invoke(self, *args: Any, **kwargs: Any) -> Any:
        return self.fn(*args, **kwargs)

    @classmethod
    def ensure(cls, name: str, candidate: "ToolSpec | Callable[..., Any]", *, description: str | None = None) -> "ToolSpec":
        if isinstance(candidate, cls):
            return candidate
        return cls(name=name, description=description or f"Callable tool '{name}'", fn=candidate)


__all__ = ["ToolSpec"]
