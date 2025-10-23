"""Implementation of the Doctrinal Evaluation Agent (DEA)."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Callable

from agents.base import BaseAgent
from tools.llm_client import get_llm_client


class DEAAgent(BaseAgent):
    """Produce legal theories, citations, and doctrinal analysis."""

    REQUIRED_TOOLS = ("issue_spotter", "citation_retriever")

    def __init__(self, *, tools: dict[str, Callable[..., Any]] | None = None) -> None:
        super().__init__(name="dea")
        default_tools: dict[str, Callable[..., Any]] = {
            "issue_spotter": _default_issue_spotter,
            "citation_retriever": _default_citation_retriever,
        }
        self.tools = default_tools | (tools or {})
        missing = [tool for tool in self.REQUIRED_TOOLS if tool not in self.tools]
        if missing:
            missing_csv = ", ".join(missing)
            raise ValueError(f"Missing required tools for DEA agent: {missing_csv}")

    async def _run(self, matter: dict[str, Any]) -> dict[str, Any]:
        """Derive legal issues and map them to supporting authorities."""

        spotted_issues = await self._call_tool("issue_spotter", matter)
        citations = await self._call_tool("citation_retriever", matter, spotted_issues)

        unresolved: list[str] = []
        if not spotted_issues:
            unresolved.append("No legal issues identified from the fact pattern.")
        if not citations:
            unresolved.append("Unable to locate supporting authorities for the issues raised.")

        legal_analysis = {
            "issues": spotted_issues,
            "authorities": citations,
            "analysis": await _synthesise_analysis(spotted_issues, citations, matter),
        }

        provenance = {
            "tools_used": list(self.tools.keys()),
            "citations_considered": [citation.get("cite") for citation in citations],
        }

        return self._build_response(
            core={"legal_analysis": legal_analysis},
            provenance=provenance,
            unresolved_issues=unresolved,
        )


async def _default_issue_spotter(matter: dict[str, Any]) -> list[dict[str, Any]]:
    """Identify legal issues using LLM analysis of the matter."""
    llm = get_llm_client()

    # Build context from matter
    context_parts = []
    if matter.get("summary") or matter.get("description"):
        context_parts.append(f"Matter: {matter.get('summary') or matter.get('description')}")
    if matter.get("parties"):
        context_parts.append(f"Parties: {', '.join(matter.get('parties', []))}")

    # Include facts if available from LDA output
    facts = matter.get("facts", {})
    if isinstance(facts, dict) and facts.get("fact_pattern_summary"):
        fact_list = facts["fact_pattern_summary"]
        if fact_list:
            context_parts.append(f"Key Facts:\n" + "\n".join(f"- {fact}" for fact in fact_list[:10]))

    context = "\n\n".join(context_parts)

    system_prompt = """You are a skilled legal analyst specializing in issue spotting. Your job is to:
1. Analyze fact patterns and identify all potential legal issues
2. Categorize issues by area of law (tort, contract, property, etc.)
3. Link each issue to the specific facts that give rise to it
4. Assess the strength/merit of each issue

Be thorough but focused on legally significant issues."""

    user_prompt = f"""Analyze this legal matter and identify all potential legal issues.

{context}

For each legal issue you identify, provide:
1. The issue name/description
2. The area of law (e.g., "Tort - Negligence", "Contract - Breach")
3. Supporting facts from the matter
4. A brief assessment of the issue's strength (strong/moderate/weak)

Respond in JSON format:
{{
  "issues": [
    {{
      "issue": "issue description",
      "area_of_law": "legal area",
      "facts": ["supporting fact 1", "supporting fact 2"],
      "strength": "strong/moderate/weak"
    }}
  ]
}}"""

    response_format = {
        "issues": [
            {
                "issue": "string",
                "area_of_law": "string",
                "facts": ["string"],
                "strength": "string",
            }
        ]
    }

    try:
        result = await llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format=response_format,
        )
        return result.get("issues", [])
    except Exception as e:
        # Fallback to extracting from matter payload
        issues: list[dict[str, Any]] = []
        for entry in matter.get("issues", []):
            if isinstance(entry, str):
                issues.append({"issue": entry, "facts": [], "area_of_law": "Unknown"})
            elif isinstance(entry, dict):
                issue_label = entry.get("issue") or entry.get("label")
                if issue_label:
                    issues.append(
                        {
                            "issue": issue_label,
                            "facts": entry.get("facts", []),
                            "area_of_law": entry.get("area_of_law", "Unknown"),
                        }
                    )
        return issues


def _default_citation_retriever(
    matter: dict[str, Any],
    issues: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return a list of candidate authorities relevant to the issues."""

    authorities = []
    for authority in matter.get("authorities", []):
        if isinstance(authority, dict) and authority.get("cite"):
            authorities.append(authority)
        elif isinstance(authority, str):
            authorities.append({"cite": authority, "summary": "Reference provided as free text."})

    if not authorities and issues:
        for issue in issues:
            authorities.append(
                {
                    "cite": f"Secondary research required for issue: {issue['issue']}",
                    "summary": "No authority supplied; follow-up research needed.",
                }
            )

    return authorities


async def _synthesise_analysis(
    issues: list[dict[str, Any]],
    citations: list[dict[str, Any]],
    matter: dict[str, Any],
) -> str:
    """Create a legal analysis narrative using LLM."""
    if not issues:
        return "No issues identified to analyse."

    llm = get_llm_client()

    # Build context
    issues_text = "\n".join(
        f"- {i+1}. {issue.get('issue')} (Area: {issue.get('area_of_law', 'N/A')}, "
        f"Strength: {issue.get('strength', 'N/A')})"
        for i, issue in enumerate(issues)
    )

    citations_text = "\n".join(
        f"- {cite.get('cite')}: {cite.get('summary', 'No summary')}"
        for cite in citations
        if cite.get("cite")
    )

    system_prompt = """You are a legal expert writing doctrinal analysis. Your job is to:
1. Synthesize legal issues and authorities into a coherent analysis
2. Apply legal precedents to the facts
3. Explain how each authority supports or undermines each issue
4. Provide a clear, professional legal analysis

Write in a formal but clear legal style."""

    user_prompt = f"""Write a legal analysis synthesizing these issues and authorities.

Matter Context: {matter.get('summary') or matter.get('description', 'N/A')}
Parties: {', '.join(matter.get('parties', ['N/A']))}

Legal Issues Identified:
{issues_text}

Authorities:
{citations_text if citations_text else 'No specific authorities cited - requires research'}

Provide a comprehensive legal analysis (3-5 paragraphs) that:
1. Analyzes each legal issue in light of the facts
2. Applies relevant authorities to support or challenge each issue
3. Identifies gaps requiring additional research
4. Provides preliminary conclusions on the strength of each claim"""

    try:
        analysis = await llm.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=2000,
        )
        return analysis
    except Exception:
        # Fallback to simple synthesis
        party_context = ", ".join(matter.get("parties", []))
        lead_issue = issues[0]["issue"]
        cited_strings = [citation.get("cite") for citation in citations if citation.get("cite")]
        if cited_strings:
            cite_text = "; ".join(cited_strings)
            return f"Primary issue '{lead_issue}' for parties {party_context or 'N/A'} is supported by {cite_text}."
        return (
            f"Primary issue '{lead_issue}' for parties {party_context or 'N/A'} lacks direct authority "
            "and requires additional research."
        )
