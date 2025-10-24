"""Command-line entry point for the PI demand practice pack."""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

try:  # pragma: no cover - optional dependency guard
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - executed when PyYAML missing
    yaml = None  # type: ignore[assignment]

from orchestrator.service import OrchestratorService
from packs.pi_demand.complaint_generator import generate_complaint
from packs.pi_demand.jurisdictions import get_jurisdiction
from packs.pi_demand.schema import validate_matter_schema, format_validation_errors


def load_matter(path: Path) -> dict[str, Any]:
    """Load and normalise a matter payload from YAML or JSON files."""

    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Matter file '{path}' does not exist")

    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        if yaml is None:
            raise ValueError(
                "PyYAML is required to load YAML matter files. Install the 'pyyaml' dependency."
            )
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    elif suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        raise ValueError("Matter files must be YAML or JSON")

    if data is None:
        raise ValueError("Matter file is empty")
    if not isinstance(data, dict):
        raise ValueError("Matter file must contain an object at the top level")

    # Validate schema
    is_valid, validation_errors = validate_matter_schema(data)
    if validation_errors and any("REQUIRED" in e for e in validation_errors):
        error_message = format_validation_errors(validation_errors)
        raise ValueError(f"Matter file validation failed:\n{error_message}")

    # Print warnings but continue
    if validation_errors and not is_valid:
        print(format_validation_errors(validation_errors))
        print("")

    matter_payload = (
        data.get("matter") if isinstance(data.get("matter"), dict) else data
    )
    return _normalise_matter(matter_payload, source=path)


def persist_outputs(
    matter: dict[str, Any],
    execution_result: dict[str, Any],
    *,
    output_root: Path = Path("outputs"),
) -> list[Path]:
    """Persist derived artifacts from the orchestrator execution."""

    metadata = (
        matter.get("metadata", {}) if isinstance(matter.get("metadata"), dict) else {}
    )
    slug_source = (
        metadata.get("slug") or matter.get("matter_name") or metadata.get("title")
    )
    slug = _slugify(str(slug_source or "matter"))

    matter_output_dir = output_root / slug
    matter_output_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: list[Path] = []
    artifacts = execution_result.get("artifacts", {})

    lda_output = artifacts.get("lda") if isinstance(artifacts, dict) else None
    timeline_entries = None
    if isinstance(lda_output, dict):
        facts = lda_output.get("facts")
        if isinstance(facts, dict):
            timeline_entries = facts.get("timeline")

    # Timeline CSV
    if isinstance(timeline_entries, list) and timeline_entries:
        timeline_path = matter_output_dir / "timeline.csv"
        with timeline_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["date", "description"])
            writer.writeheader()
            for entry in timeline_entries:
                if not isinstance(entry, dict):
                    continue
                writer.writerow(
                    {
                        "date": entry.get("date", ""),
                        "description": entry.get("description", ""),
                    }
                )
        saved_paths.append(timeline_path)

    lsa_output = artifacts.get("lsa") if isinstance(artifacts, dict) else None

    # Demand Letter
    if isinstance(lsa_output, dict) and lsa_output:
        letter_path = matter_output_dir / "draft_demand_letter.txt"
        letter_content = _compose_draft_letter(matter, execution_result)
        letter_path.write_text(letter_content, encoding="utf-8")
        saved_paths.append(letter_path)

    # Complaint
    if isinstance(lsa_output, dict) and lsa_output:
        complaint_path = matter_output_dir / "draft_complaint.txt"
        complaint_content = generate_complaint(matter, execution_result)
        complaint_path.write_text(complaint_content, encoding="utf-8")
        saved_paths.append(complaint_path)

    # Evidence Checklist
    checklist_path = matter_output_dir / "evidence_checklist.txt"
    checklist_content = _generate_evidence_checklist(matter, execution_result)
    checklist_path.write_text(checklist_content, encoding="utf-8")
    saved_paths.append(checklist_path)

    # Medical Expense Summary
    if lda_output:
        medical_summary_path = matter_output_dir / "medical_expense_summary.csv"
        medical_content = _generate_medical_summary(matter, execution_result)
        medical_summary_path.write_text(medical_content, encoding="utf-8")
        saved_paths.append(medical_summary_path)

    # Statute of Limitations Tracker
    statute_path = matter_output_dir / "statute_tracker.txt"
    statute_content = _generate_statute_tracker(matter, execution_result)
    statute_path.write_text(statute_content, encoding="utf-8")
    saved_paths.append(statute_path)

    return saved_paths


def _normalise_matter(raw: dict[str, Any], *, source: Path) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("Matter payload must be an object")

    existing_metadata = (
        raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}
    )
    summary_value = raw.get("summary") or raw.get("description")
    if not isinstance(summary_value, str) or not summary_value.strip():
        raise ValueError("Matter summary or description is required")
    summary = summary_value.strip()
    description_value = raw.get("description") or summary
    description = str(description_value).strip()

    parties = _coerce_str_list(raw.get("parties") or existing_metadata.get("parties"))
    if not parties:
        raise ValueError("Matter must list at least one party")

    documents = _normalise_documents(raw.get("documents"))
    if not documents:
        raise ValueError("Matter must include at least one document entry")

    events = _normalise_events(raw.get("events"))
    issues = _normalise_issues(raw.get("issues"))
    authorities = _normalise_authorities(raw.get("authorities"))

    goals = raw.get("goals") if isinstance(raw.get("goals"), dict) else {}
    strengths = _coerce_str_list(raw.get("strengths"))
    weaknesses = _coerce_str_list(raw.get("weaknesses"))
    concessions = _coerce_str_list(raw.get("concessions"))
    evidentiary_gaps = _coerce_str_list(raw.get("evidentiary_gaps"))

    counterparty_value = (
        raw.get("counterparty") or raw.get("defendant") or raw.get("respondent")
    )
    counterparty = str(counterparty_value).strip() if counterparty_value else ""

    confidence_raw = raw.get("confidence_score", 60)
    try:
        confidence_score = int(confidence_raw)
    except (TypeError, ValueError) as exc:  # pragma: no cover - defensive guardrail
        raise ValueError("confidence_score must be an integer") from exc
    confidence_score = max(0, min(100, confidence_score))

    damages = raw.get("damages") if isinstance(raw.get("damages"), dict) else None

    matter_id_value = (
        existing_metadata.get("id")
        or existing_metadata.get("matter_id")
        or raw.get("matter_id")
        or raw.get("id")
        or source.stem
    )
    matter_id = str(matter_id_value).strip() or source.stem

    title_value = (
        existing_metadata.get("title")
        or existing_metadata.get("name")
        or raw.get("title")
        or raw.get("name")
        or raw.get("case_name")
        or parties[0]
    )
    matter_name = str(title_value).strip() or matter_id

    slug_value = existing_metadata.get("slug")
    slug = (
        _slugify(str(slug_value))
        if isinstance(slug_value, str) and slug_value.strip()
        else _slugify(matter_name)
    )

    metadata: dict[str, Any] = dict(existing_metadata)
    metadata.update(
        {
            "id": matter_id,
            "title": matter_name,
            "slug": slug,
            "source_file": str(source),
        }
    )

    normalised: dict[str, Any] = {
        "matter_id": matter_id,
        "matter_name": matter_name,
        "summary": summary,
        "description": description,
        "parties": parties,
        "documents": documents,
        "events": events,
        "issues": issues,
        "authorities": authorities,
        "goals": goals,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "concessions": concessions,
        "evidentiary_gaps": evidentiary_gaps,
        "confidence_score": confidence_score,
        "metadata": metadata,
    }

    if counterparty:
        normalised["counterparty"] = counterparty
    if damages:
        normalised["damages"] = damages

    return normalised


def _coerce_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [segment.strip() for segment in value.split(",") if segment.strip()]
    if isinstance(value, Iterable):
        result = []
        for item in value:
            if item is None:
                continue
            item_str = str(item).strip()
            if item_str:
                result.append(item_str)
        return result
    return []


def _normalise_documents(value: Any) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    if not isinstance(value, Iterable):
        return documents

    for index, entry in enumerate(value, start=1):
        if isinstance(entry, str):
            documents.append(
                {
                    "title": entry,
                    "summary": entry,
                    "facts": [],
                }
            )
            continue
        if not isinstance(entry, dict):
            continue
        title = entry.get("title") or entry.get("name") or f"document-{index}"
        summary = (
            entry.get("summary") or entry.get("description") or entry.get("content")
        )
        content = entry.get("content")
        facts_value = entry.get("facts") or entry.get("key_facts")
        facts = _coerce_str_list(facts_value)
        document_payload: dict[str, Any] = {
            "title": str(title).strip() or f"document-{index}",
            "summary": str(summary).strip() if summary else "",
            "facts": facts,
        }
        if content:
            document_payload["content"] = str(content)
        if entry.get("date"):
            document_payload["date"] = str(entry.get("date"))
        if entry.get("type"):
            document_payload["type"] = entry.get("type")
        documents.append(document_payload)
    return documents


def _normalise_events(value: Any) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if not isinstance(value, Iterable):
        return events
    for entry in value:
        if not isinstance(entry, dict):
            continue
        description = entry.get("description") or entry.get("summary")
        if not description:
            continue
        event_payload = {
            "description": str(description).strip(),
        }
        if entry.get("date"):
            event_payload["date"] = str(entry.get("date"))
        events.append(event_payload)
    return events


def _normalise_issues(value: Any) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    if not isinstance(value, Iterable):
        return issues
    for entry in value:
        if isinstance(entry, str):
            label = entry.strip()
            if label:
                issues.append({"issue": label, "facts": []})
            continue
        if not isinstance(entry, dict):
            continue
        issue_label = entry.get("issue") or entry.get("label") or entry.get("name")
        if not issue_label:
            continue
        issues.append(
            {
                "issue": str(issue_label).strip(),
                "facts": _coerce_str_list(entry.get("facts")),
            }
        )
    return issues


def _normalise_authorities(value: Any) -> list[dict[str, Any]]:
    authorities: list[dict[str, Any]] = []
    if not isinstance(value, Iterable):
        return authorities
    for entry in value:
        if isinstance(entry, str):
            cite = entry.strip()
            if cite:
                authorities.append(
                    {"cite": cite, "summary": "Reference provided as free text."}
                )
            continue
        if not isinstance(entry, dict):
            continue
        cite = entry.get("cite") or entry.get("citation")
        if not cite:
            continue
        authorities.append(
            {
                "cite": str(cite).strip(),
                "summary": str(
                    entry.get("summary") or entry.get("notes") or ""
                ).strip(),
            }
        )
    return authorities


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "matter"


def _compose_draft_letter(
    matter: dict[str, Any], execution_result: dict[str, Any]
) -> str:
    metadata = (
        matter.get("metadata", {}) if isinstance(matter.get("metadata"), dict) else {}
    )
    matter_name = (
        metadata.get("title")
        or matter.get("matter_name")
        or metadata.get("id")
        or "Matter"
    )
    matter_id = metadata.get("id") or matter.get("matter_id") or ""
    parties = ", ".join(matter.get("parties", []))
    counterparty = matter.get("counterparty") or "Opposing Counsel"
    summary = matter.get("summary") or matter.get("description") or ""

    artifacts = (
        execution_result.get("artifacts", {})
        if isinstance(execution_result, dict)
        else {}
    )

    lda = artifacts.get("lda") if isinstance(artifacts, dict) else {}
    facts = lda.get("facts", {}) if isinstance(lda, dict) else {}
    key_facts = facts.get("fact_pattern_summary") if isinstance(facts, dict) else []

    dea = artifacts.get("dea") if isinstance(artifacts, dict) else {}
    legal_analysis = dea.get("legal_analysis", {}) if isinstance(dea, dict) else {}
    issues = legal_analysis.get("issues") if isinstance(legal_analysis, dict) else []

    lsa = artifacts.get("lsa") if isinstance(artifacts, dict) else {}
    strategy = lsa.get("strategy", {}) if isinstance(lsa, dict) else {}
    positions = (
        strategy.get("negotiation_positions", {}) if isinstance(strategy, dict) else {}
    )
    actions = (
        strategy.get("recommended_actions", []) if isinstance(strategy, dict) else []
    )
    contingencies = (
        strategy.get("contingencies", []) if isinstance(strategy, dict) else []
    )
    risk = strategy.get("risk_assessment", {}) if isinstance(strategy, dict) else {}

    lines: list[str] = []
    lines.append(f"Subject: Settlement Demand – {matter_name}")
    if matter_id:
        lines.append(f"Matter ID: {matter_id}")
    lines.append("")
    lines.append(f"Dear {counterparty},")
    lines.append("")
    if summary:
        lines.append(summary)
        lines.append("")
    if key_facts:
        lines.append("Key Facts:")
        for fact in key_facts:
            lines.append(f"  - {fact}")
        lines.append("")
    if issues:
        lines.append("Legal Theories Raised:")
        for issue in issues:
            if isinstance(issue, dict) and issue.get("issue"):
                lines.append(f"  - {issue['issue']}")
            elif isinstance(issue, str):
                lines.append(f"  - {issue}")
        lines.append("")
    if positions:
        lines.append("Negotiation Positions:")
        for label, value in positions.items():
            lines.append(f"  - {label.title()}: {value}")
        lines.append("")
    if actions:
        lines.append("Next Recommended Actions:")
        for action in actions:
            lines.append(f"  - {action}")
        lines.append("")
    if contingencies:
        lines.append("Contingencies:")
        for item in contingencies:
            lines.append(f"  - {item}")
        lines.append("")
    if risk:
        confidence = risk.get("confidence")
        if confidence is not None:
            lines.append(f"Confidence Assessment: {confidence}%")
        unknowns = risk.get("unknowns")
        if isinstance(unknowns, list) and unknowns:
            lines.append("Open Questions:")
            for unknown in unknowns:
                lines.append(f"  - {unknown}")
        lines.append("")

    lines.append(
        "Please review the enclosed materials and contact us to discuss resolution."
    )
    lines.append("")
    lines.append("Sincerely,")
    lines.append(parties or "Your Legal Team")

    return "\n".join(lines).strip() + "\n"


def _generate_evidence_checklist(
    matter: dict[str, Any], execution_result: dict[str, Any]
) -> str:
    """Generate an evidence checklist for case preparation."""
    lines: list[str] = []
    lines.append("EVIDENCE CHECKLIST")
    lines.append("=" * 80)
    lines.append("")

    metadata = (
        matter.get("metadata", {}) if isinstance(matter.get("metadata"), dict) else {}
    )
    matter_name = metadata.get("title") or matter.get("matter_name") or "Matter"
    lines.append(f"Case: {matter_name}")
    lines.append("")

    # Documents
    lines.append("DOCUMENTS REQUIRED:")
    lines.append("")
    documents = matter.get("documents", [])
    if documents:
        for idx, doc in enumerate(documents, start=1):
            if isinstance(doc, dict):
                title = doc.get("title", f"Document {idx}")
                status = "[ ] "  # Checkbox
                lines.append(f"{status}{idx}. {title}")
    else:
        lines.append("[ ] Medical records")
        lines.append("[ ] Police/incident reports")
        lines.append("[ ] Witness statements")
        lines.append("[ ] Photographs of injuries/scene")
        lines.append("[ ] Employment/wage records")
    lines.append("")

    # Evidentiary gaps from matter
    gaps = matter.get("evidentiary_gaps", [])
    if gaps:
        lines.append("OUTSTANDING EVIDENCE (GAPS TO FILL):")
        lines.append("")
        for gap in gaps:
            lines.append(f"[ ] {gap}")
        lines.append("")

    # Witnesses
    lines.append("WITNESSES TO INTERVIEW:")
    lines.append("")
    parties = matter.get("parties", [])
    for party in parties:
        lines.append(f"[ ] {party}")
    lines.append("[ ] Expert witnesses (medical, accident reconstruction, etc.)")
    lines.append("")

    # Legal authorities
    artifacts = execution_result.get("artifacts", {})
    dea = artifacts.get("dea") if isinstance(artifacts, dict) else {}
    legal_analysis = dea.get("legal_analysis", {}) if isinstance(dea, dict) else {}
    authorities = (
        legal_analysis.get("authorities", [])
        if isinstance(legal_analysis, dict)
        else []
    )

    if authorities:
        lines.append("LEGAL AUTHORITIES TO RESEARCH:")
        lines.append("")
        for auth in authorities[:10]:
            if isinstance(auth, dict) and auth.get("cite"):
                lines.append(f"[ ] {auth['cite']}")
        lines.append("")

    lines.append("TASKS:")
    lines.append("")
    lines.append("[ ] Verify statute of limitations")
    lines.append("[ ] Confirm venue requirements")
    lines.append("[ ] Calculate damages (review with client)")
    lines.append("[ ] Obtain signed retainer agreement")
    lines.append("[ ] Draft and file complaint (if proceeding to litigation)")
    lines.append("[ ] Serve defendant")
    lines.append("")

    return "\n".join(lines)


def _generate_medical_summary(
    matter: dict[str, Any], execution_result: dict[str, Any]
) -> str:
    """Generate a CSV summary of medical expenses."""
    lines: list[str] = []
    lines.append("Date,Provider,Service,Amount,Status")

    artifacts = execution_result.get("artifacts", {})
    lda = artifacts.get("lda") if isinstance(artifacts, dict) else {}
    facts = lda.get("facts", {}) if isinstance(lda, dict) else {}
    damages_calc = (
        facts.get("damages_calculation", {}) if isinstance(facts, dict) else {}
    )
    medical_expenses = (
        damages_calc.get("medical_expenses", [])
        if isinstance(damages_calc, dict)
        else []
    )

    if medical_expenses:
        for expense in medical_expenses:
            if isinstance(expense, dict):
                date = expense.get("date", "")
                provider = expense.get("provider", "Unknown Provider")
                service = expense.get("service", "Medical Service")
                amount = expense.get("amount", 0)
                status = expense.get("status", "Pending")
                lines.append(f"{date},{provider},{service},{amount},{status}")
    else:
        # Extract from documents if available
        documents = matter.get("documents", [])
        for doc in documents:
            if isinstance(doc, dict):
                title = doc.get("title", "")
                if "medical" in title.lower() or "treatment" in title.lower():
                    date = doc.get("date", "")
                    provider = "Medical Provider"
                    service = title
                    amount = ""
                    status = "To be documented"
                    lines.append(f"{date},{provider},{service},{amount},{status}")

    # If no medical records at all, add template rows
    if len(lines) == 1:
        lines.append(",,Medical treatment (to be documented),,")
        lines.append(",,Future medical care estimate,,")

    # Add totals if damages available
    damages = (
        matter.get("damages", {}) if isinstance(matter.get("damages"), dict) else {}
    )
    specials = damages.get("specials", 0)
    if specials:
        lines.append("")
        lines.append(f",,,Total Medical Expenses:,${specials:,}")

    return "\n".join(lines)


def _generate_statute_tracker(
    matter: dict[str, Any], execution_result: dict[str, Any]
) -> str:
    """Generate statute of limitations tracker."""
    lines: list[str] = []
    lines.append("STATUTE OF LIMITATIONS TRACKER")
    lines.append("=" * 80)
    lines.append("")

    metadata = (
        matter.get("metadata", {}) if isinstance(matter.get("metadata"), dict) else {}
    )
    matter_name = metadata.get("title") or matter.get("matter_name") or "Matter"
    lines.append(f"Case: {matter_name}")
    lines.append("")

    # Get jurisdiction
    jurisdiction_name = metadata.get("jurisdiction") or "California"
    jurisdiction = get_jurisdiction(jurisdiction_name)

    lines.append(f"Jurisdiction: {jurisdiction_name}")
    lines.append("")

    # Get incident date from timeline or events
    incident_date = None
    events = matter.get("events", [])
    if events and isinstance(events[0], dict):
        incident_date = events[0].get("date")

    if not incident_date:
        artifacts = execution_result.get("artifacts", {})
        lda = artifacts.get("lda") if isinstance(artifacts, dict) else {}
        facts = lda.get("facts", {}) if isinstance(lda, dict) else {}
        timeline = facts.get("timeline", []) if isinstance(facts, dict) else []
        if timeline and isinstance(timeline[0], dict):
            incident_date = timeline[0].get("date")

    if incident_date:
        lines.append(f"Incident Date: {incident_date}")
        lines.append("")

    # Show applicable statutes of limitation
    if jurisdiction and jurisdiction.get("statutes_of_limitation"):
        lines.append("APPLICABLE STATUTES OF LIMITATION:")
        lines.append("")
        sol_dict = jurisdiction["statutes_of_limitation"]
        for cause_type, sol_info in sol_dict.items():
            if isinstance(sol_info, dict):
                period = sol_info.get("period", "Unknown")
                statute = sol_info.get("statute", "")
                lines.append(f"{cause_type.replace('_', ' ').title()}:")
                lines.append(f"  Period: {period}")
                lines.append(f"  Statute: {statute}")
                if incident_date:
                    lines.append(
                        f"  Deadline: {incident_date} + {period} = [Calculate deadline]"
                    )
                lines.append("")

    lines.append("IMPORTANT DEADLINES:")
    lines.append("")
    lines.append("[ ] Complaint filing deadline (statute of limitations)")
    lines.append("[ ] Discovery cutoff")
    lines.append("[ ] Expert designation deadline")
    lines.append("[ ] Motion filing deadlines")
    lines.append("[ ] Trial date")
    lines.append("")

    lines.append("WARNING:")
    lines.append("This is a general reference only. Consult with supervising attorney")
    lines.append("to confirm all applicable deadlines and statutes of limitation.")
    lines.append("Tolling provisions may apply based on specific facts.")
    lines.append("")

    return "\n".join(lines)


def _list_fixtures() -> None:
    """List available fixture files in the pi_demand pack."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    if not fixtures_dir.exists():
        print("No fixtures directory found.")
        return

    fixtures = sorted(fixtures_dir.glob("*.json"))
    if not fixtures:
        print("No fixture files found.")
        return

    print("Available fixtures:")
    print("")
    for fixture in fixtures:
        # Try to load and extract basic info
        try:
            data = json.loads(fixture.read_text(encoding="utf-8"))
            matter = data.get("matter", {})
            metadata = matter.get("metadata", {})
            title = metadata.get("title", "Untitled")
            jurisdiction = metadata.get("jurisdiction", "N/A")
            cause = metadata.get("cause_of_action", "N/A")
            print(f"  {fixture.name}")
            print(f"    Title: {title}")
            print(f"    Jurisdiction: {jurisdiction}")
            print(f"    Cause of Action: {cause}")
            print("")
        except Exception:
            print(f"  {fixture.name} (unable to read details)")
            print("")


def _create_matter_interactive(output_path: Path) -> None:
    """Interactively create a new matter file."""
    print("=== Create New Personal Injury Matter ===")
    print("")
    print("This wizard will help you create a matter file.")
    print("Press Enter to skip optional fields.")
    print("")

    # Metadata
    print("--- Metadata ---")
    matter_id = (
        input("Matter ID (e.g., PI-2024-001): ").strip()
        or f"PI-{datetime.now().year}-TEMP"
    )
    title = input("Matter Title (e.g., Doe v. Smith): ").strip() or "Untitled Matter"

    print("\nAvailable jurisdictions: California, New York, Texas, Florida, Illinois")
    jurisdiction = input("Jurisdiction: ").strip() or "California"

    print(
        "\nAvailable causes of action: negligence, motor_vehicle, premises_liability,"
    )
    print("  medical_malpractice, product_liability, dog_bite")
    cause_of_action = input("Cause of Action: ").strip() or "negligence"

    # Summary
    print("\n--- Case Information ---")
    summary = input("Brief summary of the matter (required): ").strip()
    while not summary or len(summary) < 10:
        print("Summary must be at least 10 characters.")
        summary = input("Brief summary: ").strip()

    # Parties
    print("\n--- Parties ---")
    parties = []
    party_num = 1
    while True:
        party = input(f"Party #{party_num} (press Enter when done): ").strip()
        if not party:
            break
        parties.append(party)
        party_num += 1

    if not parties:
        parties = ["Plaintiff (Name TBD)", "Defendant (Name TBD)"]
        print("Using default parties:", parties)

    counterparty = input("\nOpposing counsel name: ").strip()

    # Documents
    print("\n--- Documents ---")
    print("Add at least one document.")
    documents = []
    doc_num = 1
    while True:
        print(f"\nDocument #{doc_num}:")
        doc_title = input("  Document title (press Enter to finish): ").strip()
        if not doc_title:
            break
        doc_date = input("  Date (YYYY-MM-DD, optional): ").strip()
        doc_summary = input("  Summary: ").strip()

        doc = {"title": doc_title}
        if doc_date:
            doc["date"] = doc_date
        if doc_summary:
            doc["summary"] = doc_summary

        documents.append(doc)
        doc_num += 1

    if not documents:
        documents = [{"title": "Document placeholder - update with actual documents"}]

    # Damages
    print("\n--- Damages (optional) ---")
    specials_input = input("Economic damages (specials): $").strip()
    generals_input = input("Non-economic damages (generals): $").strip()

    damages = {}
    if specials_input:
        try:
            damages["specials"] = float(specials_input.replace(",", ""))
        except ValueError:
            pass
    if generals_input:
        try:
            damages["generals"] = float(generals_input.replace(",", ""))
        except ValueError:
            pass

    # Build matter
    matter_data = {
        "matter": {
            "metadata": {
                "id": matter_id,
                "title": title,
                "jurisdiction": jurisdiction,
                "cause_of_action": cause_of_action,
            },
            "summary": summary,
            "parties": parties,
            "documents": documents,
            "events": [],
            "issues": [],
            "authorities": [],
            "goals": {},
            "strengths": [],
            "weaknesses": [],
            "concessions": [],
            "evidentiary_gaps": [],
        }
    }

    if counterparty:
        matter_data["matter"]["counterparty"] = counterparty
    if damages:
        matter_data["matter"]["damages"] = damages

    # Save
    output_path.write_text(json.dumps(matter_data, indent=2), encoding="utf-8")
    print(f"\n✓ Matter file created: {output_path}")
    print("\nYou can now edit this file to add more details, then run:")
    print(f"  python -m packs.pi_demand.run --matter {output_path}")


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the PI demand practice pack",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with existing matter file
  python -m packs.pi_demand.run --matter path/to/matter.json

  # Validate matter file without executing
  python -m packs.pi_demand.run --matter path/to/matter.json --validate-only

  # List available fixtures
  python -m packs.pi_demand.run --list-fixtures

  # Create a new matter file interactively
  python -m packs.pi_demand.run --create-matter --output new_matter.json
        """,
    )
    parser.add_argument(
        "--matter", type=Path, help="Path to the matter YAML or JSON file"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate the matter file without executing",
    )
    parser.add_argument(
        "--list-fixtures", action="store_true", help="List available fixture files"
    )
    parser.add_argument(
        "--create-matter",
        action="store_true",
        help="Interactively create a new matter file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for created matter file (use with --create-matter)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Output directory for artifacts (default: outputs/)",
    )

    args = parser.parse_args()

    # List fixtures
    if args.list_fixtures:
        _list_fixtures()
        return

    # Create matter interactively
    if args.create_matter:
        output_path = args.output or Path("new_matter.json")
        _create_matter_interactive(output_path)
        return

    # Require --matter for other operations
    if not args.matter:
        parser.error("--matter is required (or use --list-fixtures or --create-matter)")

    if not args.matter.exists():
        parser.error(f"Matter file '{args.matter}' was not found")

    # Validate only
    if args.validate_only:
        try:
            matter = load_matter(args.matter)
            print(f"✓ Matter file '{args.matter}' is valid!")
            print(
                f"  Jurisdiction: {matter.get('metadata', {}).get('jurisdiction', 'Not specified')}"
            )
            print(f"  Parties: {len(matter.get('parties', []))}")
            print(f"  Documents: {len(matter.get('documents', []))}")
        except (FileNotFoundError, ValueError) as exc:
            print(f"✗ Validation failed: {exc}")
            return
        return

    # Execute normally
    service = OrchestratorService()
    try:
        matter = load_matter(args.matter)
    except (FileNotFoundError, ValueError) as exc:
        parser.error(str(exc))

    print(
        f"Executing workflow for: {matter.get('metadata', {}).get('title', 'Untitled Matter')}"
    )
    print("")

    result = await service.execute(matter)
    saved_paths = persist_outputs(matter, result, output_root=args.output_dir)

    print("Execution complete. Artifacts saved to:")
    for path in saved_paths:
        print(f" - {path}")
    if not saved_paths:
        print(" - No artifacts generated")


if __name__ == "__main__":
    asyncio.run(main())
