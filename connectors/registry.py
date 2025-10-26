"""Connector specification and registry utilities."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ConnectorSpec:
    """Metadata describing a pluggable external connector."""

    name: str
    connector: Any
    capabilities: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "capabilities": sorted(self.capabilities),
            "metadata": dict(self.metadata),
        }


class ConnectorRegistry:
    """Simple registry for mounting connectors into agent runs."""

    def __init__(self, specs: Iterable[ConnectorSpec] | None = None) -> None:
        self._specs: dict[str, ConnectorSpec] = {}
        if specs:
            for spec in specs:
                self.register(spec)

    def register(self, spec: ConnectorSpec) -> None:
        self._specs[spec.name] = spec

    def resolve(self, names: Iterable[str]) -> dict[str, Any]:
        resolved: dict[str, Any] = {}
        for name in names:
            spec = self._specs.get(name)
            if spec:
                resolved[name] = spec.connector
        return resolved

    def catalogue(self) -> list[dict[str, Any]]:
        return [spec.describe() for spec in self._specs.values()]

    def __contains__(self, name: str) -> bool:  # pragma: no cover - convenience
        return name in self._specs

