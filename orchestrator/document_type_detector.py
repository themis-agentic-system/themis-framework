"""Intelligent document type detection for legal matters."""

from __future__ import annotations

from typing import Any

from tools.llm_client import get_llm_client


async def determine_document_type(matter: dict[str, Any]) -> str:
    """Determine appropriate legal document type based on matter context.

    Analyzes:
    - User intent from summary
    - Legal issues and strategy
    - Case stage (pre-litigation vs. litigation)
    - Jurisdictional requirements

    Args:
        matter: Full matter payload with facts, legal_analysis, strategy

    Returns:
        Document type: "complaint", "demand_letter", "motion", "memorandum"
    """
    # 1. Check for explicit user specification
    explicit_type = (
        matter.get("document_type")
        or matter.get("metadata", {}).get("document_type")
    )
    if explicit_type:
        return explicit_type

    # 2. Build context for LLM analysis
    context_parts = []

    # User's description/intent
    summary = matter.get("summary", "")
    if summary:
        context_parts.append(f"Case Description: {summary}")

    # Parties
    parties = matter.get("parties", [])
    if parties:
        context_parts.append(f"Parties: {', '.join(parties)}")

    # Legal issues from DEA
    legal_analysis = matter.get("legal_analysis", {})
    if legal_analysis:
        issues = legal_analysis.get("issues", [])
        if issues:
            issues_list = "\n".join(f"  - {issue.get('issue', 'N/A')}" for issue in issues)
            context_parts.append(f"Legal Issues:\n{issues_list}")

    # Strategy from LSA
    strategy = matter.get("strategy", {})
    if strategy:
        recommended_actions = strategy.get("recommended_actions", [])
        if recommended_actions:
            context_parts.append(f"Recommended Actions: {', '.join(recommended_actions[:3])}")

        negotiation_positions = strategy.get("negotiation_positions", {})
        if negotiation_positions:
            context_parts.append("Strategy Includes Settlement Negotiation: Yes")

    # Draft guidance from LSA
    draft = matter.get("draft", {})
    if draft:
        next_steps = draft.get("next_steps", [])
        if next_steps:
            context_parts.append(f"Next Steps: {', '.join(next_steps[:3])}")

    context = "\n\n".join(context_parts)

    # 3. Use LLM to determine appropriate document type
    llm = get_llm_client()

    system_prompt = """You are a legal process expert who determines what type of legal document is appropriate for a given situation.

Your job is to analyze the case context and determine which document type is needed:

1. **complaint** - Formal civil complaint to be filed with the court
   - Use when: Client needs to initiate litigation, file a lawsuit
   - Keywords: "file complaint", "sue", "lawsuit", "litigation", "file in court"

2. **demand_letter** - Pre-litigation settlement demand letter
   - Use when: Seeking settlement before litigation, making a demand
   - Keywords: "demand", "settlement", "negotiate", "pre-litigation", "resolve without court"

3. **motion** - Motion or brief to be filed with the court
   - Use when: Responding to or initiating motion practice in active litigation
   - Keywords: "motion to dismiss", "summary judgment", "motion for", "brief"

4. **memorandum** - Internal legal memo analyzing issues
   - Use when: No clear litigation or settlement intent, just legal analysis needed
   - Keywords: "analyze", "research", "advise", "opinion", "memo"

Choose the document type that best matches the client's needs and case stage."""

    user_prompt = f"""Based on this case information, determine the appropriate legal document type.

{context}

What type of legal document should be generated?

Respond in JSON format:
{{
  "document_type": "complaint|demand_letter|motion|memorandum",
  "reasoning": "Brief explanation of why this document type is appropriate"
}}"""

    response_format = {
        "document_type": "string",
        "reasoning": "string",
    }

    try:
        result = await llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format=response_format,
            max_tokens=500,
        )

        doc_type = result.get("document_type", "memorandum")
        reasoning = result.get("reasoning", "")

        # Validate document type
        valid_types = ["complaint", "demand_letter", "motion", "memorandum"]
        if doc_type not in valid_types:
            doc_type = "memorandum"

        # Log the decision
        import logging
        logger = logging.getLogger("themis.orchestrator")
        logger.info(
            f"Document type determined: {doc_type}. Reasoning: {reasoning}"
        )

        return doc_type

    except Exception as e:
        # Fallback to heuristic-based detection
        import logging
        logger = logging.getLogger("themis.orchestrator")
        logger.warning(f"LLM document type detection failed: {e}. Using heuristics.")

        return _heuristic_document_type(matter)


def _heuristic_document_type(matter: dict[str, Any]) -> str:
    """Fallback heuristic-based document type detection.

    Args:
        matter: Matter payload

    Returns:
        Document type based on keyword matching
    """
    # Check summary text for keywords
    summary = (matter.get("summary", "") + " " + matter.get("description", "")).lower()

    # Demand letter indicators
    if any(word in summary for word in [
        "demand", "settlement", "negotiate", "settle", "pre-litigation",
        "resolve without", "avoid court"
    ]):
        return "demand_letter"

    # Complaint indicators
    if any(word in summary for word in [
        "file complaint", "sue", "lawsuit", "litigation", "file suit",
        "bring action", "civil action"
    ]):
        return "complaint"

    # Motion indicators
    if any(word in summary for word in [
        "motion", "dismiss", "summary judgment", "brief", "opposition",
        "reply brief"
    ]):
        return "motion"

    # Check strategy for settlement vs litigation intent
    strategy = matter.get("strategy", {})
    if strategy:
        actions = " ".join(strategy.get("recommended_actions", [])).lower()
        if "settlement" in actions or "negotiate" in actions:
            return "demand_letter"
        if "file" in actions or "complaint" in actions:
            return "complaint"

    # Default to memorandum if unclear
    return "memorandum"
