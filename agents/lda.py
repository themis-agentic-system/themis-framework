"""Implementation of the Legal Docket Analysis (LDA) agent."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime
from typing import Any

from agents.base import BaseAgent
from agents.tooling import ToolSpec
from tools.document_parser import parse_document_with_llm


class LDAAgent(BaseAgent):
    """Summarise the fact pattern from the incoming matter payload.

    Enhanced with code execution capabilities for:
    - Damages calculations (economic, non-economic, punitive)
    - Statistical analysis of case data
    - Timeline gap analysis
    - Financial modeling for settlement ranges
    """

    REQUIRED_TOOLS = ("document_parser", "timeline_builder")

    def __init__(
        self,
        *,
        tools: Iterable[ToolSpec] | dict[str, Callable[..., Any]] | None = None,
        enable_code_execution: bool = True,
    ) -> None:
        super().__init__(name="lda")
        self.enable_code_execution = enable_code_execution

        default_tools = [
            ToolSpec(
                name="document_parser",
                description="Parse source documents and extract salient facts.",
                fn=_default_document_parser,
                input_schema={
                    "type": "object",
                    "properties": {"documents": {"type": "array"}},
                },
                output_schema={"type": "array"},
            ),
            ToolSpec(
                name="timeline_builder",
                description="Construct a chronological sequence of key events.",
                fn=_default_timeline_builder,
                input_schema={"type": "object"},
                output_schema={"type": "array"},
            ),
            ToolSpec(
                name="damages_calculator",
                description="Calculate damages (economic, non-economic, punitive) using computational analysis.",
                fn=_damages_calculator,
                input_schema={
                    "type": "object",
                    "properties": {
                        "economic_losses": {"type": "object"},
                        "non_economic_factors": {"type": "object"},
                        "punitive_factors": {"type": "object"},
                    },
                },
                output_schema={"type": "object"},
            ),
            ToolSpec(
                name="timeline_analyzer",
                description="Analyze timeline for gaps, patterns, and critical periods using statistical methods.",
                fn=_timeline_analyzer,
                input_schema={
                    "type": "object",
                    "properties": {"timeline": {"type": "array"}},
                },
                output_schema={"type": "object"},
            ),
        ]
        self.register_tools(default_tools)

        if tools:
            if isinstance(tools, dict):
                self.register_tools(list(tools.items()))
            else:
                self.register_tools(tools)

        self.require_tools(self.REQUIRED_TOOLS)

    async def _run(self, matter: dict[str, Any]) -> dict[str, Any]:
        """Derive a structured fact summary from the provided matter."""

        parsed_documents = await self._call_tool("document_parser", matter)
        timeline = await self._call_tool("timeline_builder", matter, parsed_documents)

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

        # Enhanced: Add computational analysis if code execution enabled
        if self.enable_code_execution:
            # Calculate damages if damage data is available
            damages_data = matter.get("damages")
            if damages_data:
                try:
                    damages_analysis = await self._call_tool("damages_calculator", damages_data)
                    facts_payload["damages_analysis"] = damages_analysis
                except Exception as e:
                    unresolved.append(f"Unable to complete damages calculation: {e!s}")

            # Analyze timeline for patterns and gaps
            if timeline:
                try:
                    timeline_analysis = await self._call_tool("timeline_analyzer", {"timeline": timeline})
                    facts_payload["timeline_analysis"] = timeline_analysis
                except Exception as e:
                    unresolved.append(f"Unable to complete timeline analysis: {e!s}")

        provenance = {
            "source_documents": [doc.get("document") for doc in parsed_documents],
            "tools_used": list(self.tools.keys()),
            "code_execution_enabled": self.enable_code_execution,
        }

        return self._build_response(
            core={"facts": facts_payload},
            provenance=provenance,
            unresolved_issues=unresolved,
        )


async def _default_document_parser(matter: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract document summaries and key facts using LLM.

    This is now a properly async function that can be awaited.
    """
    documents: Iterable[dict[str, Any]] = matter.get("documents", [])
    parsed: list[dict[str, Any]] = []

    # Extract matter context for better analysis
    matter_context = {
        "summary": matter.get("summary") or matter.get("description"),
        "parties": matter.get("parties", []),
    }

    for document in documents:
        try:
            # Use LLM-powered parser
            parsed_doc = await parse_document_with_llm(document, matter_context)
            parsed.append(parsed_doc)
        except Exception as e:
            # Fallback to basic parsing if LLM fails
            title = document.get("title") or "Untitled Document"
            parsed.append(
                {
                    "document": title,
                    "summary": f"Error parsing document: {e!s}",
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


async def _damages_calculator(damages_data: dict[str, Any]) -> dict[str, Any]:
    """Calculate total damages using computational analysis.

    This tool can leverage Claude's code execution capability when available
    for accurate financial calculations, projections, and statistical analysis.

    Args:
        damages_data: Dictionary containing:
            - economic_losses: Dict of economic damages (medical, lost wages, etc.)
            - non_economic_factors: Dict of non-economic factors (pain/suffering, etc.)
            - punitive_factors: Dict of punitive damage factors (if applicable)

    Returns:
        Dictionary with calculated totals, breakdowns, and analysis.
    """
    from tools.llm_client import get_llm_client

    client = get_llm_client()

    # Prepare prompt for calculation
    prompt = f"""Calculate total damages from the following data:

Economic Losses: {damages_data.get('economic_losses', {})}
Non-Economic Factors: {damages_data.get('non_economic_factors', {})}
Punitive Factors: {damages_data.get('punitive_factors', {})}

Provide a detailed breakdown including:
1. Total economic damages (sum of all economic losses)
2. Non-economic damages estimate (based on factors provided)
3. Punitive damages (if applicable)
4. Grand total with confidence interval
5. Settlement range recommendation (60-80% of total for settlement strategy)

Return as JSON with the structure:
{{
    "economic_total": float,
    "non_economic_estimate": float,
    "punitive_total": float,
    "grand_total": float,
    "confidence_level": str,
    "settlement_range": {{"min": float, "max": float}},
    "breakdown": dict
}}
"""

    try:
        result = await client.generate_structured(
            system_prompt="You are a legal damages calculator. Perform accurate financial calculations.",
            user_prompt=prompt,
            response_format={
                "economic_total": 0.0,
                "non_economic_estimate": 0.0,
                "punitive_total": 0.0,
                "grand_total": 0.0,
                "confidence_level": "medium",
                "settlement_range": {"min": 0.0, "max": 0.0},
                "breakdown": {},
            },
        )
        return result
    except Exception as e:
        # Fallback to simple summation
        economic = damages_data.get("economic_losses", {})
        economic_total = sum(float(v) for v in economic.values() if isinstance(v, (int, float)))

        return {
            "economic_total": economic_total,
            "non_economic_estimate": 0.0,
            "punitive_total": 0.0,
            "grand_total": economic_total,
            "confidence_level": "low",
            "settlement_range": {"min": economic_total * 0.6, "max": economic_total * 0.8},
            "breakdown": {"economic": economic},
            "error": str(e),
        }


async def _timeline_analyzer(timeline_data: dict[str, Any]) -> dict[str, Any]:
    """Analyze timeline for gaps, patterns, and critical periods.

    Uses computational analysis to identify:
    - Timeline gaps (periods with no recorded events)
    - Event clustering (periods of high activity)
    - Critical dates and deadlines
    - Statistical patterns in event distribution

    Args:
        timeline_data: Dictionary containing 'timeline' list of events.

    Returns:
        Dictionary with analysis results.
    """
    from tools.llm_client import get_llm_client

    client = get_llm_client()
    timeline = timeline_data.get("timeline", [])

    if not timeline:
        return {"gaps": [], "clusters": [], "critical_periods": [], "summary": "No timeline data available"}

    prompt = f"""Analyze the following timeline for legal case planning:

Timeline Events:
{timeline}

Provide analysis including:
1. Timeline gaps (periods >30 days between events)
2. Event clusters (3+ events within 14 days)
3. Critical periods (high activity indicating important case developments)
4. Duration from first to last event
5. Average time between events
6. Recommendations for additional fact development

Return as JSON with structure:
{{
    "duration_days": int,
    "total_events": int,
    "gaps": [{{"start_date": str, "end_date": str, "days": int}}],
    "clusters": [{{"period": str, "event_count": int, "significance": str}}],
    "critical_periods": [str],
    "average_gap_days": float,
    "recommendations": [str]
}}
"""

    try:
        result = await client.generate_structured(
            system_prompt="You are a legal timeline analyst. Analyze event sequences for patterns and gaps.",
            user_prompt=prompt,
            response_format={
                "duration_days": 0,
                "total_events": 0,
                "gaps": [],
                "clusters": [],
                "critical_periods": [],
                "average_gap_days": 0.0,
                "recommendations": [],
            },
        )
        return result
    except Exception as e:
        # Fallback to basic analysis
        valid_dates = []
        for event in timeline:
            date_str = event.get("date")
            if date_str:
                try:
                    valid_dates.append(datetime.fromisoformat(date_str))
                except (TypeError, ValueError):
                    pass

        duration = 0
        if len(valid_dates) >= 2:
            valid_dates.sort()
            duration = (valid_dates[-1] - valid_dates[0]).days

        return {
            "duration_days": duration,
            "total_events": len(timeline),
            "gaps": [],
            "clusters": [],
            "critical_periods": [],
            "average_gap_days": duration / max(len(valid_dates) - 1, 1) if valid_dates else 0,
            "recommendations": ["Manual timeline review recommended"],
            "error": str(e),
        }
