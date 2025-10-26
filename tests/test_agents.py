"""Unit tests for individual agent implementations."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agents.dda import DocumentDraftingAgent
from agents.dea import DEAAgent
from agents.lda import LDAAgent
from agents.lsa import LSAAgent


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


def test_document_drafting_agent_schema(sample_matter: dict[str, object]) -> None:
    agent = DocumentDraftingAgent()
    result = asyncio.run(agent.run(sample_matter))

    assert result["agent"] == "dda"
    assert "document" in result and isinstance(result["document"], dict)
    assert result["document"]["full_text"], "Expected document text"
    assert "metadata" in result and isinstance(result["metadata"], dict)
    assert "provenance" in result and "tools_used" in result["provenance"]
    assert "unresolved_issues" in result and isinstance(result["unresolved_issues"], list)


def test_document_drafting_agent_tool_injection(sample_matter: dict[str, object]) -> None:
    captured: dict[str, Any] = {}

    async def custom_section_generator(
        document_type: str,
        facts: dict[str, Any],
        legal_analysis: dict[str, Any],
        strategy: dict[str, Any],
        jurisdiction: str,
    ) -> dict[str, Any]:
        captured["section_generator_called"] = True
        return {
            "caption": "CUSTOM CAPTION",
            "introduction": "Custom intro",
            "facts_section": "Custom facts",
            "argument_section": "Custom argument",
            "conclusion": "Custom conclusion",
        }

    async def custom_document_composer(
        document_type: str,
        sections: dict[str, Any],
        citations: dict[str, Any],
        jurisdiction: str,
        matter: dict[str, Any],
    ) -> dict[str, Any]:
        captured["composer_called"] = True
        return {
            "full_text": "Custom document text",
            "word_count": 100,
            "page_estimate": 1,
            "sections": list(sections.keys()),
            "citation_count": 0,
        }

    agent = DocumentDraftingAgent(
        tools={
            "section_generator": custom_section_generator,
            "document_composer": custom_document_composer,
        }
    )
    asyncio.run(agent.run(sample_matter))

    assert captured == {"section_generator_called": True, "composer_called": True}
