"""Implementation of the Document Drafting Agent (DDA)."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from agents.base import BaseAgent
from agents.tooling import ToolSpec
from tools.llm_client import get_llm_client


def _normalise_party_roles(parties: Any) -> dict[str, str]:
    """Map arbitrary party payloads to plaintiff/defendant placeholders."""

    defaults = {"plaintiff": "PLAINTIFF NAME", "defendant": "DEFENDANT NAME"}
    if parties is None:
        return defaults.copy()

    # Direct mapping support
    if isinstance(parties, dict):
        normalised = defaults.copy()
        for role in defaults:
            value = parties.get(role)
            if isinstance(value, str) and value.strip():
                normalised[role] = value.strip()
        if normalised != defaults:
            return normalised

        # Fall back to the first non-empty string values
        names = [str(value).strip() for value in parties.values() if str(value).strip()]
        if names:
            normalised["plaintiff"] = names[0]
            if len(names) >= 2:
                normalised["defendant"] = names[1]
        return normalised

    # List of parties (strings or dicts)
    if isinstance(parties, list):
        normalised = defaults.copy()
        unnamed: list[str] = []
        for entry in parties:
            if isinstance(entry, str):
                name = entry.strip()
                if name:
                    unnamed.append(name)
                continue
            if isinstance(entry, dict):
                name_field = entry.get("name") or entry.get("party") or entry.get("full_name")
                role_field = entry.get("role") or entry.get("type") or entry.get("side")
                if isinstance(role_field, str) and isinstance(name_field, str):
                    role_lower = role_field.lower()
                    name = name_field.strip()
                    if not name:
                        continue
                    if any(tag in role_lower for tag in ("plaintiff", "claimant", "petitioner")):
                        normalised["plaintiff"] = name
                        continue
                    if any(tag in role_lower for tag in ("defendant", "respondent", "accused")):
                        normalised["defendant"] = name
                        continue
                    unnamed.append(name)
                    continue
                if isinstance(name_field, str) and name_field.strip():
                    unnamed.append(name_field.strip())
                continue
            if entry is not None:
                entry_str = str(entry).strip()
                if entry_str:
                    unnamed.append(entry_str)
        if normalised["plaintiff"] == defaults["plaintiff"] and unnamed:
            normalised["plaintiff"] = unnamed[0]
        if normalised["defendant"] == defaults["defendant"] and len(unnamed) >= 2:
            normalised["defendant"] = unnamed[1]
        return normalised

    if isinstance(parties, str) and parties.strip():
        return {"plaintiff": parties.strip(), "defendant": defaults["defendant"]}

    return defaults.copy()


class DocumentDraftingAgent(BaseAgent):
    """Draft formal legal documents using modern legal prose.

    Consumes outputs from LDA (facts), DEA (legal analysis), and LSA (strategy)
    to generate jurisdiction-compliant legal documents with proper formatting,
    citations, and structure.
    """

    REQUIRED_TOOLS = (
        "document_composer",
        "citation_formatter",
        "section_generator",
        "document_validator",
        "tone_analyzer",
    )

    def __init__(
        self,
        *,
        tools: Iterable[ToolSpec] | dict[str, Callable[..., Any]] | None = None,
    ) -> None:
        super().__init__(name="dda")

        default_tools = [
            ToolSpec(
                name="document_composer",
                description="Assembles multi-section legal documents from components.",
                fn=_default_document_composer,
                input_schema={"type": "object"},
                output_schema={"type": "object"},
            ),
            ToolSpec(
                name="citation_formatter",
                description="Formats legal citations according to jurisdiction standards.",
                fn=_default_citation_formatter,
                input_schema={"type": "object"},
                output_schema={"type": "object"},
            ),
            ToolSpec(
                name="section_generator",
                description="Generates specific document sections (facts, arguments, etc.).",
                fn=_default_section_generator,
                input_schema={"type": "object"},
                output_schema={"type": "object"},
            ),
            ToolSpec(
                name="document_validator",
                description="Validates document completeness and compliance.",
                fn=_default_document_validator,
                input_schema={"type": "object"},
                output_schema={"type": "object"},
            ),
            ToolSpec(
                name="tone_analyzer",
                description="Analyzes legal writing quality and tone appropriateness.",
                fn=_default_tone_analyzer,
                input_schema={"type": "object"},
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
        """Generate formal legal documents from aggregated matter data."""

        # Determine document type from matter - user should specify what they need
        document_type = matter.get("document_type") or matter.get("metadata", {}).get("document_type", "memorandum")
        jurisdiction = matter.get("jurisdiction") or matter.get("metadata", {}).get("jurisdiction", "federal")

        # Extract relevant data from prior agent outputs
        facts = matter.get("facts", {})
        legal_analysis = matter.get("legal_analysis", {})
        strategy = matter.get("strategy", {})

        # Generate document sections
        sections = await self._call_tool(
            "section_generator",
            document_type=document_type,
            facts=facts,
            legal_analysis=legal_analysis,
            strategy=strategy,
            jurisdiction=jurisdiction,
        )

        # Format citations
        formatted_citations = await self._call_tool(
            "citation_formatter",
            authorities=legal_analysis.get("authorities", []),
            jurisdiction=jurisdiction,
        )

        # Compose complete document
        document = await self._call_tool(
            "document_composer",
            document_type=document_type,
            sections=sections,
            citations=formatted_citations,
            jurisdiction=jurisdiction,
            matter=matter,
        )

        # Analyze tone and quality
        tone_analysis = await self._call_tool(
            "tone_analyzer",
            document=document,
            document_type=document_type,
        )

        # Validate document
        validation = await self._call_tool(
            "document_validator",
            document=document,
            document_type=document_type,
            matter=matter,
        )

        # Track unresolved issues
        unresolved: list[str] = []
        if not sections.get("facts_section"):
            unresolved.append("Unable to generate factual background section.")
        if validation.get("missing_elements"):
            unresolved.extend(
                f"Missing document element: {elem}"
                for elem in validation["missing_elements"]
            )
        if tone_analysis.get("issues"):
            unresolved.extend(
                f"Tone issue: {issue}"
                for issue in tone_analysis["issues"][:3]  # Top 3 issues
            )

        provenance = {
            "tools_used": list(self.tools.keys()),
            "document_type": document_type,
            "jurisdiction": jurisdiction,
            "sections_generated": list(sections.keys()),
            "citation_count": len(formatted_citations.get("citations", [])),
        }

        return self._build_response(
            core={
                "document": document,
                "metadata": {
                    "document_type": document_type,
                    "jurisdiction": jurisdiction,
                    "word_count": document.get("word_count", 0),
                    "section_count": len(sections),
                },
                "tone_analysis": tone_analysis,
                "validation": validation,
            },
            provenance=provenance,
            unresolved_issues=unresolved,
        )


async def _default_section_generator(
    document_type: str,
    facts: dict[str, Any],
    legal_analysis: dict[str, Any],
    strategy: dict[str, Any],
    jurisdiction: str,
) -> dict[str, Any]:
    """Generate document sections using LLM with modern legal prose."""
    llm = get_llm_client()

    # Build context from matter data
    context_parts = []

    # Facts
    if facts:
        fact_pattern = facts.get("fact_pattern_summary", [])
        if fact_pattern:
            context_parts.append("Facts:\n" + "\n".join(f"  - {f}" for f in fact_pattern))

        parties = facts.get("parties", {})
        if parties:
            context_parts.append(f"Parties: {parties}")

        timeline = facts.get("timeline", [])
        if timeline:
            timeline_summary = "\n".join(
                f"  {event.get('date', 'N/A')}: {event.get('description', 'N/A')}"
                for event in timeline[:10]
            )
            context_parts.append(f"Timeline:\n{timeline_summary}")

    # Legal analysis
    if legal_analysis:
        issues = legal_analysis.get("issues", [])
        if issues:
            issues_summary = "\n".join(
                f"  - {issue.get('issue')} (Strength: {issue.get('strength', 'N/A')})"
                for issue in issues
            )
            context_parts.append(f"Legal Issues:\n{issues_summary}")

        analysis = legal_analysis.get("analysis")
        if analysis:
            context_parts.append(f"Legal Analysis:\n{analysis[:1000]}")

        authorities = legal_analysis.get("authorities", [])
        if authorities:
            auth_summary = "\n".join(
                f"  - {auth.get('citation', 'N/A')}: {auth.get('holding', 'N/A')[:100]}"
                for auth in authorities[:5]
            )
            context_parts.append(f"Key Authorities:\n{auth_summary}")

    # Strategy
    if strategy:
        objectives = strategy.get("objectives")
        if objectives:
            context_parts.append(f"Strategic Objectives: {objectives}")

        positions = strategy.get("positions", {})
        if positions:
            context_parts.append(f"Negotiation Position: {positions}")

    context = "\n\n".join(context_parts)

    # Document type-specific system prompts
    system_prompts = {
        "complaint": """You are an expert legal writer specializing in civil complaints. Write using modern legal prose that is:
- Clear and concise (plain language movement principles)
- Properly structured (caption, jurisdiction, parties, facts, causes of action, prayer)
- Factually grounded and persuasive
- Compliant with pleading standards (notice pleading or fact pleading as appropriate)
- Free of legalese and unnecessary Latin phrases""",

        "demand_letter": """You are an expert legal writer specializing in demand letters. Write using modern legal prose that is:
- Professional but accessible
- Persuasive and fact-focused
- Clear about demands and consequences
- Free of unnecessary legalese
- Appropriate for settlement negotiations""",

        "motion": """You are an expert legal writer specializing in motions and briefs. Write using modern legal prose that is:
- Persuasive and well-organized (IRAC or similar structure)
- Grounded in controlling authority
- Clear and compelling
- Compliant with local rules and page limits
- Free of hyperbole and unnecessary adjectives""",

        "memorandum": """You are an expert legal writer specializing in legal memoranda. Write using modern legal prose that is:
- Objective and analytical
- Well-structured (Question Presented, Brief Answer, Facts, Discussion, Conclusion)
- Thoroughly researched with proper citations
- Clear and accessible
- Balanced in presenting both sides""",
    }

    system_prompt = system_prompts.get(
        document_type,
        system_prompts["memorandum"],  # Default to memo style
    )

    user_prompt = f"""Generate a formal {document_type} based on the following matter information:

{context}

Jurisdiction: {jurisdiction}

Generate the following sections in modern legal prose:

1. **Caption/Header** - Formal document header with case information
2. **Introduction** - Opening paragraph establishing purpose
3. **Facts** - Factual background section (objective, chronological)
4. **Legal Analysis/Argument** - Application of law to facts
5. **Conclusion** - Summary and relief requested

For each section, use clear, modern legal writing. Avoid unnecessary legalese. Use short sentences and active voice where possible.

Respond in JSON format:
{{
  "caption": "formatted caption/header",
  "introduction": "introduction paragraph(s)",
  "facts_section": "factual background narrative",
  "argument_section": "legal analysis/argument",
  "conclusion": "conclusion and prayer for relief"
}}"""

    response_format = {
        "caption": "string",
        "introduction": "string",
        "facts_section": "string",
        "argument_section": "string",
        "conclusion": "string",
    }

    try:
        result = await llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format=response_format,
            max_tokens=4000,
        )

        # Log the response for debugging
        import logging
        import json
        logger = logging.getLogger("themis.agents.dda")
        logger.info(f"Section generator LLM response: {result}")
        logger.info(f"Generated sections: {list(result.keys())}")

        # FIX: Handle case where LLM wraps response in 'response' key
        if 'response' in result and isinstance(result['response'], str):
            try:
                result = json.loads(result['response'])
                logger.info(f"Parsed nested JSON from 'response' key. Sections: {list(result.keys())}")
            except json.JSONDecodeError as parse_err:
                logger.error(f"Failed to parse nested JSON: {result['response'][:200]}", exc_info=True)

        return result
    except Exception as e:
        # Log the error so we can see what failed
        import logging
        logger = logging.getLogger("themis.agents.dda")
        logger.error(f"Section generator LLM call failed: {e!s}", exc_info=True)
        # Fallback to basic section generation
        caption = f"IN THE MATTER OF: {facts.get('parties', {}).get('plaintiff', 'N/A')}"
        introduction = f"This {document_type} addresses the legal issues arising from the facts presented below."

        fact_pattern = facts.get("fact_pattern_summary", [])
        facts_section = "\n\n".join(fact_pattern) if fact_pattern else "Facts to be provided."

        issues = legal_analysis.get("issues", [])
        argument_section = "\n\n".join(
            f"{issue.get('issue')}: {issue.get('analysis', 'Analysis pending.')}"
            for issue in issues
        ) if issues else "Legal analysis to be provided."

        conclusion = "For the foregoing reasons, the relief requested should be granted."

        return {
            "caption": caption,
            "introduction": introduction,
            "facts_section": facts_section,
            "argument_section": argument_section,
            "conclusion": conclusion,
        }


async def _default_citation_formatter(
    authorities: list[dict[str, Any]],
    jurisdiction: str,
) -> dict[str, Any]:
    """Format legal citations according to jurisdiction standards."""
    llm = get_llm_client()

    if not authorities:
        return {"citations": [], "formatted_count": 0}

    # Build authority list
    authority_list = "\n".join(
        f"{i+1}. {auth.get('citation', 'N/A')}: {auth.get('holding', 'N/A')[:200]}"
        for i, auth in enumerate(authorities[:20])  # Limit to 20 authorities
    )

    system_prompt = """You are a legal citation expert specializing in Bluebook and jurisdiction-specific citation formats. Your job is to:
1. Format citations according to Bluebook standards (or jurisdiction-specific rules)
2. Include proper pin-cites and parentheticals
3. Use proper short forms and id. references
4. Ensure consistency across all citations
5. Add explanatory parentheticals where helpful"""

    user_prompt = f"""Format the following legal authorities according to proper citation standards for {jurisdiction} jurisdiction:

{authority_list}

For each authority, provide:
1. Full citation (first reference)
2. Short citation (subsequent references)
3. Explanatory parenthetical (if helpful)

Respond in JSON format:
{{
  "citations": [
    {{
      "full_citation": "complete Bluebook citation",
      "short_citation": "id. or short form",
      "parenthetical": "explanatory parenthetical if needed",
      "case_name": "case name",
      "holding": "brief holding summary"
    }}
  ]
}}"""

    response_format = {
        "citations": [
            {
                "full_citation": "string",
                "short_citation": "string",
                "parenthetical": "string",
                "case_name": "string",
                "holding": "string",
            }
        ]
    }

    try:
        result = await llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format=response_format,
            max_tokens=2000,
        )
        result["formatted_count"] = len(result.get("citations", []))
        return result
    except Exception:
        # Fallback to basic formatting
        citations = []
        for auth in authorities:
            citation = auth.get("citation", "Citation not available")
            citations.append({
                "full_citation": citation,
                "short_citation": "Id.",
                "parenthetical": "",
                "case_name": auth.get("case_name", ""),
                "holding": auth.get("holding", ""),
            })
        return {"citations": citations, "formatted_count": len(citations)}


async def _default_document_composer(
    document_type: str,
    sections: dict[str, Any],
    citations: dict[str, Any],
    jurisdiction: str,
    matter: dict[str, Any],
) -> dict[str, Any]:
    """Assemble complete legal document from sections."""

    # Document header
    parties = _normalise_party_roles(matter.get("parties"))
    plaintiff = parties.get("plaintiff", "PLAINTIFF NAME")
    defendant = parties.get("defendant", "DEFENDANT NAME")

    metadata = matter.get("metadata", {})

    case_number = None
    if isinstance(metadata, dict):
        case_number = metadata.get("case_number") or metadata.get("docket_number")
    if not case_number:
        case_number = matter.get("case_number")
    case_number = case_number or "No. XX-XXXX"

    court = None
    if isinstance(metadata, dict):
        court = metadata.get("court") or metadata.get("jurisdiction")
    if not court:
        court = matter.get("court") or matter.get("jurisdiction")
    court = court or "COURT NAME"

    # Build document parts
    parts = []

    # Caption
    caption = sections.get("caption") or f"""
{court}

{plaintiff},
    Plaintiff,
v.                                  {case_number}
{defendant},
    Defendant.
"""
    parts.append(caption.strip())
    parts.append("\n")

    # Document title
    title_map = {
        "complaint": "COMPLAINT",
        "demand_letter": "DEMAND LETTER",
        "motion": "MOTION",
        "memorandum": "MEMORANDUM OF LAW",
    }
    title = title_map.get(document_type, "LEGAL DOCUMENT")
    parts.append(f"\n{title}\n")
    parts.append("=" * len(title))
    parts.append("\n\n")

    # Introduction
    if sections.get("introduction"):
        parts.append(sections["introduction"])
        parts.append("\n\n")

    # Facts section
    if sections.get("facts_section"):
        parts.append("FACTUAL BACKGROUND\n")
        parts.append("-" * 20)
        parts.append("\n\n")
        parts.append(sections["facts_section"])
        parts.append("\n\n")

    # Argument/Analysis section
    if sections.get("argument_section"):
        section_title = "ARGUMENT" if document_type in ["motion", "complaint"] else "LEGAL ANALYSIS"
        parts.append(f"{section_title}\n")
        parts.append("-" * len(section_title))
        parts.append("\n\n")
        parts.append(sections["argument_section"])
        parts.append("\n\n")

    # Conclusion
    if sections.get("conclusion"):
        parts.append("CONCLUSION\n")
        parts.append("-" * 10)
        parts.append("\n\n")
        parts.append(sections["conclusion"])
        parts.append("\n\n")

    # Signature block
    attorney_name = matter.get("attorney_name", "[Attorney Name]")
    attorney_bar = matter.get("attorney_bar_number", "[Bar Number]")
    firm_name = matter.get("firm_name", "[Law Firm]")

    signature_block = f"""
Respectfully submitted,

________________________
{attorney_name}
{firm_name}
Bar No. {attorney_bar}
Attorney for {plaintiff}

Dated: [Date]
"""
    parts.append(signature_block.strip())

    # Assemble complete document
    full_text = "".join(parts)

    # Calculate metrics
    word_count = len(full_text.split())
    page_estimate = word_count // 250  # Rough estimate: 250 words/page

    return {
        "full_text": full_text,
        "word_count": word_count,
        "page_estimate": page_estimate,
        "sections": list(sections.keys()),
        "citation_count": citations.get("formatted_count", 0),
    }


async def _default_document_validator(
    document: dict[str, Any],
    document_type: str,
    matter: dict[str, Any],
) -> dict[str, Any]:
    """Validate document completeness and compliance."""

    full_text = document.get("full_text", "")
    missing_elements = []
    warnings = []

    # Check required elements by document type
    required_elements = {
        "complaint": [
            ("caption", ["plaintiff", "defendant", "v."]),
            ("jurisdiction", ["jurisdiction"]),
            ("facts", ["factual background", "facts"]),
            ("causes_of_action", ["cause of action", "claim", "count"]),
            ("prayer", ["prayer", "wherefore", "relief"]),
        ],
        "demand_letter": [
            ("introduction", ["demand", "settlement"]),
            ("facts", ["facts", "incident"]),
            ("damages", ["damages", "injury", "loss"]),
            ("demand_amount", ["$", "amount", "settlement"]),
        ],
        "motion": [
            ("caption", ["plaintiff", "defendant"]),
            ("introduction", ["motion", "moves"]),
            ("argument", ["argument", "analysis"]),
            ("conclusion", ["conclusion", "wherefore"]),
        ],
        "memorandum": [
            ("facts", ["facts", "factual"]),
            ("analysis", ["analysis", "discussion"]),
            ("conclusion", ["conclusion"]),
        ],
    }

    required = required_elements.get(document_type, [])
    full_text_lower = full_text.lower()

    for element_name, keywords in required:
        if not any(keyword in full_text_lower for keyword in keywords):
            missing_elements.append(element_name)

    # Check document length
    word_count = document.get("word_count", 0)
    if word_count < 100:
        warnings.append("Document appears too short (< 100 words)")
    elif word_count > 10000:
        warnings.append("Document may be too long (> 10,000 words)")

    # Check for placeholder text
    placeholders = ["[", "TODO", "TBD", "XXXX", "N/A"]
    for placeholder in placeholders:
        if placeholder in full_text:
            warnings.append(f"Document contains placeholder text: {placeholder}")

    is_valid = len(missing_elements) == 0 and len(warnings) < 3

    return {
        "is_valid": is_valid,
        "missing_elements": missing_elements,
        "warnings": warnings,
        "completeness_score": max(0, 100 - (len(missing_elements) * 20) - (len(warnings) * 5)),
    }


async def _default_tone_analyzer(
    document: dict[str, Any],
    document_type: str,
) -> dict[str, Any]:
    """Analyze legal writing quality and tone appropriateness."""
    llm = get_llm_client()

    full_text = document.get("full_text", "")

    if not full_text or len(full_text) < 50:
        return {
            "overall_score": 0,
            "issues": ["Document too short to analyze"],
            "strengths": [],
            "recommendations": ["Generate complete document before analysis"],
        }

    # Sample text for analysis (first 2000 chars to stay within token limits)
    sample_text = full_text[:2000]

    system_prompt = """You are a legal writing expert specializing in modern legal prose. Analyze legal documents for:
1. Clarity and conciseness
2. Appropriate tone for document type
3. Plain language usage (avoiding unnecessary legalese)
4. Proper structure and organization
5. Persuasiveness (for advocacy documents) or objectivity (for memos)
6. Grammar and professionalism

Provide constructive feedback focused on modern legal writing best practices."""

    user_prompt = f"""Analyze this {document_type} excerpt for legal writing quality:

{sample_text}

Provide:
1. Overall quality score (0-100)
2. Specific issues or weaknesses
3. Strengths and positive aspects
4. Recommendations for improvement

Respond in JSON format:
{{
  "overall_score": 85,
  "issues": ["issue 1", "issue 2"],
  "strengths": ["strength 1", "strength 2"],
  "recommendations": ["recommendation 1", "recommendation 2"]
}}"""

    response_format = {
        "overall_score": 0,
        "issues": ["string"],
        "strengths": ["string"],
        "recommendations": ["string"],
    }

    try:
        result = await llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format=response_format,
            max_tokens=1000,
        )
        # Ensure score is in valid range
        if "overall_score" in result:
            result["overall_score"] = max(0, min(100, int(result.get("overall_score", 60))))
        return result
    except Exception:
        # Fallback to basic analysis
        word_count = document.get("word_count", 0)
        has_sections = len(document.get("sections", [])) > 3

        score = 60
        if has_sections:
            score += 10
        if word_count > 500:
            score += 10

        return {
            "overall_score": score,
            "issues": ["Unable to perform detailed tone analysis"],
            "strengths": ["Document structure appears reasonable"] if has_sections else [],
            "recommendations": ["Review for clarity and conciseness", "Ensure proper citation format"],
        }
