"""Command-line entry point for the PI demand practice pack."""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import re
from pathlib import Path
from typing import Any, Iterable

try:  # pragma: no cover - optional dependency guard
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - executed when PyYAML missing
    yaml = None  # type: ignore[assignment]

from orchestrator.service import OrchestratorService


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

    matter_payload = data.get("matter") if isinstance(data.get("matter"), dict) else data
    return _normalise_matter(matter_payload, source=path)


def persist_outputs(
    matter: dict[str, Any],
    execution_result: dict[str, Any],
    *,
    output_root: Path = Path("outputs"),
) -> list[Path]:
    """Persist derived artifacts from the orchestrator execution."""

    metadata = matter.get("metadata", {}) if isinstance(matter.get("metadata"), dict) else {}
    slug_source = metadata.get("slug") or matter.get("matter_name") or metadata.get("title")
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
    if isinstance(lsa_output, dict) and lsa_output:
        letter_path = matter_output_dir / "draft_demand_letter.txt"
        letter_content = _compose_draft_letter(matter, execution_result)
        letter_path.write_text(letter_content, encoding="utf-8")
        saved_paths.append(letter_path)

    return saved_paths


def _normalise_matter(raw: dict[str, Any], *, source: Path) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("Matter payload must be an object")

    existing_metadata = raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}
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
    slug = _slugify(str(slug_value)) if isinstance(slug_value, str) and slug_value.strip() else _slugify(matter_name)

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
        summary = entry.get("summary") or entry.get("description") or entry.get("content")
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
                authorities.append({"cite": cite, "summary": "Reference provided as free text."})
            continue
        if not isinstance(entry, dict):
            continue
        cite = entry.get("cite") or entry.get("citation")
        if not cite:
            continue
        authorities.append(
            {
                "cite": str(cite).strip(),
                "summary": str(entry.get("summary") or entry.get("notes") or "").strip(),
            }
        )
    return authorities


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "matter"


def _compose_draft_letter(matter: dict[str, Any], execution_result: dict[str, Any]) -> str:
    metadata = matter.get("metadata", {}) if isinstance(matter.get("metadata"), dict) else {}
    matter_name = metadata.get("title") or matter.get("matter_name") or metadata.get("id") or "Matter"
    matter_id = metadata.get("id") or matter.get("matter_id") or ""
    parties = ", ".join(matter.get("parties", []))
    counterparty = matter.get("counterparty") or "Opposing Counsel"
    summary = matter.get("summary") or matter.get("description") or ""

    artifacts = execution_result.get("artifacts", {}) if isinstance(execution_result, dict) else {}

    lda = artifacts.get("lda") if isinstance(artifacts, dict) else {}
    facts = lda.get("facts", {}) if isinstance(lda, dict) else {}
    key_facts = facts.get("fact_pattern_summary") if isinstance(facts, dict) else []

    dea = artifacts.get("dea") if isinstance(artifacts, dict) else {}
    legal_analysis = dea.get("legal_analysis", {}) if isinstance(dea, dict) else {}
    issues = legal_analysis.get("issues") if isinstance(legal_analysis, dict) else []

    lsa = artifacts.get("lsa") if isinstance(artifacts, dict) else {}
    strategy = lsa.get("strategy", {}) if isinstance(lsa, dict) else {}
    positions = strategy.get("negotiation_positions", {}) if isinstance(strategy, dict) else {}
    actions = strategy.get("recommended_actions", []) if isinstance(strategy, dict) else []
    contingencies = strategy.get("contingencies", []) if isinstance(strategy, dict) else []
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

    lines.append("Please review the enclosed materials and contact us to discuss resolution.")
    lines.append("")
    lines.append("Sincerely,")
    lines.append(parties or "Your Legal Team")

    return "\n".join(lines).strip() + "\n"


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run the PI demand practice pack")
    parser.add_argument("--matter", type=Path, required=True, help="Path to the matter YAML or JSON file")
    args = parser.parse_args()

    if not args.matter.exists():
        parser.error(f"Matter file '{args.matter}' was not found")

    service = OrchestratorService()
    try:
        matter = load_matter(args.matter)
    except (FileNotFoundError, ValueError) as exc:
        parser.error(str(exc))

    result = await service.execute(matter)
    saved_paths = persist_outputs(matter, result)

    print("Execution complete. Artifacts saved to:")
    for path in saved_paths:
        print(f" - {path}")
    if not saved_paths:
        print(" - No artifacts generated")


if __name__ == "__main__":
    asyncio.run(main())
