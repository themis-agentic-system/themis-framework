"""Unit tests for individual agent implementations."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agents.dea import DEAAgent
from agents.lda import LDAAgent
from agents.lsa import LSAAgent


@pytest.fixture()
def sample_matter() -> dict[str, object]:
    """Representative payload shared across agent scenarios."""

    return {
        "summary": "Alice retained counsel after Bob failed to deliver contracted goods.",
        "parties": ["Alice", "Bob"],
        "documents": [
            {
                "title": "Master Supply Agreement",
                "content": "Agreement executed on 2023-01-15 for delivery of custom parts.",
                "facts": [
                    "Alice and Bob entered a supply contract on 2023-01-15.",
                    "Bob agreed to deliver custom parts by March 1, 2023.",
                ],
                "date": "2023-01-15",
            },
            {
                "title": "Notice of Breach",
                "summary": "Alice notified Bob of material breach due to non-delivery on March 5, 2023.",
                "facts": [
                    "Alice provided written breach notice on March 5, 2023.",
                    "Bob did not cure within 10 days of notice.",
                ],
                "date": "2023-03-05",
            },
        ],
        "events": [
            {"date": "2023-01-15", "description": "Contract executed."},
            {"date": "2023-03-01", "description": "Delivery deadline passes without shipment."},
            {"date": "2023-03-05", "description": "Notice of breach sent."},
        ],
        "issues": [
            {
                "issue": "Breach of contract",
                "facts": ["Failure to deliver goods by the contractual deadline."],
            },
            "Damages for lost production time",
        ],
        "authorities": [
            {"cite": "Restatement (Second) of Contracts § 235", "summary": "Non-performance is breach."},
            "U.C.C. § 2-601",
        ],
        "goals": {
            "settlement": "Recover $50,000 and secure expedited replacement parts.",
            "fallback": "Seek partial refund and future discount.",
        },
        "strengths": ["Clear written agreement", "Prompt breach notice"],
        "weaknesses": ["Limited documentation of consequential damages"],
        "concessions": ["Extended delivery schedule if partial payment made."],
        "evidentiary_gaps": ["Need expert report on downtime losses."],
        "counterparty": "Bob's Fabrication LLC",
        "confidence_score": 72,
    }


def test_lda_agent_schema(sample_matter: dict[str, object]) -> None:
    agent = LDAAgent()
    result = asyncio.run(agent.run(sample_matter))

    assert result["agent"] == "lda"
    assert "facts" in result and isinstance(result["facts"], dict)
    assert result["facts"]["timeline"], "Expected timeline entries"
    assert "provenance" in result and "tools_used" in result["provenance"]
    assert "unresolved_issues" in result and isinstance(result["unresolved_issues"], list)


def test_dea_agent_schema(sample_matter: dict[str, object]) -> None:
    agent = DEAAgent()
    result = asyncio.run(agent.run(sample_matter))

    assert result["agent"] == "dea"
    assert "legal_analysis" in result and isinstance(result["legal_analysis"], dict)
    assert result["legal_analysis"]["issues"], "Expected identified issues"
    assert result["legal_analysis"]["authorities"], "Expected citations list"
    assert "provenance" in result and result["provenance"]["citations_considered"]
    assert "unresolved_issues" in result and isinstance(result["unresolved_issues"], list)


def test_lsa_agent_schema(sample_matter: dict[str, object]) -> None:
    agent = LSAAgent()
    result = asyncio.run(agent.run(sample_matter))

    assert result["agent"] == "lsa"
    assert "strategy" in result and isinstance(result["strategy"], dict)
    assert result["strategy"]["recommended_actions"], "Expected action items"
    assert "provenance" in result and result["provenance"]["tools_used"]
    assert "unresolved_issues" in result and isinstance(result["unresolved_issues"], list)


def test_agents_allow_tool_injection(sample_matter: dict[str, object]) -> None:
    captured: dict[str, Any] = {}

    def custom_parser(matter: dict[str, Any]) -> list[dict[str, Any]]:
        captured["lda_called"] = True
        return [
            {
                "document": "custom",
                "summary": "custom summary",
                "key_facts": ["custom fact"],
            }
        ]

    def custom_issue_spotter(matter: dict[str, Any]) -> list[dict[str, Any]]:
        captured["dea_called"] = True
        return [{"issue": "custom", "facts": []}]

    def custom_strategy_template(matter: dict[str, Any]) -> dict[str, Any]:
        captured["lsa_called"] = True
        return {
            "objectives": "Custom objective",
            "actions": ["Action"],
            "positions": {},
            "contingencies": [],
            "assumptions": [],
        }

    lda_agent = LDAAgent(tools={"document_parser": custom_parser})
    dea_agent = DEAAgent(tools={"issue_spotter": custom_issue_spotter})
    lsa_agent = LSAAgent(tools={"strategy_template": custom_strategy_template})

    asyncio.run(lda_agent.run(sample_matter))
    asyncio.run(dea_agent.run(sample_matter))
    asyncio.run(lsa_agent.run(sample_matter))

    assert captured == {"lda_called": True, "dea_called": True, "lsa_called": True}
