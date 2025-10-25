"""Task graph primitives for orchestrating agent workflows."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Iterator


@dataclass(slots=True)
class TaskNode:
    """Represents a single unit of work in an orchestration graph."""

    id: str
    agent: str
    phase: str | None = None
    description: str | None = None
    dependencies: list[str] = field(default_factory=list)
    successors: list[str] = field(default_factory=list)
    expected_artifacts: list[dict[str, Any]] = field(default_factory=list)
    supporting_agents: list[dict[str, Any]] = field(default_factory=list)
    exit_signals: list[str] = field(default_factory=list)
    entry_signals: list[str] = field(default_factory=list)
    required_connectors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable payload for the node."""

        payload = {
            "id": self.id,
            "agent": self.agent,
            "phase": self.phase,
            "description": self.description,
            "dependencies": list(self.dependencies),
            "successors": list(self.successors),
            "expected_artifacts": list(self.expected_artifacts),
            "supporting_agents": list(self.supporting_agents),
            "exit_signals": list(self.exit_signals),
            "entry_signals": list(self.entry_signals),
            "required_connectors": list(self.required_connectors),
            "metadata": dict(self.metadata),
        }
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TaskNode":
        """Instantiate a :class:`TaskNode` from a serialised payload."""

        return cls(
            id=payload["id"],
            agent=payload["agent"],
            phase=payload.get("phase"),
            description=payload.get("description"),
            dependencies=list(payload.get("dependencies", [])),
            successors=list(payload.get("successors", [])),
            expected_artifacts=list(payload.get("expected_artifacts", [])),
            supporting_agents=list(payload.get("supporting_agents", [])),
            exit_signals=list(payload.get("exit_signals", [])),
            entry_signals=list(payload.get("entry_signals", [])),
            required_connectors=list(payload.get("required_connectors", [])),
            metadata=dict(payload.get("metadata", {})),
        )


class TaskGraph:
    """A directed acyclic graph describing the orchestrated workflow."""

    def __init__(self, nodes: Iterable[TaskNode] | None = None) -> None:
        self._nodes: dict[str, TaskNode] = {}
        if nodes:
            for node in nodes:
                self.add_node(node)

    def __contains__(self, node_id: str) -> bool:  # pragma: no cover - convenience
        return node_id in self._nodes

    def __iter__(self) -> Iterator[TaskNode]:  # pragma: no cover - convenience
        return iter(self._nodes.values())

    def add_node(self, node: TaskNode) -> None:
        """Register a node with the graph, overriding existing metadata."""

        self._nodes[node.id] = node

    def add_edge(self, source_id: str, target_id: str) -> None:
        """Connect two nodes, enforcing DAG semantics."""

        source = self._nodes[source_id]
        target = self._nodes[target_id]
        if target_id not in source.successors:
            source.successors.append(target_id)
        if source_id not in target.dependencies:
            target.dependencies.append(source_id)

    def get(self, node_id: str) -> TaskNode:
        return self._nodes[node_id]

    def nodes(self) -> dict[str, TaskNode]:  # pragma: no cover - convenience
        return dict(self._nodes)

    def as_dict(self) -> dict[str, Any]:
        """Serialise the graph for persistence."""

        return {node_id: node.as_dict() for node_id, node in self._nodes.items()}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TaskGraph":
        """Rehydrate a :class:`TaskGraph` from persisted metadata."""

        nodes = [TaskNode.from_dict(node_data) for node_data in payload.values()]
        graph = cls(nodes)
        # Ensure successor/dependency symmetry after loading
        for node in graph._nodes.values():
            for successor in node.successors:
                if successor not in graph._nodes:
                    continue
                graph._nodes[successor].dependencies = list(
                    dict.fromkeys(graph._nodes[successor].dependencies + [node.id])
                )
        return graph

    @classmethod
    def from_linear_steps(cls, steps: Iterable[dict[str, Any]]) -> "TaskGraph":
        """Create a graph from a simple sequential plan."""

        nodes: list[TaskNode] = []
        previous: TaskNode | None = None
        for step in steps:
            node = TaskNode(
                id=step["id"],
                agent=step["agent"],
                phase=step.get("phase"),
                description=step.get("description"),
                dependencies=list(step.get("dependencies", [])),
                expected_artifacts=list(step.get("expected_artifacts", [])),
                supporting_agents=list(step.get("supporting_agents", [])),
                exit_signals=list(step.get("exit_signals", [])),
                entry_signals=list(step.get("entry_signals", [])),
                required_connectors=list(step.get("required_connectors", [])),
                metadata=dict(step.get("metadata", {})),
            )
            if previous:
                node.dependencies = [previous.id]
                previous.successors = [node.id]
            nodes.append(node)
            previous = node
        return cls(nodes)

    def topological_order(self) -> list[TaskNode]:
        """Return nodes ordered via Kahn's algorithm."""

        indegree: Dict[str, int] = {
            node_id: len(node.dependencies) for node_id, node in self._nodes.items()
        }
        queue: deque[str] = deque(
            node_id for node_id, degree in indegree.items() if degree == 0
        )
        ordered: list[TaskNode] = []
        while queue:
            node_id = queue.popleft()
            node = self._nodes[node_id]
            ordered.append(node)
            for successor_id in node.successors:
                if successor_id not in indegree:
                    continue
                indegree[successor_id] -= 1
                if indegree[successor_id] == 0:
                    queue.append(successor_id)
        if len(ordered) != len(self._nodes):  # pragma: no cover - defensive
            raise ValueError("Task graph contains a cycle or disconnected component.")
        return ordered

    def to_linear_steps(self) -> list[dict[str, Any]]:
        """Project the DAG into a compatible list of steps for clients."""

        steps: list[dict[str, Any]] = []
        for node in self.topological_order():
            payload = node.as_dict()
            payload.pop("successors", None)
            steps.append(payload)
        return steps

    def iter_ready(self, completed: Iterable[str]) -> Iterator[TaskNode]:
        """Yield nodes whose dependencies are satisfied by ``completed``."""

        completed_set = set(completed)
        for node in self.topological_order():
            if all(dep in completed_set for dep in node.dependencies):
                yield node

