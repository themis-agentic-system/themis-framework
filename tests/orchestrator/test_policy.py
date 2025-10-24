"""Unit tests for the routing policy."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from orchestrator.policy import RoutingPolicy


def test_routing_policy_builds_expected_phases():
    policy = RoutingPolicy()
    steps = policy.build_plan({"objective": "Evaluate negligence exposure"})

    phases = [step["phase"] for step in steps]
    assert phases == [
        "intake_facts",
        "issue_framing",
        "research_retrieval",
        "application_analysis",
        "draft_review",
    ]
    assert steps[0]["agent"] == "lda"
    assert steps[1]["agent"] == "dea"
    assert steps[-1]["agent"] == "lsa"
    assert any(step.get("supporting_agents") for step in steps)


def test_routing_policy_selects_agents_based_on_intent():
    policy = RoutingPolicy()

    damages_steps = policy.build_plan({"objective": "Compute damages timeline"})
    issue_step = next(step for step in damages_steps if step["phase"] == "issue_framing")
    application_step = next(
        step for step in damages_steps if step["phase"] == "application_analysis"
    )
    assert issue_step["agent"] == "lda"
    assert application_step["agent"] == "lda"

    negotiation_steps = policy.build_plan({"objective": "Draft settlement demand letter"})
    draft_step = next(step for step in negotiation_steps if step["phase"] == "draft_review")
    assert draft_step["agent"] == "lsa"
