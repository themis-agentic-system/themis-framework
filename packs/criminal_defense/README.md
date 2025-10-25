# State Criminal Defense Practice Pack

The State Criminal Defense Practice Pack is a comprehensive workflow for analyzing criminal cases, generating discovery demands, identifying constitutional issues, and drafting suppression motions. This pack leverages the Themis multi-agent framework with LLM-powered jurisdictional analysis to provide intelligent, case-specific defense strategies.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Matter File Format](#matter-file-format)
- [Generated Artifacts](#generated-artifacts)
- [Example Workflows](#example-workflows)
- [Fixtures Library](#fixtures-library)
- [LLM-Powered Jurisdictional Analysis](#llm-powered-jurisdictional-analysis)
- [Constitutional Issue Detection](#constitutional-issue-detection)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

---

## Overview

This practice pack automates criminal defense analysis and document generation by:

1. **CCA (Criminal Case Analyst)**: Analyzes case facts, identifies Fourth/Fifth/Sixth Amendment issues, and flags discovery priorities
2. **DMS (Discovery & Motion Specialist)**: Drafts jurisdiction-specific discovery demands and identifies required pretrial motions
3. **LSW (Legal Strategist & Writer)**: Generates persuasive suppression motions and strategic recommendations

The pack then generates:
- **Discovery Demand Letters**: Comprehensive, charge-specific requests
- **Constitutional Issues Analysis**: Fourth, Fifth, and Sixth Amendment violation assessment
- **Suppression Motions**: Fully drafted motions when constitutional issues warrant (no frivolous filings)
- **Brady/Giglio Checklists**: Exculpatory evidence demands
- **Case Timeline**: Chronological events with constitutional issue flagging
- **Evidence Preservation Letters**: Spoliation prevention demands
- **Witness Interview Checklists**: Key witnesses and questions
- **Pretrial Motion Recommendations**: Strategic motion planning

---

## Features

### Intelligent Constitutional Analysis

- **Fourth Amendment**: Search/seizure legality, warrant validity, Franks violations, consent issues
- **Fifth Amendment**: Miranda compliance, confession voluntariness, custodial interrogation analysis
- **Sixth Amendment**: Suggestive identifications, right to counsel violations
- **Suppression Motion Generation**: Only when legally justified (no frivolous motions)

### LLM-Powered Jurisdictional Research

- **No Hardcoded Jurisdictions**: Agents dynamically research jurisdiction-specific discovery rules, case law, and procedural requirements
- **All 50 States Supported**: Works with any U.S. state jurisdiction
- **Federal Cases**: Can be adapted for federal criminal cases (separate pack recommended)
- **Local Court Rules**: Agents can research and apply local court procedural rules

### Charge-Specific Discovery

- **DUI/DWI**: Breathalyzer calibration, field sobriety test videos, officer training, Title 17/implied consent compliance
- **Drug Offenses**: Lab analysis, chain of custody, CI reliability records, search warrant affidavits
- **Theft/Burglary**: Surveillance video, forensics, witness statements
- **Fraud**: Computer forensics, bank records, authorization agreements
- **Assault/Domestic Violence**: 911 calls, body cam footage, medical records, prior complaints

### Case Type Coverage

- **Misdemeanors**: DUI, simple assault, theft, trespass, domestic battery
- **Felonies**: Drug trafficking, burglary, fraud, aggravated assault, weapons offenses
- **Both Levels**: Pack handles both misdemeanor and felony cases seamlessly

---

## Installation

The State Criminal Defense pack is included with the Themis Framework. No additional installation is required if you have Themis installed.

```bash
# If you haven't installed Themis:
git clone https://github.com/themis-agentic-system/themis-framework.git
cd themis-framework
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

---

## Quick Start

### Running the Pack

```bash
# Run with one of the included fixtures
python -m packs.criminal_defense.run --matter packs/criminal_defense/fixtures/dui_california.json

# Run with your own matter file
python -m packs.criminal_defense.run --matter path/to/your/matter.json

# Validate matter file without executing
python -m packs.criminal_defense.run --matter your_matter.json --validate-only

# List available fixtures
python -m packs.criminal_defense.run --list-fixtures
```

### Output

The pack generates artifacts in the `outputs/<case-name>/` directory:

```
outputs/
└── 24cr12345/
    ├── case_timeline.csv
    ├── constitutional_issues_analysis.txt
    ├── discovery_demand.txt
    ├── brady_giglio_checklist.txt
    ├── motion_to_suppress.txt
    ├── evidence_preservation_letter.txt
    ├── witness_interview_checklist.txt
    └── pretrial_motion_recommendations.txt
```

---

## Matter File Format

Matter files can be in JSON or YAML format. The basic structure:

```json
{
  "matter": {
    "metadata": {
      "case_number": "24CR12345",
      "jurisdiction": "California",
      "court": "Superior Court of San Diego County",
      "case_type": "misdemeanor"
    },
    "client": {
      "name": "John Doe",
      "dob": "1990-01-15",
      "prior_record": "none"
    },
    "charges": [
      {
        "statute": "Vehicle Code § 23152(a)",
        "description": "Driving under the influence",
        "degree": "misdemeanor",
        "potential_sentence": "Up to 6 months jail"
      }
    ],
    "arrest": {
      "date": "2024-10-15T23:45:00",
      "location": "Main St & 5th Ave, San Diego",
      "arresting_agency": "San Diego PD",
      "officers": ["Officer Smith #1234"],
      "circumstances": "Traffic stop for alleged weaving"
    },
    "search_and_seizure": {
      "was_search_conducted": true,
      "search_type": "automobile",
      "items_seized": ["Open container"],
      "location_searched": "Vehicle"
    },
    "interrogation": {
      "was_interrogated": true,
      "miranda_given": true,
      "miranda_waived": true,
      "statements_made": ["I had two beers"],
      "interrogation_location": "Roadside",
      "duration": "15 minutes"
    },
    "constitutional_issues": [
      {
        "issue_type": "fourth_amendment",
        "description": "No reasonable suspicion for traffic stop",
        "evidence": ["Officer claimed 'weaving' but dashcam may contradict"]
      }
    ],
    "defense_theory": "No probable cause for stop. Client was driving normally.",
    "goals": {
      "primary": "Dismissal via suppression",
      "fallback": "Reduction to reckless driving"
    }
  }
}
```

### Required Fields

- **client**: Client information (name required)
- **charges**: Array of charges (at least one charge required)
- **arrest**: Arrest information (date required)

### Recommended Fields

- **metadata.jurisdiction**: For jurisdiction-specific discovery and motion generation
- **metadata.case_type**: Felony or misdemeanor classification
- **search_and_seizure**: Details of any search conducted
- **interrogation**: Details of any questioning
- **identification**: Details of any ID procedures (lineup, showup, photo array)
- **constitutional_issues**: Any Fourth/Fifth/Sixth Amendment concerns you've identified
- **defense_theory**: Your theory of the case
- **discovery_outstanding**: Evidence you still need

---

## Generated Artifacts

### 1. Case Timeline (CSV)

Chronological timeline of key case events with constitutional issue flags:

```csv
date,event,constitutional_flag
2024-10-15,Arrest: Traffic stop for weaving,
2024-10-15,Interrogation conducted,⚠ Miranda issue
2024-10-20,Discovery received: police report,
```

### 2. Constitutional Issues Analysis (TXT)

Comprehensive analysis of Fourth, Fifth, and Sixth Amendment issues:
- Issue identification and severity assessment
- Legal standards and case law
- Evidence supporting suppression
- Discovery needed to develop motion
- Likelihood of success estimates
- Motion recommendations with priorities

### 3. Discovery Demand Letter (TXT)

Jurisdiction-specific discovery demand including:
- Mandatory disclosure requirements (per jurisdiction)
- Charge-specific discovery items (DUI, drug, theft, fraud, assault)
- Brady/Giglio exculpatory evidence demands
- Impeachment evidence requests
- Chain of custody documentation
- Scientific reports and expert qualifications
- Video/audio recordings
- Witness statements

### 4. Brady/Giglio Checklist (TXT)

Exculpatory evidence checklist:
- Favorable evidence on guilt or punishment
- Witness credibility/impeachment material
- Alternative suspects
- Police misconduct evidence
- Conflicting expert opinions

### 5. Motion to Suppress (TXT)

**Only generated when constitutional issues warrant it** (no frivolous motions):
- Fourth Amendment: Illegal searches/seizures
- Fifth Amendment: Miranda violations, coerced confessions
- Sixth Amendment: Suggestive identifications
- Memorandum of law with case citations
- Proposed findings of fact
- Fruit of the poisonous tree analysis

### 6. Evidence Preservation Letter (TXT)

Spoliation prevention demand letter:
- Video/audio recordings
- Physical evidence
- Digital data
- Laboratory tests and raw data
- Calibration records
- Legal consequences of destruction

### 7. Witness Interview Checklist (TXT)

Organized witness list with interview questions:
- Law enforcement witnesses
- Alleged victims
- Eyewitnesses
- Expert witnesses
- Case-specific question templates

### 8. Pretrial Motion Recommendations (TXT)

Prioritized motion strategy:
- Motion to suppress (if constitutional issues present)
- Motion to compel discovery
- Motion for bill of particulars
- Motion to reduce bail
- Motion for speedy trial
- Motions in limine
- Priority rankings and timing

---

## Example Workflows

### Scenario 1: DUI with Fourth Amendment Issues (California)

```bash
python -m packs.criminal_defense.run \
  --matter packs/criminal_defense/fixtures/dui_california.json
```

**Charge**: DUI (VC 23152(a) and (b))

**Constitutional Issue**: Traffic stop based on "weaving within lane" without actual traffic violation

**Generated Documents**:
- Discovery demand requests dash cam, breathalyzer calibration, officer training
- Constitutional analysis identifies People v. Perez issue (weaving insufficient)
- Motion to suppress generated challenging stop basis
- If stop suppressed → all evidence suppressed → dismissal

---

### Scenario 2: Drug Possession with Warrant Issues (New York)

```bash
python -m packs.criminal_defense.run \
  --matter packs/criminal_defense/fixtures/drug_possession_warrant_new_york.json
```

**Charge**: Criminal Possession of Controlled Substance 3rd Degree (felony)

**Constitutional Issue**: Search warrant may be based on unreliable CI; Franks hearing warranted

**Generated Documents**:
- Discovery demand requests sealed warrant affidavit, CI reliability records
- Constitutional analysis identifies Franks v. Delaware issue
- Motion to suppress generated challenging warrant probable cause
- Evidence preservation letter demands all CI documentation

---

### Scenario 3: Theft with Miranda Violation (Texas)

```bash
python -m packs.criminal_defense.run \
  --matter packs/criminal_defense/fixtures/theft_burglary_texas.json
```

**Charge**: Burglary of Building, Theft (felonies)

**Constitutional Issues**:
- Miranda violation (custodial interrogation without knowing waiver)
- Suggestive showup identification

**Generated Documents**:
- Discovery demand requests interrogation video, identification procedure documentation
- Constitutional analysis identifies Fifth and Sixth Amendment violations
- Motion to suppress statements and identification generated
- Witness checklist includes security guard (identification witness)

---

### Scenario 4: Fraud with Interrogation Issues (Florida)

```bash
python -m packs.criminal_defense.run \
  --matter packs/criminal_defense/fixtures/fraud_florida.json
```

**Charge**: Communications Fraud, Identity Theft, Forgery (felonies)

**Constitutional Issues**:
- Fifth Amendment: Client invoked counsel but questioning continued
- Fourth Amendment: Overbroad search warrant

**Generated Documents**:
- Discovery demand requests interrogation recordings, complete authorization agreements
- Constitutional analysis identifies Edwards v. Arizona violation (continued questioning after invocation)
- Motion to suppress all statements generated
- Challenge to warrant scope and particularity

---

### Scenario 5: Domestic Violence with Miranda Violation (Illinois)

```bash
python -m packs.criminal_defense.run \
  --matter packs/criminal_defense/fixtures/assault_domestic_violence_illinois.json
```

**Charge**: Domestic Battery (misdemeanor)

**Constitutional Issues**:
- Fifth Amendment: Custodial interrogation without Miranda warnings
- Fourth Amendment: Entry into home without exigent circumstances

**Generated Documents**:
- Discovery demand requests body cam footage, 911 call, alleged victim's prior complaints
- Constitutional analysis identifies Miranda violation and unlawful entry
- Motion to suppress statements generated
- Evidence preservation letter emphasizes body cam footage critical

---

## Fixtures Library

The pack includes 5 diverse fixtures covering common criminal case types:

| Fixture | Jurisdiction | Charges | Key Issues | Case Type |
|---------|-------------|---------|------------|-----------|
| `dui_california.json` | California | DUI (VC 23152) | Fourth Amendment: Insufficient basis for stop; Title 17 compliance | Misdemeanor |
| `drug_possession_warrant_new_york.json` | New York | Drug Possession 3rd Degree | Fourth Amendment: Franks hearing (warrant based on unreliable CI) | Felony |
| `theft_burglary_texas.json` | Texas | Burglary, Theft | Fifth Amendment: Miranda violation; Sixth Amendment: Suggestive identification | Felony |
| `fraud_florida.json` | Florida | Fraud, Identity Theft, Forgery | Fifth Amendment: Continued interrogation after invocation; Fourth Amendment: Overbroad warrant | Felony |
| `assault_domestic_violence_illinois.json` | Illinois | Domestic Battery | Fifth Amendment: No Miranda warnings; Fourth Amendment: Unlawful entry | Misdemeanor |

Use these fixtures as templates for your own cases!

---

## LLM-Powered Jurisdictional Analysis

**Unlike traditional practice packs**, this pack does **not** hardcode jurisdiction-specific rules. Instead, it leverages LLM agents to dynamically research and apply:

### What Agents Research

1. **Discovery Rules**:
   - State criminal procedure codes
   - Brady/Giglio obligations
   - Automatic disclosure requirements
   - Discovery deadlines and procedures

2. **Suppression Motion Standards**:
   - Fourth Amendment search/seizure law in jurisdiction
   - Fifth Amendment Miranda/confession law
   - Sixth Amendment identification law
   - Jurisdiction-specific case precedents

3. **Procedural Requirements**:
   - Motion filing deadlines
   - Notice requirements (e.g., CPL § 710.30 in NY)
   - Hearing procedures (Huntley, Mapp, Wade in NY; Franks hearings, etc.)
   - Local court rules

4. **Evidentiary Standards**:
   - DUI chemical test requirements (Title 17 in CA, implied consent laws)
   - Chain of custody rules
   - Expert qualification requirements
   - Authentication requirements

### Benefits

- **Unlimited Jurisdictions**: Works with all 50 states without code changes
- **Up-to-Date Law**: LLM knowledge reflects recent legal developments
- **Local Court Rules**: Can adapt to specific court local rules
- **Flexible**: Handles unique jurisdiction-specific procedures

### How It Works

When you provide a matter file with `"jurisdiction": "Arizona"`, the agents will:
1. Research Arizona's criminal discovery rules
2. Identify Arizona-specific suppression motion standards
3. Apply Arizona case law to constitutional issues
4. Generate discovery demands compliant with Arizona Criminal Rule 15.1
5. Draft suppression motions citing Arizona appellate decisions

**No hardcoding required** - the LLM agents handle jurisdictional research automatically.

---

## Constitutional Issue Detection

### Fourth Amendment Analysis

The CCA agent analyzes:

**Searches**:
- Was there a search under Katz v. United States?
- If warrant: Valid probable cause? Particularity? Proper execution?
- If warrantless: Does exception apply (consent, exigent, automobile, plain view, incident to arrest)?
- Franks issues: False statements in affidavit?

**Seizures**:
- Was there reasonable suspicion for stop? (Terry v. Ohio)
- Probable cause for arrest?
- Pretextual stop issues

**Recommended Motions**:
- Motion to Suppress Evidence (illegal search)
- Motion to Suppress Statements (fruit of illegal seizure)
- Franks Motion (challenge warrant affidavit)

### Fifth Amendment Analysis

The CCA agent analyzes:

**Miranda**:
- Custodial interrogation?
- Miranda warnings given?
- Knowing and intelligent waiver?
- Invocation of rights?
- Continued questioning after invocation? (Edwards v. Arizona)

**Voluntariness**:
- Coercive circumstances?
- Promises or threats?
- Defendant characteristics (age, education, mental condition)
- Duration of interrogation

**Recommended Motions**:
- Motion to Suppress Confession (Miranda violation)
- Motion to Suppress Confession (involuntary)

### Sixth Amendment Analysis

The CCA agent analyzes:

**Identifications**:
- Unnecessarily suggestive procedure?
- Reliability factors (Neil v. Biggers, Manson v. Brathwaite)
- Post-indictment lineup without counsel? (United States v. Wade)

**Right to Counsel**:
- Massiah violations (post-indictment interrogation)
- Denial of counsel at critical stage

**Recommended Motions**:
- Motion to Suppress Identification
- Wade hearing request

---

## Customization

### Adding Case-Specific Analysis

Edit the matter file to include detailed constitutional issues:

```json
"constitutional_issues": [
  {
    "issue_type": "fourth_amendment",
    "description": "Search warrant based on stale information - no activity within 72 hours of warrant execution",
    "evidence": [
      "Affidavit dated 10 days before search",
      "All alleged drug sales occurred 2+ weeks prior",
      "No recent surveillance documented"
    ]
  }
]
```

### Customizing Discovery Demands

The DMS agent automatically generates charge-specific discovery, but you can guide it by including:

```json
"discovery_outstanding": [
  "Specific item you need",
  "Expert reports on forensics",
  "Prior complaints against officer"
]
```

### Programmatic Usage

```python
import asyncio
from pathlib import Path
from packs.criminal_defense.run import load_matter, persist_outputs
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

## Troubleshooting

### Common Issues

**Problem**: "Matter file validation failed"

**Solution**: Review the error messages. Ensure your matter file includes:
- `client` object with `name` field
- `charges` array with at least one charge (with `statute` and `description`)
- `arrest` object with `date` field

---

**Problem**: "No suppression motion generated"

**Solution**: The pack only generates suppression motions when constitutional issues are identified. This is intentional to avoid frivolous motions. Check:
- Did you include `constitutional_issues` in your matter file?
- Are the issues Fourth, Fifth, or Sixth Amendment violations?
- Review the constitutional_issues_analysis.txt for recommendations

---

**Problem**: "Discovery demand is too generic"

**Solution**: Provide more detail in your matter file:
- Include specific charges (not just "drug offense")
- Add `discovery_outstanding` field with specific items needed
- Include details in `search_and_seizure`, `interrogation`, etc.

---

**Problem**: "Jurisdiction-specific rules not applied"

**Solution**: Ensure `metadata.jurisdiction` is specified in your matter file. The LLM agents will research that jurisdiction's rules. You can also add guidance in `defense_theory` field to direct agent research.

---

## Ethical Safeguards

### No Frivolous Motions

The pack includes safeguards to prevent unethical practice:

1. **Threshold Requirements**: Suppression motions only generated when constitutional issue severity is "medium" or higher

2. **Disclosure to User**: All generated motions include disclaimer: "**ATTORNEY REVIEW REQUIRED** - This is a draft. Verify factual basis before filing."

3. **Issue Analysis**: Each issue includes likelihood-of-success estimate

4. **Attorney Supervision**: All outputs are drafts requiring attorney review and customization

### Professional Responsibility

Remember:
- **Brady obligations**: Demand all exculpatory evidence
- **No coaching**: Don't suggest client fabricate evidence or testimony
- **Competence**: Review all AI-generated analysis for accuracy
- **Confidentiality**: Matter files may contain privileged information - handle securely

---

## Support

For issues, questions, or feature requests:
- Open an issue on the Themis Framework GitHub repository
- Consult the main Themis documentation

---

**"Innocent until proven guilty."** All generated documents require attorney review before use. This pack assists with legal analysis but does not replace attorney judgment and expertise.
