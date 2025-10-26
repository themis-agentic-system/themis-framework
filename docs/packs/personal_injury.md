# Personal Injury Practice Pack

## Overview
The personal injury pack delivers an end-to-end knowledge workflow for automobile, premises, and general negligence cases. It introduces a shared matter schema, reusable knowledge assets, and generators for every major litigation document from intake through trial.

Jurisdiction-specific rules (limitations periods, comparative negligence models, jury instructions) are resolved dynamically. When the pack encounters an unfamiliar venue it queries the configured LLM connector and blends the response with safe baseline defaults so every U.S. jurisdiction is supported out of the box.

## Setup
1. Install dependencies: `pip install -e .` (PyYAML is optional for YAML fixtures).
2. Review sample matter data in `packs/personal_injury/fixtures/` and tailor to your case.
3. Run the CLI to generate documents: `python -m packs.personal_injury.run --matter packs/personal_injury/fixtures/sample_matter.json`.

## Supported Documents
The pack exposes the following generators (keys in parentheses):
- Case Intake Memorandum (`intake_memo`)
- Settlement Demand Letter (`demand_letter`)
- Civil Complaint (`complaint`)
- Answer / Responsive Pleading (`answer`)
- Written Discovery Package (`discovery`)
- Deposition Outline (`deposition_outline`)
- Mediation Statement (`mediation_brief`)
- Trial Brief (`trial_brief`)
- Witness & Exhibit Lists (`witness_exhibit_lists`)
- Proposed Jury Instructions (`jury_instructions`)
- Settlement Agreement (`settlement_agreement`)

Each generator produces tagged analytics context for downstream reporting.

## Shared Matter Schema
All documents consume the normalized schema defined in `packs/personal_injury/schema.py`. Key sections include:
- `metadata`: id, title, jurisdiction, cause_of_action, phase, venue
- `parties`: name, role, counsel, contact
- `insurance`: carrier, policy_number, coverage_limits, adjuster, contact
- `deadlines`: name, due, description, source
- `injuries`: description, body_parts, severity, treatment, prognosis
- `medical`: provider records with date, description, balance
- `liability`: theories with supporting facts and defenses
- `damages`: specials, generals, punitive, wage_loss, future_medical
- `facts`: incident_description, timeline, evidence, witnesses
- `goals` and `notes`: negotiation objectives, history, and strategy annotations

Use `packs.personal_injury.schema.required_fields()` for validation hints and `load_matter()` to transform incoming payloads.

## Workflows
Phase orchestration lives in `packs/personal_injury/workflows.py`. Workflow phases:
1. **Intake** – triage, insurance capture, engagement tasks
2. **Pre-suit** – demand preparation, negotiation positioning
3. **Litigation** – pleadings, discovery, deposition planning
4. **ADR** – mediation briefing, settlement strategy
5. **Trial** – trial briefs, witness/exhibit prep, jury instructions

Run `python -m packs.personal_injury.run --matter <file> --list` to view document availability by phase. `catalog_assets()` returns phase-to-document mapping and knowledge library metadata.

## Knowledge Assets
Reference assets live in `packs/personal_injury/knowledge/`:
- Model fact patterns and damages baselines
- Discovery question banks (interrogatories, RFPs, RFAs)
- Negotiation playbooks with scenario checklists
- Exemplar authorities and filings
- Damages calculator utilities

## Testing Guidance
Execute `pytest tests/personal_injury` to run unit fixtures, workflow regression checks, and smoke tests that render a complete case packet. The CLI smoke test writes output to a temporary directory to ensure packaging coverage. All assets should pass CI before deployment.
