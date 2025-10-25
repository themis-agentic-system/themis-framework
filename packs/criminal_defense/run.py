"""Command-line entry point for the State Criminal Defense practice pack."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

try:  # pragma: no cover - optional dependency guard
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - executed when PyYAML missing
    yaml = None  # type: ignore[assignment]

from orchestrator.service import OrchestratorService
from packs.criminal_defense.schema import validate_matter_schema, format_validation_errors


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
    slug_source = metadata.get("slug") or matter.get("matter_name") or metadata.get("case_number")
    slug = _slugify(str(slug_source or "matter"))

    matter_output_dir = output_root / slug
    matter_output_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: list[Path] = []
    artifacts = execution_result.get("artifacts", {})

    # Criminal Case Analyst (CCA) output
    cca_output = artifacts.get("cca") if isinstance(artifacts, dict) else None

    # Discovery & Motion Specialist (DMS) output
    dms_output = artifacts.get("dms") if isinstance(artifacts, dict) else None

    # Legal Strategist & Writer (LSW) output
    lsw_output = artifacts.get("lsw") if isinstance(artifacts, dict) else None

    # 1. Case Timeline with Constitutional Issues
    timeline_path = matter_output_dir / "case_timeline.csv"
    timeline_content = _generate_timeline(matter, execution_result)
    timeline_path.write_text(timeline_content, encoding="utf-8")
    saved_paths.append(timeline_path)

    # 2. Constitutional Issues Analysis
    if cca_output:
        analysis_path = matter_output_dir / "constitutional_issues_analysis.txt"
        analysis_content = _generate_constitutional_analysis(matter, execution_result)
        analysis_path.write_text(analysis_content, encoding="utf-8")
        saved_paths.append(analysis_path)

    # 3. Discovery Demand Letter
    if dms_output:
        discovery_path = matter_output_dir / "discovery_demand.txt"
        discovery_content = _generate_discovery_demand(matter, execution_result)
        discovery_path.write_text(discovery_content, encoding="utf-8")
        saved_paths.append(discovery_path)

    # 4. Brady/Giglio Checklist
    brady_path = matter_output_dir / "brady_giglio_checklist.txt"
    brady_content = _generate_brady_checklist(matter, execution_result)
    brady_path.write_text(brady_content, encoding="utf-8")
    saved_paths.append(brady_path)

    # 5. Suppression Motion (only if constitutional issues warrant it)
    if lsw_output and _should_generate_suppression_motion(matter, execution_result):
        motion_path = matter_output_dir / "motion_to_suppress.txt"
        motion_content = _generate_suppression_motion(matter, execution_result)
        motion_path.write_text(motion_content, encoding="utf-8")
        saved_paths.append(motion_path)

    # 6. Evidence Preservation Letter
    preservation_path = matter_output_dir / "evidence_preservation_letter.txt"
    preservation_content = _generate_preservation_letter(matter, execution_result)
    preservation_path.write_text(preservation_content, encoding="utf-8")
    saved_paths.append(preservation_path)

    # 7. Witness Interview Checklist
    witness_path = matter_output_dir / "witness_interview_checklist.txt"
    witness_content = _generate_witness_checklist(matter, execution_result)
    witness_path.write_text(witness_content, encoding="utf-8")
    saved_paths.append(witness_path)

    # 8. Motion Recommendations
    recommendations_path = matter_output_dir / "pretrial_motion_recommendations.txt"
    recommendations_content = _generate_motion_recommendations(matter, execution_result)
    recommendations_path.write_text(recommendations_content, encoding="utf-8")
    saved_paths.append(recommendations_path)

    return saved_paths


def _normalise_matter(raw: dict[str, Any], *, source: Path) -> dict[str, Any]:
    """Normalize criminal defense matter data."""
    if not isinstance(raw, dict):
        raise ValueError("Matter payload must be an object")

    existing_metadata = raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}

    # Client information (required)
    client = raw.get("client")
    if not isinstance(client, dict):
        raise ValueError("Matter must include client information")

    # Charges (required)
    charges = raw.get("charges")
    if not isinstance(charges, list) or len(charges) == 0:
        raise ValueError("Matter must include at least one charge")

    # Arrest information (required)
    arrest = raw.get("arrest")
    if not isinstance(arrest, dict):
        raise ValueError("Matter must include arrest information")

    # Generate matter ID and name
    case_number = existing_metadata.get("case_number") or raw.get("case_number") or source.stem
    client_name = client.get("name", "Unknown Client")
    matter_id = str(case_number).strip() or source.stem
    matter_name = f"{existing_metadata.get('jurisdiction', 'State')} v. {client_name}"

    slug_value = existing_metadata.get("slug")
    slug = _slugify(str(slug_value)) if isinstance(slug_value, str) and slug_value.strip() else _slugify(matter_id)

    metadata: dict[str, Any] = dict(existing_metadata)
    metadata.update({
        "id": matter_id,
        "case_number": case_number,
        "title": matter_name,
        "slug": slug,
        "source_file": str(source),
    })

    normalised: dict[str, Any] = {
        "matter_id": matter_id,
        "matter_name": matter_name,
        "metadata": metadata,
        "client": client,
        "charges": charges,
        "arrest": arrest,
    }

    # Optional fields
    optional_fields = [
        "search_and_seizure", "interrogation", "identification",
        "discovery_received", "discovery_outstanding", "constitutional_issues",
        "defense_theory", "goals", "client_narrative"
    ]

    for field in optional_fields:
        if field in raw:
            normalised[field] = raw[field]

    return normalised


def _should_generate_suppression_motion(matter: dict[str, Any], result: dict[str, Any]) -> bool:
    """Determine if a suppression motion should be generated based on constitutional issues."""
    # Check if CCA identified suppression-worthy issues
    artifacts = result.get("artifacts", {})
    cca_output = artifacts.get("cca") if isinstance(artifacts, dict) else None

    if not cca_output:
        return False

    # Check for high-severity constitutional issues
    issues = matter.get("constitutional_issues", [])
    if not isinstance(issues, list):
        return False

    # Generate motion if there are Fourth, Fifth, or Sixth Amendment issues
    constitutional_issue_types = {issue.get("issue_type") for issue in issues if isinstance(issue, dict)}
    return bool(constitutional_issue_types & {"fourth_amendment", "fifth_amendment", "sixth_amendment"})


def _generate_timeline(matter: dict[str, Any], result: dict[str, Any]) -> str:
    """Generate chronological case timeline CSV."""
    lines = ["date,event,constitutional_flag\n"]

    # Add arrest date
    arrest = matter.get("arrest", {})
    if arrest.get("date"):
        lines.append(f"{arrest['date']},Arrest: {arrest.get('circumstances', 'Arrested')},\n")

    # Add discovery dates
    for doc in matter.get("discovery_received", []):
        if isinstance(doc, dict) and doc.get("date_received"):
            lines.append(f"{doc['date_received']},Discovery received: {doc.get('document_type', 'Document')},\n")

    # Add interrogation if present
    interrogation = matter.get("interrogation", {})
    if interrogation.get("was_interrogated"):
        flag = "⚠ Miranda issue" if not interrogation.get("miranda_given") else ""
        lines.append(f"{arrest.get('date', '')},Interrogation conducted,{flag}\n")

    return "".join(lines)


def _generate_constitutional_analysis(matter: dict[str, Any], result: dict[str, Any]) -> str:
    """Generate constitutional issues analysis from CCA agent output."""
    artifacts = result.get("artifacts", {})
    cca_output = artifacts.get("cca", {}) if isinstance(artifacts, dict) else {}

    lines = [
        "CONSTITUTIONAL ISSUE ANALYSIS",
        f"Case: {matter.get('matter_name', 'Unknown')}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "=" * 80,
        ""
    ]

    # Get analysis from CCA agent
    if isinstance(cca_output, dict) and "constitutional_analysis" in cca_output:
        lines.append(str(cca_output["constitutional_analysis"]))
    else:
        # Fallback: analyze constitutional issues from matter file
        issues = matter.get("constitutional_issues", [])
        if issues:
            lines.append("IDENTIFIED CONSTITUTIONAL ISSUES:")
            lines.append("")
            for idx, issue in enumerate(issues, 1):
                if isinstance(issue, dict):
                    lines.append(f"{idx}. {issue.get('issue_type', 'Unknown').upper().replace('_', ' ')}")
                    lines.append(f"   {issue.get('description', 'No description provided')}")
                    lines.append("")
        else:
            lines.append("No constitutional issues identified in matter file.")
            lines.append("Review case facts for potential Fourth, Fifth, or Sixth Amendment violations.")

    lines.append("")
    lines.append("=" * 80)
    lines.append("**ATTORNEY REVIEW REQUIRED** - Verify all analysis before filing motions")

    return "\n".join(lines)


def _generate_discovery_demand(matter: dict[str, Any], result: dict[str, Any]) -> str:
    """Generate discovery demand letter from DMS agent output."""
    artifacts = result.get("artifacts", {})
    dms_output = artifacts.get("dms", {}) if isinstance(artifacts, dict) else {}

    metadata = matter.get("metadata", {})
    jurisdiction = metadata.get("jurisdiction", "State")

    lines = [
        "[ATTORNEY LETTERHEAD]",
        "",
        datetime.now().strftime("%B %d, %Y"),
        "",
        "District Attorney's Office",
        f"{jurisdiction}",
        "",
        f"Re: {matter.get('matter_name', 'Unknown Case')}",
        f"    Case No. {metadata.get('case_number', 'Unknown')}",
        "",
        "Dear Prosecutor:",
        "",
        f"Pursuant to applicable discovery rules in {jurisdiction} and Brady v. Maryland, "
        f"defendant {matter.get('client', {}).get('name', 'Unknown')} requests immediate disclosure "
        "of the following discovery materials:",
        "",
    ]

    # Get discovery demand from DMS agent
    if isinstance(dms_output, dict) and "discovery_demand" in dms_output:
        lines.append(str(dms_output["discovery_demand"]))
    else:
        # Fallback: generate basic discovery demand
        lines.extend([
            "I. MANDATORY DISCLOSURE",
            "",
            "1. All police reports and investigative materials",
            "2. All witness statements (recorded and written)",
            "3. All physical evidence seized or obtained",
            "4. All scientific reports and lab results",
            "5. All photographs and video/audio recordings",
            "",
            "II. EXCULPATORY EVIDENCE (Brady/Giglio)",
            "",
            "1. Any evidence favorable to the defendant",
            "2. Any impeachment evidence regarding prosecution witnesses",
            "3. Any evidence of other suspects",
            "4. Any prior inconsistent statements by witnesses",
            "",
        ])

        # Charge-specific requests
        charges = matter.get("charges", [])
        if charges and isinstance(charges[0], dict):
            first_charge = charges[0].get("description", "").lower()

            if "dui" in first_charge or "dwi" in first_charge:
                lines.extend([
                    "III. DUI-SPECIFIC DISCOVERY",
                    "",
                    "1. Breathalyzer/blood test calibration records",
                    "2. Officer training and certification records",
                    "3. Dash cam and body cam footage",
                    "4. Field sobriety test videos",
                    "",
                ])
            elif "drug" in first_charge or "controlled substance" in first_charge:
                lines.extend([
                    "III. DRUG CASE DISCOVERY",
                    "",
                    "1. Laboratory analysis and chain of custody",
                    "2. Confidential informant identity/reliability records",
                    "3. Search warrant and supporting affidavit",
                    "4. Any surveillance recordings",
                    "",
                ])

    lines.extend([
        "",
        "Please provide this discovery within the time required by law.",
        "",
        "Respectfully submitted,",
        "",
        "[DEFENSE ATTORNEY NAME]",
        "Attorney for Defendant",
    ])

    return "\n".join(lines)


def _generate_brady_checklist(matter: dict[str, Any], result: dict[str, Any]) -> str:
    """Generate Brady/Giglio exculpatory evidence checklist."""
    lines = [
        "BRADY/GIGLIO EXCULPATORY EVIDENCE CHECKLIST",
        f"Case: {matter.get('matter_name', 'Unknown')}",
        "",
        "=" * 80,
        "",
        "EXCULPATORY EVIDENCE TO DEMAND:",
        "",
        "[ ] Evidence favorable to defendant on guilt or punishment",
        "[ ] Witness credibility/impeachment evidence:",
        "    [ ] Prior inconsistent statements",
        "    [ ] Bias, motive to lie, or interest in outcome",
        "    [ ] Criminal convictions of prosecution witnesses",
        "    [ ] Pending charges against prosecution witnesses",
        "    [ ] Promises, deals, or benefits given to witnesses",
        "[ ] Evidence of other suspects or alternative perpetrators",
        "[ ] Evidence contradicting prosecution theory",
        "[ ] Evidence supporting defense theory",
        "[ ] Police officer disciplinary records (Brady-Giglio material)",
        "[ ] Evidence of investigative misconduct",
        "[ ] Exculpatory scientific evidence or conflicting expert opinions",
        "",
    ]

    # Add case-specific items
    if matter.get("search_and_seizure"):
        lines.extend([
            "SEARCH & SEIZURE SPECIFIC:",
            "[ ] Evidence of illegal search or seizure",
            "[ ] Evidence warrant was based on false information",
            "[ ] Evidence of consent being involuntary or coerced",
            "",
        ])

    if matter.get("interrogation"):
        lines.extend([
            "CONFESSION/INTERROGATION SPECIFIC:",
            "[ ] Evidence confession was coerced or involuntary",
            "[ ] Evidence of Miranda violations",
            "[ ] Evidence of promises made to induce confession",
            "",
        ])

    return "\n".join(lines)


def _generate_suppression_motion(matter: dict[str, Any], result: dict[str, Any]) -> str:
    """Generate motion to suppress from LSW agent output."""
    artifacts = result.get("artifacts", {})
    lsw_output = artifacts.get("lsw", {}) if isinstance(artifacts, dict) else {}

    metadata = matter.get("metadata", {})

    lines = [
        f"{metadata.get('court', 'SUPERIOR COURT')}",
        f"{metadata.get('jurisdiction', 'STATE')}",
        "",
        "=" * 80,
        "",
        f"{matter.get('matter_name', 'State v. Unknown')}",
        f"Case No. {metadata.get('case_number', 'Unknown')}",
        "",
        "MOTION TO SUPPRESS EVIDENCE",
        "",
        "=" * 80,
        "",
    ]

    # Get motion from LSW agent
    if isinstance(lsw_output, dict) and "suppression_motion" in lsw_output:
        lines.append(str(lsw_output["suppression_motion"]))
    else:
        # Fallback: generate basic motion structure
        lines.extend([
            "COMES NOW the Defendant, by and through undersigned counsel, and respectfully ",
            "moves this Court to suppress all evidence obtained as a result of violations of ",
            "the Fourth, Fifth, and/or Sixth Amendments to the United States Constitution.",
            "",
            "FACTUAL BACKGROUND",
            "",
            f"On or about {matter.get('arrest', {}).get('date', '[DATE]')}, "
            f"{matter.get('client', {}).get('name', 'Defendant')} was arrested by "
            f"{matter.get('arrest', {}).get('arresting_agency', 'law enforcement')}.",
            "",
            "LEGAL ARGUMENT",
            "",
        ])

        # Add constitutional arguments based on identified issues
        issues = matter.get("constitutional_issues", [])
        for issue in issues:
            if isinstance(issue, dict):
                issue_type = issue.get("issue_type", "")
                if "fourth" in issue_type:
                    lines.extend([
                        "I. THE EVIDENCE MUST BE SUPPRESSED DUE TO FOURTH AMENDMENT VIOLATIONS",
                        "",
                        f"{issue.get('description', 'Fourth Amendment violation occurred.')}",
                        "",
                    ])
                elif "fifth" in issue_type:
                    lines.extend([
                        "II. DEFENDANT'S STATEMENTS MUST BE SUPPRESSED DUE TO FIFTH AMENDMENT VIOLATIONS",
                        "",
                        f"{issue.get('description', 'Fifth Amendment violation occurred.')}",
                        "",
                    ])

        lines.extend([
            "",
            "CONCLUSION",
            "",
            "For the foregoing reasons, Defendant respectfully requests that this Court grant ",
            "this Motion to Suppress and exclude all evidence obtained in violation of Defendant's ",
            "constitutional rights.",
            "",
            "Respectfully submitted,",
            "",
            "[DEFENSE ATTORNEY NAME]",
            "Attorney for Defendant",
            "",
            "**ATTORNEY REVIEW REQUIRED** - This is a draft motion. Review and customize before filing.",
        ])

    return "\n".join(lines)


def _generate_preservation_letter(matter: dict[str, Any], result: dict[str, Any]) -> str:
    """Generate evidence preservation/spoliation letter."""
    metadata = matter.get("metadata", {})

    lines = [
        "[ATTORNEY LETTERHEAD]",
        "",
        datetime.now().strftime("%B %d, %Y"),
        "",
        f"{matter.get('arrest', {}).get('arresting_agency', 'Police Department')}",
        "ATTENTION: Evidence Custodian",
        "",
        f"Re: {matter.get('matter_name', 'Unknown Case')}",
        f"    Case No. {metadata.get('case_number', 'Unknown')}",
        "    EVIDENCE PRESERVATION DEMAND",
        "",
        "Dear Sir or Madam:",
        "",
        f"This office represents {matter.get('client', {}).get('name', 'the defendant')} in the above-referenced matter. ",
        "This letter serves as formal notice and demand that your agency preserve all evidence related to this case.",
        "",
        "YOU ARE HEREBY DIRECTED TO PRESERVE THE FOLLOWING EVIDENCE:",
        "",
        "1. All video and audio recordings (dash cam, body cam, surveillance, interrogation)",
        "2. All photographs and digital images",
        "3. All physical evidence seized or collected",
        "4. All laboratory tests, reports, and raw data",
        "5. All written reports, notes, and memoranda",
        "6. All electronic data (emails, text messages, GPS data, computer files)",
        "7. All radio communications and dispatch logs",
        "8. All calibration and maintenance records for testing equipment",
        "",
    ]

    # Add case-specific preservation items
    if matter.get("search_and_seizure", {}).get("was_search_conducted"):
        lines.extend([
            "SEARCH & SEIZURE RELATED:",
            "9. All search warrant materials and applications",
            "10. All evidence of property damage during search",
            "",
        ])

    if matter.get("interrogation", {}).get("was_interrogated"):
        lines.extend([
            "INTERROGATION RELATED:",
            "11. All recordings of interrogation (video and audio)",
            "12. All written statements and Miranda waivers",
            "",
        ])

    lines.extend([
        "FAILURE TO PRESERVE THIS EVIDENCE MAY RESULT IN:",
        "- Sanctions by the court",
        "- Adverse jury instructions",
        "- Dismissal of charges",
        "- Civil liability for spoliation",
        "",
        "Please confirm in writing within 7 days that all evidence is being preserved.",
        "",
        "Respectfully submitted,",
        "",
        "[DEFENSE ATTORNEY NAME]",
        "Attorney for Defendant",
    ])

    return "\n".join(lines)


def _generate_witness_checklist(matter: dict[str, Any], result: dict[str, Any]) -> str:
    """Generate witness interview checklist."""
    lines = [
        "WITNESS INTERVIEW CHECKLIST",
        f"Case: {matter.get('matter_name', 'Unknown')}",
        "",
        "=" * 80,
        "",
        "KEY WITNESSES TO INTERVIEW:",
        "",
    ]

    # Officers
    officers = matter.get("arrest", {}).get("officers", [])
    if officers:
        lines.append("LAW ENFORCEMENT WITNESSES:")
        for officer in officers:
            lines.append(f"[ ] {officer}")
            lines.append("    Questions to ask:")
            lines.append("    - What was the basis for the stop/arrest?")
            lines.append("    - What training have you had in [relevant area]?")
            lines.append("    - Have you testified in court before?")
            lines.append("")

    lines.extend([
        "",
        "CLIENT INTERVIEW:",
        f"[ ] {matter.get('client', {}).get('name', 'Client')}",
        "    Questions to ask:",
        "    - Detailed timeline of events",
        "    - What exactly did officers say/do?",
        "    - Were there any witnesses?",
        "    - Any medical conditions or injuries?",
        "    - Any prior contacts with these officers?",
        "",
        "ADDITIONAL WITNESSES:",
        "[ ] [Identify additional witnesses from police reports]",
        "",
    ])

    return "\n".join(lines)


def _generate_motion_recommendations(matter: dict[str, Any], result: dict[str, Any]) -> str:
    """Generate pretrial motion recommendations."""
    lines = [
        "PRETRIAL MOTION RECOMMENDATIONS",
        f"Case: {matter.get('matter_name', 'Unknown')}",
        "",
        "=" * 80,
        "",
        "RECOMMENDED MOTIONS (Prioritized):",
        "",
    ]

    priority_num = 1

    # Check for suppression opportunities
    if matter.get("constitutional_issues"):
        lines.append(f"{priority_num}. MOTION TO SUPPRESS EVIDENCE [HIGH PRIORITY]")
        lines.append("   Status: Draft motion generated")
        lines.append("   Basis: Constitutional violations identified")
        lines.append("")
        priority_num += 1

    # Always recommend discovery motion
    lines.append(f"{priority_num}. MOTION TO COMPEL DISCOVERY [HIGH PRIORITY]")
    lines.append("   Status: Discovery demand letter generated")
    lines.append("   Timing: File if prosecution fails to respond timely")
    lines.append("")
    priority_num += 1

    # Other common motions
    lines.extend([
        f"{priority_num}. MOTION FOR BILL OF PARTICULARS [MEDIUM PRIORITY]",
        "   Purpose: Obtain more specific details about charges",
        "",
        f"{priority_num + 1}. MOTION TO REDUCE BAIL [CASE DEPENDENT]",
        "   Purpose: Reduce excessive bail if client is detained",
        "",
        f"{priority_num + 2}. MOTION FOR SPEEDY TRIAL [CASE DEPENDENT]",
        "   Purpose: Enforce constitutional right to speedy trial",
        "   Timing: File if prosecution causing delays",
        "",
        f"{priority_num + 3}. MOTION IN LIMINE [PRE-TRIAL]",
        "   Purpose: Exclude prejudicial evidence at trial",
        "   Topics: Prior bad acts, character evidence, etc.",
        "",
    ])

    return "\n".join(lines)


def _slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text[:100]


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the State Criminal Defense practice pack",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with existing matter file
  python -m packs.criminal_defense.run --matter path/to/matter.json

  # Validate matter file without executing
  python -m packs.criminal_defense.run --matter path/to/matter.json --validate-only

  # List available fixtures
  python -m packs.criminal_defense.run --list-fixtures
        """
    )
    parser.add_argument("--matter", type=Path, help="Path to the matter YAML or JSON file")
    parser.add_argument("--validate-only", action="store_true", help="Only validate the matter file without executing")
    parser.add_argument("--list-fixtures", action="store_true", help="List available fixture files")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Output directory for artifacts (default: outputs/)")

    args = parser.parse_args()

    # List fixtures
    if args.list_fixtures:
        fixtures_dir = Path(__file__).parent / "fixtures"
        if fixtures_dir.exists():
            print("Available fixture files:")
            for fixture in sorted(fixtures_dir.glob("*.json")):
                print(f"  - {fixture.name}")
        else:
            print("No fixtures directory found.")
        return

    # Require --matter for other operations
    if not args.matter:
        parser.error("--matter is required (or use --list-fixtures)")

    if not args.matter.exists():
        parser.error(f"Matter file '{args.matter}' was not found")

    # Validate only
    if args.validate_only:
        try:
            matter = load_matter(args.matter)
            print(f"✓ Matter file '{args.matter}' is valid!")
            print(f"  Jurisdiction: {matter.get('metadata', {}).get('jurisdiction', 'Not specified')}")
            print(f"  Client: {matter.get('client', {}).get('name', 'Unknown')}")
            print(f"  Charges: {len(matter.get('charges', []))}")
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

    print(f"Executing workflow for: {matter.get('matter_name', 'Untitled Matter')}")
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
