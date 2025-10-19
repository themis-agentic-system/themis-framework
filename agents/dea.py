"""Implementation of the Doctrinal Evaluation Agent (DEA)."""

from __future__ import annotations

from typing import Any, Callable

from agents.base import BaseAgent


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

    async def run(self, matter: dict[str, Any]) -> dict[str, Any]:
        """Derive legal issues and map them to supporting authorities."""

        spotted_issues = self.tools["issue_spotter"](matter)
        citations = self.tools["citation_retriever"](matter, spotted_issues)

        unresolved: list[str] = []
        if not spotted_issues:
            unresolved.append("No legal issues identified from the fact pattern.")
        if not citations:
            unresolved.append("Unable to locate supporting authorities for the issues raised.")

        legal_analysis = {
            "issues": spotted_issues,
            "authorities": citations,
            "analysis": _synthesise_analysis(spotted_issues, citations, matter),
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


def _default_issue_spotter(matter: dict[str, Any]) -> list[dict[str, Any]]:
    """Pull out high-level legal issues from the matter payload."""

    issues: list[dict[str, Any]] = []
    for entry in matter.get("issues", []):
        if isinstance(entry, str):
            issues.append({"issue": entry, "facts": []})
        elif isinstance(entry, dict):
            issue_label = entry.get("issue") or entry.get("label")
            if issue_label:
                issues.append(
                    {
                        "issue": issue_label,
                        "facts": entry.get("facts", []),
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


def _synthesise_analysis(
    issues: list[dict[str, Any]],
    citations: list[dict[str, Any]],
    matter: dict[str, Any],
) -> str:
    """Create a short doctrinal narrative connecting issues and cites."""

    if not issues:
        return "No issues identified to analyse."

    party_context = ", ".join(matter.get("parties", []))
    lead_issue = issues[0]["issue"]
    cited_strings = [citation.get("cite") for citation in citations if citation.get("cite")]
    if cited_strings:
        cite_text = "; ".join(cited_strings)
        return (
            f"Primary issue '{lead_issue}' for parties {party_context or 'N/A'} is supported by {cite_text}."
        )
    return (
        f"Primary issue '{lead_issue}' for parties {party_context or 'N/A'} lacks direct authority and"
        " requires additional research."
    )
