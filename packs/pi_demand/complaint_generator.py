"""Generate jurisdiction-specific civil complaints for personal injury matters."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from packs.pi_demand.jurisdictions import (
    get_cause_of_action,
    get_jurisdiction,
    infer_cause_of_action,
)


def generate_complaint(matter: dict[str, Any], execution_result: dict[str, Any]) -> str:
    """Generate a formal civil complaint based on matter details and agent analysis."""

    # Extract jurisdiction
    metadata = matter.get("metadata", {}) if isinstance(matter.get("metadata"), dict) else {}
    jurisdiction_name = metadata.get("jurisdiction") or "California"  # Default to California
    jurisdiction = get_jurisdiction(jurisdiction_name)

    if not jurisdiction:
        return f"ERROR: Jurisdiction '{jurisdiction_name}' is not supported.\n"

    # Infer cause of action type
    cause_type = metadata.get("cause_of_action") or infer_cause_of_action(matter, jurisdiction_name)
    cause_of_action = get_cause_of_action(jurisdiction_name, cause_type)

    if not cause_of_action:
        # Fall back to general negligence
        cause_of_action = get_cause_of_action(jurisdiction_name, "negligence")

    # Extract matter details
    matter_name = metadata.get("title") or matter.get("matter_name") or "Untitled Matter"
    matter_id = metadata.get("id") or matter.get("matter_id") or "UNKNOWN"
    parties = matter.get("parties", [])
    plaintiff = parties[0] if parties else "Jane Doe"
    defendant = matter.get("counterparty") or (parties[1] if len(parties) > 1 else "Unknown Defendant")
    summary = matter.get("summary") or matter.get("description") or ""

    # Extract artifacts from agent execution
    artifacts = execution_result.get("artifacts", {}) if isinstance(execution_result, dict) else {}

    # LDA facts
    lda = artifacts.get("lda") if isinstance(artifacts, dict) else {}
    facts = lda.get("facts", {}) if isinstance(lda, dict) else {}
    fact_pattern = facts.get("fact_pattern_summary", []) if isinstance(facts, dict) else []
    timeline = facts.get("timeline", []) if isinstance(facts, dict) else []
    damages_calc = facts.get("damages_calculation", {}) if isinstance(facts, dict) else {}

    # DEA legal analysis
    dea = artifacts.get("dea") if isinstance(artifacts, dict) else {}
    legal_analysis = dea.get("legal_analysis", {}) if isinstance(dea, dict) else {}
    issues = legal_analysis.get("issues", []) if isinstance(legal_analysis, dict) else []
    authorities = legal_analysis.get("authorities", []) if isinstance(legal_analysis, dict) else []

    # LSA strategy
    lsa = artifacts.get("lsa") if isinstance(artifacts, dict) else {}
    strategy = lsa.get("strategy", {}) if isinstance(lsa, dict) else {}

    # Damages from matter
    damages = matter.get("damages", {}) if isinstance(matter.get("damages"), dict) else {}
    specials = damages.get("specials", 0)
    generals = damages.get("generals", 0)
    punitives = damages.get("punitive")

    # Build the complaint
    lines: list[str] = []

    # Header
    lines.append(_format_header(jurisdiction, matter_name, plaintiff, defendant))

    # Caption
    lines.append(_format_caption(jurisdiction, plaintiff, defendant, matter_id))

    # Introduction
    lines.append("COMPLAINT FOR DAMAGES")
    lines.append("")
    lines.append(f"Plaintiff {plaintiff} alleges:")
    lines.append("")

    # Parties
    lines.append("PARTIES")
    lines.append("")
    lines.append(f"1. Plaintiff {plaintiff} is an individual residing in {jurisdiction_name}.")
    lines.append("")
    lines.append(f"2. Defendant {defendant} is a person or entity that, at all relevant times, " +
                 f"conducted business in {jurisdiction_name}.")
    lines.append("")

    # Jurisdiction and Venue
    lines.append("JURISDICTION AND VENUE")
    lines.append("")
    lines.append("3. This Court has jurisdiction over this action pursuant to applicable state law.")
    lines.append("")
    lines.append("4. Venue is proper in this judicial district.")
    lines.append("")

    # General Allegations / Facts
    lines.append("GENERAL ALLEGATIONS")
    lines.append("")
    paragraph_num = 5

    # Add summary as first factual paragraph
    if summary:
        lines.append(f"{paragraph_num}. {summary}")
        lines.append("")
        paragraph_num += 1

    # Add timeline events
    if timeline:
        for event in timeline[:10]:  # Limit to first 10 events
            if isinstance(event, dict):
                date = event.get("date", "")
                description = event.get("description", "")
                if description:
                    date_text = f"On or about {date}, " if date else ""
                    lines.append(f"{paragraph_num}. {date_text}{description}")
                    lines.append("")
                    paragraph_num += 1

    # Add key facts
    if fact_pattern:
        for fact in fact_pattern[:10]:  # Limit to top 10 facts
            if fact:
                lines.append(f"{paragraph_num}. {fact}")
                lines.append("")
                paragraph_num += 1

    # Causes of Action
    lines.append("FIRST CAUSE OF ACTION")
    lines.append(f"({cause_of_action['name']})")
    lines.append("")

    # Add elements as allegations
    elements = cause_of_action.get("elements", [])
    for element in elements:
        lines.append(f"{paragraph_num}. {element}")
        lines.append("")
        paragraph_num += 1

    # Reference statute
    lines.append(f"{paragraph_num}. As a direct and proximate result of Defendant's conduct, " +
                 "Plaintiff has suffered and continues to suffer injuries and damages as set forth below.")
    lines.append("")
    paragraph_num += 1

    # Add additional causes of action if multiple issues identified
    if len(issues) > 1 and issues[1].get("issue"):
        cause_number = 2
        for issue in issues[1:4]:  # Add up to 3 additional causes
            if isinstance(issue, dict) and issue.get("issue"):
                lines.append(f"{_ordinal(cause_number).upper()} CAUSE OF ACTION")
                lines.append(f"({issue['issue']})")
                lines.append("")
                lines.append(f"{paragraph_num}. Plaintiff incorporates by reference all preceding allegations.")
                lines.append("")
                paragraph_num += 1

                # Add issue-specific facts if available
                issue_facts = issue.get("facts", [])
                for fact in issue_facts[:3]:  # Limit to 3 facts per issue
                    if fact:
                        lines.append(f"{paragraph_num}. {fact}")
                        lines.append("")
                        paragraph_num += 1

                lines.append(f"{paragraph_num}. As a direct result of the conduct alleged above, " +
                             "Plaintiff has been damaged.")
                lines.append("")
                paragraph_num += 1
                cause_number += 1

    # Damages
    lines.append("DAMAGES")
    lines.append("")
    lines.append(f"{paragraph_num}. As a direct and proximate result of Defendant's conduct, " +
                 "Plaintiff has suffered the following damages:")
    lines.append("")

    # Economic damages
    if jurisdiction and jurisdiction.get("damages"):
        econ_damages = jurisdiction["damages"].get("economic", [])
        if econ_damages:
            lines.append("Economic Damages:")
            for damage_type in econ_damages:
                lines.append(f"  • {damage_type}")
            lines.append("")

        # Non-economic damages
        non_econ_damages = jurisdiction["damages"].get("non_economic", [])
        if non_econ_damages:
            lines.append("Non-Economic Damages:")
            for damage_type in non_econ_damages:
                lines.append(f"  • {damage_type}")
            lines.append("")

    # Damage amounts if available
    if specials or generals:
        lines.append(f"{paragraph_num + 1}. Plaintiff's economic damages exceed ${specials:,}.")
        lines.append("")
        if generals:
            lines.append(f"{paragraph_num + 2}. Plaintiff's non-economic damages exceed ${generals:,}.")
            lines.append("")

    # Punitive damages if applicable
    if punitives:
        punitive_standard = jurisdiction.get("damages", {}).get("punitive_standard", "")
        lines.append(f"{paragraph_num + 3}. Plaintiff is entitled to punitive damages because " +
                     f"Defendant's conduct meets the standard for such damages: {punitive_standard}")
        lines.append("")

    # Prayer for Relief
    lines.append("PRAYER FOR RELIEF")
    lines.append("")
    lines.append("WHEREFORE, Plaintiff respectfully requests that this Court enter judgment in Plaintiff's favor and against Defendant, and award:")
    lines.append("")
    lines.append("1. Economic damages according to proof;")
    lines.append("")
    lines.append("2. Non-economic damages according to proof;")
    lines.append("")
    if punitives:
        lines.append("3. Punitive damages;")
        lines.append("")
        lines.append("4. Costs of suit;")
        lines.append("")
        lines.append("5. Attorney's fees as allowed by law;")
        lines.append("")
        lines.append("6. Such other and further relief as the Court deems just and proper.")
    else:
        lines.append("3. Costs of suit;")
        lines.append("")
        lines.append("4. Attorney's fees as allowed by law;")
        lines.append("")
        lines.append("5. Such other and further relief as the Court deems just and proper.")
    lines.append("")
    lines.append("")

    # Signature block
    lines.append(f"Dated: {datetime.now().strftime('%B %d, %Y')}")
    lines.append("")
    lines.append("Respectfully submitted,")
    lines.append("")
    lines.append("_________________________")
    lines.append("Attorney for Plaintiff")
    lines.append(f"{plaintiff}")
    lines.append("")

    # Verification or special requirements note
    if cause_of_action.get("special_requirements"):
        lines.append("---")
        lines.append(f"NOTE: {cause_of_action['special_requirements']}")
        lines.append("")

    return "\n".join(lines)


def _format_header(jurisdiction: dict[str, Any], matter_name: str, plaintiff: str, defendant: str) -> str:
    """Format the complaint header based on jurisdiction."""
    lines = []
    lines.append("=" * 80)
    lines.append(f"SUPERIOR COURT OF {jurisdiction.get('code', 'STATE')}")
    lines.append(f"COUNTY OF [COUNTY NAME]")
    lines.append("")
    lines.append(f"{plaintiff},")
    lines.append("     Plaintiff,")
    lines.append("")
    lines.append("vs.")
    lines.append("")
    lines.append(f"{defendant},")
    lines.append("     Defendant.")
    lines.append("=" * 80)
    lines.append("")
    return "\n".join(lines)


def _format_caption(jurisdiction: dict[str, Any], plaintiff: str, defendant: str, case_id: str) -> str:
    """Format the case caption."""
    lines = []
    lines.append(f"Case No. {case_id}")
    lines.append("")
    return "\n".join(lines)


def _ordinal(n: int) -> str:
    """Convert number to ordinal string (e.g., 1 -> 'First', 2 -> 'Second')."""
    ordinals = {
        1: "First",
        2: "Second",
        3: "Third",
        4: "Fourth",
        5: "Fifth",
        6: "Sixth",
        7: "Seventh",
        8: "Eighth",
        9: "Ninth",
        10: "Tenth",
    }
    return ordinals.get(n, f"{n}th")
