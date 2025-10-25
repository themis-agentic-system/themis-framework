"""Structured tracing helpers for orchestrator observability."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Iterable


@dataclass(slots=True)
class TraceEvent:
    """Represents a discrete orchestration event for debugging or replay."""

    timestamp: float
    event: str
    payload: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {"timestamp": self.timestamp, "event": self.event, "payload": self.payload}


class TraceRecorder:
    """Collects structured trace events during plan execution."""

    def __init__(self) -> None:
        self._events: list[TraceEvent] = []

    def record(self, event: str, **payload: Any) -> None:
        """Append a trace event with the current timestamp."""

        self._events.append(TraceEvent(timestamp=time.time(), event=event, payload=payload))

    def extend(self, events: Iterable[TraceEvent]) -> None:
        for event in events:
            self._events.append(event)

    def flush(self) -> list[dict[str, Any]]:
        """Return accumulated events as serialisable dictionaries."""

        return [event.as_dict() for event in self._events]

    def reset(self) -> None:  # pragma: no cover - convenience
        self._events.clear()

