# Personal Injury Demand & Complaint Practice Pack

The Personal Injury (PI) Demand & Complaint Practice Pack is a comprehensive workflow for generating both pre-litigation demand letters and formal civil complaints for personal injury cases. This pack leverages the Themis multi-agent framework to analyze case facts, apply relevant law, and produce client-ready documents with jurisdiction-specific causes of action.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Supported Jurisdictions](#supported-jurisdictions)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Matter File Format](#matter-file-format)
- [Generated Artifacts](#generated-artifacts)
- [Example Workflows](#example-workflows)
- [Fixtures Library](#fixtures-library)
- [Advanced Usage](#advanced-usage)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

---

## Overview

This practice pack automates the analysis and document generation for personal injury matters by:

1. **LDA (Legal Data Analyst)**: Extracts facts, timelines, damages, and key evidence from matter files
2. **DEA (Doctrinal Expert)**: Identifies applicable legal theories and retrieves relevant authorities
3. **LSA (Legal Strategist)**: Develops negotiation strategy and drafts client-facing documents

The pack then generates:
- **Demand Letters**: Pre-litigation settlement demands with damages analysis
- **Civil Complaints**: Formal pleadings with jurisdiction-specific causes of action
- **Supporting Artifacts**: Timeline, evidence checklist, medical expense summary, statute tracker

---

## Features

### Jurisdiction-Aware Complaint Generation
- **5 Supported Jurisdictions**: California, New York, Texas, Florida, Illinois
- **Automatic Cause of Action Selection**: Intelligently matches case facts to applicable legal theories
- **State-Specific Elements**: Incorporates jurisdiction-specific elements, statutes, and jury instructions

### Comprehensive Document Suite
- **Demand Letters**: Professional settlement demands with negotiation positions
- **Civil Complaints**: Formal pleadings ready for review and filing
- **Timeline CSV**: Chronological case events in spreadsheet format
- **Evidence Checklist**: Organized task list for case preparation
- **Medical Expense Summary**: CSV breakdown of medical costs
- **Statute of Limitations Tracker**: Jurisdiction-specific deadline tracking

### Validated Matter Schema
- **JSON Schema Validation**: Ensures matter files contain required fields
- **Helpful Error Messages**: Clear guidance when files are incomplete
- **Automatic Field Normalization**: Flexible input formats with intelligent defaults

---

## Supported Jurisdictions

### California
- **Causes of Action**: Negligence, Motor Vehicle, Premises Liability, Medical Malpractice, Product Liability, Dog Bite (Strict Liability)
- **Key Statutes**: Cal. Civ. Code § 1714, § 3342, CACI instructions
- **Statute of Limitations**: 2 years (PI), 3 years or 1 year from discovery (medical malpractice)

### New York
- **Causes of Action**: Negligence, Motor Vehicle, Premises Liability, Medical Malpractice
- **Key Statutes**: NY PJI instructions, CPLR provisions
- **Statute of Limitations**: 3 years (PI), 2.5 years (medical malpractice)
- **Special Requirements**: No-fault insurance thresholds, Certificate of merit for malpractice

### Texas
- **Causes of Action**: Negligence, Motor Vehicle, Premises Liability, Medical Malpractice
- **Key Statutes**: Texas common law, PJC instructions, Tex. Civ. Prac. & Rem. Code
- **Statute of Limitations**: 2 years (PI and medical malpractice)
- **Special Requirements**: Expert report within 120 days for medical malpractice, Non-economic damages cap ($250K per defendant in med mal)

### Florida
- **Causes of Action**: Negligence, Motor Vehicle, Premises Liability, Medical Malpractice
- **Key Statutes**: FSI instructions, Fla. Stat. provisions
- **Statute of Limitations**: 4 years (PI), 2 years (medical malpractice)
- **Special Requirements**: PIP thresholds, Pre-suit investigation for medical malpractice

### Illinois
- **Causes of Action**: Negligence, Motor Vehicle, Premises Liability, Medical Malpractice
- **Key Statutes**: IPI instructions, Illinois common law
- **Statute of Limitations**: 2 years (PI and medical malpractice)
- **Special Requirements**: Certificate of merit for medical malpractice

---

## Installation

The PI Demand & Complaint pack is included with the Themis Framework. No additional installation is required if you have Themis installed.

```bash
# If you haven't installed Themis:
git clone https://github.com/themis-agentic-system/themis-framework.git
cd themis-framework
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## Quick Start

### Running the Pack

```bash
# Run with one of the included fixtures
python -m packs.pi_demand.run --matter packs/pi_demand/fixtures/sample_matter.json

# Run with your own matter file
python -m packs.pi_demand.run --matter path/to/your/matter.json
```

### Output

The pack generates artifacts in the `outputs/<matter-name>/` directory:

```
outputs/
└── smith-v-central-logistics/
    ├── timeline.csv
    ├── draft_demand_letter.txt
    ├── draft_complaint.txt
    ├── evidence_checklist.txt
    ├── medical_expense_summary.csv
    └── statute_tracker.txt
```

---

## Matter File Format

Matter files can be in JSON or YAML format. The basic structure:

```json
{
  "matter": {
    "metadata": {
      "id": "PI-2024-001",
      "title": "Doe v. Smith",
      "jurisdiction": "California",
      "cause_of_action": "motor_vehicle"
    },
    "summary": "Brief description of the incident and injuries",
    "parties": [
      "Jane Doe (Plaintiff)",
      "John Smith (Defendant)"
    ],
    "counterparty": "Counsel for John Smith",
    "documents": [
      {
        "title": "Police Report",
        "date": "2024-01-15",
        "summary": "Officer documented collision at Main & 5th",
        "facts": [
          "Defendant ran red light",
          "Plaintiff had right of way"
        ]
      }
    ],
    "events": [
      {
        "date": "2024-01-15",
        "description": "Motor vehicle collision"
      }
    ],
    "issues": [
      {
        "issue": "Negligence",
        "facts": ["Defendant violated traffic laws"]
      }
    ],
    "authorities": [
      {
        "cite": "Cal. Veh. Code § 21453",
        "summary": "Red light violations"
      }
    ],
    "goals": {
      "settlement": "$150,000",
      "fallback": "$100,000"
    },
    "strengths": [
      "Clear liability",
      "Good medical documentation"
    ],
    "weaknesses": [
      "Plaintiff had prior injury"
    ],
    "concessions": [
      "Open to structured settlement"
    ],
    "evidentiary_gaps": [
      "Need updated medical report"
    ],
    "confidence_score": 75,
    "damages": {
      "specials": 50000,
      "generals": 100000,
      "punitive": null
    }
  }
}
```

### Required Fields

- **summary** or **description**: Case overview (minimum 10 characters)
- **parties**: Array of party names (minimum 1)
- **documents**: Array of documents (minimum 1)

### Recommended Fields

- **metadata.jurisdiction**: For jurisdiction-specific complaint generation
- **metadata.cause_of_action**: To specify the legal theory
- **events**: Timeline of key dates
- **issues**: Legal claims to pursue
- **goals**: Settlement objectives
- **damages**: Breakdown of economic and non-economic damages

---

## Generated Artifacts

### 1. Timeline (CSV)

Chronological list of case events extracted from matter data:

```csv
date,description
2024-03-14,Rear-end collision at Mission & 5th in San Francisco
2024-03-20,Initial consultation with Dr. Patel
2024-05-15,Employer letter confirming reduced hours
```

### 2. Demand Letter (TXT)

Pre-litigation settlement demand including:
- Matter summary
- Key facts
- Legal theories
- Negotiation positions
- Next steps
- Confidence assessment

### 3. Civil Complaint (TXT)

Formal pleading with:
- Case caption and court information
- Parties section
- Jurisdiction and venue
- General allegations (factual background)
- Causes of action with jurisdiction-specific elements
- Damages breakdown
- Prayer for relief
- Special requirements notes (e.g., certificate of merit)

### 4. Evidence Checklist (TXT)

Organized checklist including:
- Documents required
- Outstanding evidence gaps
- Witnesses to interview
- Legal authorities to research
- Pre-filing tasks

### 5. Medical Expense Summary (CSV)

Breakdown of medical costs:

```csv
Date,Provider,Service,Amount,Status
2024-03-15,Dr. Patel,Emergency Treatment,5000,Paid
2024-04-01,Physical Therapy,12 Sessions,2400,Pending
```

### 6. Statute of Limitations Tracker (TXT)

Jurisdiction-specific deadline tracking:
- Incident date
- Applicable statutes of limitation
- Calculated deadlines
- Important filing deadlines
- Warnings about tolling provisions

---

## Example Workflows

### Scenario 1: Motor Vehicle Collision (California)

```bash
python -m packs.pi_demand.run \
  --matter packs/pi_demand/fixtures/sample_matter.json
```

**Use Case**: Rear-end collision with clear liability. Need demand letter for insurance negotiations and complaint ready if settlement fails.

**Output**: Demand letter emphasizes liability and medical damages. Complaint pleads motor vehicle negligence with CACI instructions.

---

### Scenario 2: Premises Liability (Texas)

```bash
python -m packs.pi_demand.run \
  --matter packs/pi_demand/fixtures/premises_liability_texas.json
```

**Use Case**: Slip-and-fall at grocery store with video evidence. Video shows wet floor without warning signs.

**Output**: Complaint emphasizes premises owner's actual knowledge and failure to warn, citing Texas-specific case law.

---

### Scenario 3: Medical Malpractice (New York)

```bash
python -m packs.pi_demand.run \
  --matter packs/pi_demand/fixtures/medical_malpractice_new_york.json
```

**Use Case**: Surgical error during gallbladder surgery. Expert opinion secured.

**Output**: Complaint notes NY certificate of merit requirement. Statute tracker shows 2.5-year limitation period.

---

### Scenario 4: Product Liability (Florida)

```bash
python -m packs.pi_demand.run \
  --matter packs/pi_demand/fixtures/product_liability_florida.json
```

**Use Case**: Defective bicycle helmet failed in crash causing brain injury.

**Output**: Complaint pleads multiple theories (design defect, manufacturing defect, failure to warn) with punitive damages.

---

### Scenario 5: Dog Bite (California)

```bash
python -m packs.pi_demand.run \
  --matter packs/pi_demand/fixtures/dog_bite_california.json
```

**Use Case**: Child bitten by dog in public park. Strict liability under California law.

**Output**: Complaint emphasizes strict liability statute (no need to prove prior viciousness). Demand letter notes sympathetic minor plaintiff with permanent scarring.

---

## Fixtures Library

The pack includes 8 diverse fixtures covering common PI scenarios:

| Fixture | Jurisdiction | Type | Key Features |
|---------|-------------|------|--------------|
| `sample_matter.json` | California | Motor Vehicle | Basic rear-end collision |
| `nominal_collision_matter.json` | California | Motor Vehicle | Bike vs. vehicle with serious injuries |
| `edgecase_sparse_slip_and_fall.json` | California | Premises Liability | Minimal data edge case |
| `dog_bite_california.json` | California | Dog Bite | Strict liability, minor plaintiff |
| `medical_malpractice_new_york.json` | New York | Medical Malpractice | Surgical error, certificate of merit |
| `premises_liability_texas.json` | Texas | Premises Liability | Slip-and-fall with video evidence |
| `product_liability_florida.json` | Florida | Product Liability | Defective helmet, punitive damages |
| `workplace_injury_illinois.json` | Illinois | Third-Party Liability | Scaffolding collapse, OSHA violations |

Use these fixtures as templates for your own cases!

---

## Advanced Usage

### Customizing Jurisdiction Data

Edit `packs/pi_demand/jurisdictions.py` to:
- Add new jurisdictions
- Update statutes and jury instructions
- Modify causes of action elements
- Adjust damages standards

### Validating Matter Files

Run validation without executing the full pipeline:

```python
from pathlib import Path
from packs.pi_demand.schema import validate_matter_schema, format_validation_errors
import json

matter_data = json.loads(Path("your_matter.json").read_text())
is_valid, errors = validate_matter_schema(matter_data)
print(format_validation_errors(errors))
```

### Programmatic Usage

```python
import asyncio
from pathlib import Path
from packs.pi_demand.run import load_matter, persist_outputs
from orchestrator.service import OrchestratorService

async def run_analysis():
    matter = load_matter(Path("matter.json"))
    service = OrchestratorService()
    result = await service.execute(matter)
    paths = persist_outputs(matter, result)
    print(f"Generated {len(paths)} artifacts")

asyncio.run(run_analysis())
```

---

## Customization

### Adding Custom Causes of Action

1. Edit `packs/pi_demand/jurisdictions.py`
2. Add your cause of action to the jurisdiction dictionary:

```python
"custom_claim": {
    "name": "Custom Cause of Action",
    "statute": "Citation",
    "elements": [
        "Element 1",
        "Element 2",
        "Element 3"
    ],
    "jury_instructions": ["INST-123"]
}
```

### Modifying Complaint Templates

Edit `packs/pi_demand/complaint_generator.py` to customize:
- Complaint formatting
- Caption style
- Prayer for relief
- Signature blocks

### Adding Custom Artifacts

Edit the `persist_outputs()` function in `packs/pi_demand/run.py` to generate additional artifacts:

```python
# Add custom artifact
custom_path = matter_output_dir / "custom_artifact.txt"
custom_content = _generate_custom_artifact(matter, execution_result)
custom_path.write_text(custom_content, encoding="utf-8")
saved_paths.append(custom_path)
```

---

## Troubleshooting

### Common Issues

**Problem**: "Matter file validation failed"

**Solution**: Review the error messages. Ensure your matter file includes:
- `summary` or `description` (at least 10 characters)
- `parties` array with at least one party
- `documents` array with at least one document

---

**Problem**: "Jurisdiction '[NAME]' is not supported"

**Solution**: Check `packs/pi_demand/jurisdictions.py` for supported jurisdictions:
- California
- New York
- Texas
- Florida
- Illinois

To add support for a new jurisdiction, edit the `JURISDICTIONS` dictionary.

---

**Problem**: Complaint has generic elements instead of specific causes of action

**Solution**: Ensure your matter file includes:
```json
"metadata": {
  "jurisdiction": "California",
  "cause_of_action": "motor_vehicle"
}
```

If `cause_of_action` is omitted, the system will attempt to infer it from the summary.

---

**Problem**: Missing artifacts in output

**Solution**: Check that the orchestrator completed successfully. If agents fail, some artifacts may not generate. Review console output for errors.

---

## Schema Reference

### Metadata Fields

- **id**: Unique matter identifier (string)
- **title**: Matter title or case caption (string)
- **jurisdiction**: Jurisdiction for complaint generation (enum: CA, NY, TX, FL, IL)
- **cause_of_action**: Primary legal theory (enum: negligence, motor_vehicle, premises_liability, medical_malpractice, product_liability, dog_bite)

### Document Fields

- **title**: Document name (required)
- **date**: Document date in YYYY-MM-DD format
- **summary**: Document description
- **content**: Full document text
- **facts**: Array of key facts from document
- **type**: Document type classification

### Damages Fields

- **specials**: Economic damages (medical, lost wages) (number)
- **generals**: Non-economic damages (pain & suffering) (number)
- **punitive**: Punitive damages, if applicable (number or null)

---

## Contributing

To contribute improvements to the PI practice pack:

1. Add new fixture scenarios in `packs/pi_demand/fixtures/`
2. Update jurisdiction data in `jurisdictions.py`
3. Enhance artifact generation in `run.py`
4. Update this README with your changes
5. Add tests in `tests/packs/test_pi_demand.py`

---

## Support

For issues, questions, or feature requests:
- Open an issue on the Themis Framework GitHub repository
- Consult the main Themis documentation at `/docs`

---

**"Trust, but verify."** All generated documents require attorney review before use.
