"""Reusable task-graph template with baked-in guardrails."""

from __future__ import annotations

from typing import Any

from orchestrator.policy import Phase, PhaseDefinition, RoutingPolicy


def build_standard_template(**overrides: Any) -> RoutingPolicy:
    """Return a RoutingPolicy configured with guardrail connectors.

    The template mirrors the default policy but demonstrates how to inject
    connector requirements so downstream agents automatically receive
    resources like precedent libraries or CRM context.
    """

    policy = RoutingPolicy()
    phase_defs: list[PhaseDefinition] = []
    for definition in policy.phase_definitions:
        required_connectors: list[str] = []
        if definition.phase is Phase.RESEARCH_RETRIEVAL:
            required_connectors = ["vector_research", "precedent_db"]
        elif definition.phase is Phase.DRAFT_REVIEW:
            required_connectors = ["style_guide", "safety_rules"]
        phase_defs.append(
            PhaseDefinition(
                phase=definition.phase,
                description=definition.description,
                default_primary_agent=definition.default_primary_agent,
                expected_artifacts=definition.expected_artifacts,
                exit_signals=definition.exit_signals,
                entry_signals=definition.entry_signals,
                supporting_agents=definition.supporting_agents,
                required_connectors=required_connectors,
            )
        )
    policy._phase_definitions = phase_defs  # type: ignore[attr-defined]
    return policy

