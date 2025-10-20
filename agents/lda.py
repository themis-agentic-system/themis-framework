"""Implementation of the Legal Docket Analysis (LDA) agent."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Iterable

from agents.base import BaseAgent
from tools.document_parser import parse_document_with_llm
from tools.llm_client import get_llm_client


class LDAAgent(BaseAgent):
    """Summarise the fact pattern from the incoming matter payload."""

    REQUIRED_TOOLS = ("document_parser", "timeline_builder")

    def __init__(self, *, tools: dict[str, Callable[..., Any]] | None = None) -> None:
        super().__init__(name="lda")
        default_tools: dict[str, Callable[..., Any]] = {
            "document_parser": _default_document_parser,
            "timeline_builder": _default_timeline_builder,
        }
        self.tools = default_tools | (tools or {})
        missing = [tool for tool in self.REQUIRED_TOOLS if tool not in self.tools]
        if missing:
            missing_csv = ", ".join(missing)
            raise ValueError(f"Missing required tools for LDA agent: {missing_csv}")

    async def _run(self, matter: dict[str, Any]) -> dict[str, Any]:
        """Derive a structured fact summary from the provided matter."""

        parsed_documents = self._call_tool("document_parser", matter)
        timeline = self._call_tool("timeline_builder", matter, parsed_documents)

        key_facts: list[str] = []
        for doc in parsed_documents:
            key_facts.extend(doc.get("key_facts", []))

        parties = list(dict.fromkeys(matter.get("parties", [])))
        unresolved: list[str] = []
        if not parsed_documents:
            unresolved.append("No source documents were provided for fact extraction.")
        if not parties:
            unresolved.append("Matter payload did not list any known parties.")

        facts_payload = {
            "fact_pattern_summary": key_facts,
            "timeline": timeline,
            "parties": parties,
            "matter_overview": matter.get("summary")
            or matter.get("description")
            or "Summary unavailable from provided matter.",
        }

        provenance = {
            "source_documents": [doc.get("document") for doc in parsed_documents],
            "tools_used": list(self.tools.keys()),
        }

        return self._build_response(
            core={"facts": facts_payload},
            provenance=provenance,
            unresolved_issues=unresolved,
        )


def _default_document_parser(matter: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract document summaries and key facts using LLM.

    This is a synchronous wrapper that can be called from async context.
    For true async usage, inject parse_document_with_llm directly.
    """
    import asyncio

    documents: Iterable[dict[str, Any]] = matter.get("documents", [])
    parsed: list[dict[str, Any]] = []

    # Get or create event loop for async operations
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Extract matter context for better analysis
    matter_context = {
        "summary": matter.get("summary") or matter.get("description"),
        "parties": matter.get("parties", []),
    }

    for document in documents:
        try:
            # Use LLM-powered parser
            parsed_doc = loop.run_until_complete(
                parse_document_with_llm(document, matter_context)
            )
            parsed.append(parsed_doc)
        except Exception as e:
            # Fallback to basic parsing if LLM fails
            title = document.get("title") or "Untitled Document"
            parsed.append(
                {
                    "document": title,
                    "summary": f"Error parsing document: {str(e)}",
                    "key_facts": [],
                    "date": document.get("date"),
                }
            )

    return parsed


def _default_timeline_builder(
    matter: dict[str, Any],
    parsed_documents: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Build a chronological list of events from the matter payload."""

    events: list[dict[str, Any]] = []
    for raw_event in matter.get("events", []):
        description = raw_event.get("description") or raw_event.get("summary")
        date_str = raw_event.get("date")
        events.append(
            {
                "date": date_str,
                "description": description or "Event description unavailable.",
            }
        )

    if not events and parsed_documents:
        for doc in parsed_documents:
            if doc.get("date"):
                events.append(
                    {
                        "date": doc["date"],
                        "description": f"Document produced: {doc['document']}",
                    }
                )

    def _sort_key(event: dict[str, Any]) -> tuple[int, str]:
        date_str = event.get("date")
        if not date_str:
            return (1, "")
        try:
            parsed_date = datetime.fromisoformat(date_str)
        except (TypeError, ValueError):
            return (0, date_str)
        return (0, parsed_date.isoformat())

    events.sort(key=_sort_key)
    return events
