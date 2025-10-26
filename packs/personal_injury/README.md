# Personal Injury Practice Pack

This pack orchestrates intake, negotiation, litigation, ADR, and trial workflows for personal injury matters. It provides:

- A normalized matter schema spanning parties, deadlines, insurance, medical, damages, and liability data
- Document generators for every stage of a case (intake memos, demands, pleadings, discovery, ADR, trial, settlement)
- Scenario workflows that map case phases to checklists and document playbooks
- Jurisdictional rule helpers covering statutes of limitations, comparative negligence, and jury instruction lookups sourced dynamically from LLM research when needed
- Knowledge assets: model fact patterns, exemplar filings, discovery banks, damages calculators, and negotiation playbooks

## Quick Start
```bash
python -m packs.personal_injury.run --matter packs/personal_injury/fixtures/sample_matter.json
```

Use `--list` to view available document keys and `--documents` to limit the generation set.

## Key Modules
- `schema.py`: dataclasses, validation helpers, and analytics metadata
- `config.py`: document registry with analytics tags
- `generators/`: implementations for each document type
- `workflows.py`: intake → trial phase mapping with checklists
- `rules.py`: jurisdictional calculators with LLM-backed research fallbacks
- `knowledge/`: curated references for damages, discovery, negotiation, and authorities

## Testing
Run targeted tests with:
```bash
pytest tests/personal_injury
```
Smoke tests render a full document packet and ensure every generator links to the shared schema.
