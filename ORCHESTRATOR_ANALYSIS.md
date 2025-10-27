# Themis Orchestrator & Agent Data Flow Analysis

## Executive Summary

The Themis orchestrator coordinates 4 specialized legal agents through 6 phases to produce court-ready legal documents. Each agent builds on the outputs of prior agents, culminating in the DDA (Document Drafting Agent) generating formal legal documents.

**Current Status**: System is configured correctly but missing the DOCUMENT_ASSEMBLY phase, so DDA never runs.

---

## Agent Roles & Outputs

### 1. LDA (Legal Data Analyst)
**Phase**: INTAKE_FACTS
**Purpose**: Extract structured facts, build timelines, calculate damages

**Output Structure**:
```json
{
  "agent": "lda",
  "facts": {
    "fact_pattern_summary": ["fact 1", "fact 2", ...],
    "timeline": [{"date": "...", "event": "..."}],
    "parties": ["Party A", "Party B"],
    "matter_overview": "Summary text",
    "damages_analysis": {...},
    "timeline_analysis": {...}
  },
  "provenance": {
    "source_documents": [...],
    "tools_used": ["document_parser", "timeline_builder"]
  },
  "unresolved_issues": [...]
}
```

---

### 2. DEA (Doctrinal Expert Agent)
**Phase**: ISSUE_FRAMING, RESEARCH_RETRIEVAL, APPLICATION_ANALYSIS
**Purpose**: Identify legal issues, retrieve authorities, apply law to facts

**Output Structure**:
```json
{
  "agent": "dea",
  "legal_analysis": {
    "issues": [
      {
        "issue": "Negligence Per Se - DUI Violation",
        "elements": ["Duty", "Breach", "Causation", "Damages"],
        "strength": "strong",
        "analysis": "Detailed legal analysis..."
      }
    ],
    "authorities": [
      {
        "cite": "Cal. Veh. Code § 23152",
        "holding": "DUI statute establishes duty of care",
        "relevance": "Direct applicability to facts"
      }
    ],
    "analysis": "Comprehensive legal analysis text..."
  },
  "authorities": {
    "controlling_authorities": ["Cal. Veh. Code § 23152", ...],
    "contrary_authorities": [...]
  },
  "provenance": {
    "tools_used": ["issue_spotter", "citation_retriever"],
    "citations_considered": [...]
  },
  "unresolved_issues": [...]
}
```

---

### 3. LSA (Legal Strategy Agent)
**Phase**: DRAFT_REVIEW
**Purpose**: Develop negotiation strategy, assess risks, create client-safe summaries

**Output Structure**:
```json
{
  "agent": "lsa",
  "strategy": {
    "recommended_actions": ["Action 1", "Action 2", ...],
    "negotiation_positions": {
      "opening_demand": "$750,000",
      "ideal_settlement": "$500,000",
      "minimum_acceptable": "$350,000"
    },
    "contingencies": ["Contingency plan 1", ...],
    "risk_assessment": {
      "confidence": 85,
      "risks": [...],
      "opportunities": [...]
    }
  },
  "draft": {
    "client_safe_summary": "Based on our analysis, we recommend...",
    "next_steps": ["File complaint", "Serve defendant", ...],
    "risk_level": "low"
  },
  "provenance": {
    "tools_used": ["strategy_template", "risk_assessor"],
    "assumptions": [...]
  },
  "unresolved_issues": [...]
}
```

---

### 4. DDA (Document Drafting Agent)
**Phase**: DOCUMENT_ASSEMBLY
**Purpose**: Generate formal legal documents (complaints, motions, demand letters, memos)

**Expected Inputs** (from prior agents):
```python
matter.get("facts", {})              # From LDA
matter.get("legal_analysis", {})     # From DEA
matter.get("strategy", {})           # From LSA
matter.get("document_type")          # From user or orchestrator
matter.get("jurisdiction")           # From user
```

**Output Structure**:
```json
{
  "agent": "dda",
  "document": {
    "full_text": "SUPERIOR COURT OF CALIFORNIA...\n\nCOMPLAINT\n\n...",
    "word_count": 2500,
    "page_estimate": 10,
    "sections": ["caption", "introduction", "facts_section", ...],
    "citation_count": 5
  },
  "metadata": {
    "document_type": "complaint",
    "jurisdiction": "California",
    "word_count": 2500,
    "section_count": 5
  },
  "tone_analysis": {
    "overall_score": 85,
    "issues": [],
    "strengths": ["Clear structure", "Modern prose"],
    "recommendations": []
  },
  "validation": {
    "is_valid": true,
    "missing_elements": [],
    "warnings": [],
    "completeness_score": 95
  },
  "provenance": {
    "tools_used": ["section_generator", "citation_formatter", ...],
    "document_type": "complaint",
    "jurisdiction": "California"
  },
  "unresolved_issues": []
}
```

---

## Orchestrator Data Propagation

### Phase Execution Flow (service.py lines 164-332)

```python
# For each phase/node in the graph:
for node in graph.topological_order():
    agent_name = step["agent"]
    agent = self.agents.get(agent_name)

    # 1. BUILD INPUT: Merge original matter + all prior outputs
    agent_input = deepcopy(plan_matter)
    agent_input.update(propagated)

    # 2. RUN AGENT
    output = await agent.run(agent_input)

    # 3. STORE OUTPUT: Save to artifacts and propagated
    artifacts[agent_name] = output
    propagated[agent_name] = output

    # 4. EXTRACT ARTIFACTS: Pull out specific keys for easy access
    produced_artifacts = _collect_expected_artifacts(
        output,
        step.get("expected_artifacts", [])
    )
    if produced_artifacts:
        propagated.update(produced_artifacts)
        plan_matter.update(produced_artifacts)
```

### Example: What DDA Receives

When DDA runs in phase 6, `matter` contains:

```python
{
    # Original user input
    "summary": "Car accident case...",
    "parties": ["Plaintiff: John Doe", "Defendant: Jane Smith"],
    "jurisdiction": "California",
    "metadata": {...},

    # Complete LDA output
    "lda": {
        "agent": "lda",
        "facts": {...},
        "provenance": {...},
        "unresolved_issues": [...]
    },

    # Complete DEA output
    "dea": {
        "agent": "dea",
        "legal_analysis": {...},
        "authorities": {...},
        "provenance": {...},
        "unresolved_issues": [...]
    },

    # Complete LSA output
    "lsa": {
        "agent": "lsa",
        "strategy": {...},
        "draft": {...},
        "provenance": {...},
        "unresolved_issues": [...]
    },

    # Extracted artifacts for convenient access
    "facts": {...},              # Extracted from LDA
    "legal_analysis": {...},     # Extracted from DEA
    "authorities": {...},        # Extracted from DEA
    "strategy": {...},           # Extracted from LSA
    "draft": {...}               # Extracted from LSA
}
```

---

## The 6 Orchestration Phases

### Phase 1: INTAKE_FACTS
- **Primary**: LDA
- **Supporting**: DEA (reflection), LSA (synthesis)
- **Outputs**: `facts` artifact
- **Exit Signal**: `facts` present

### Phase 2: ISSUE_FRAMING
- **Primary**: DEA (or LDA for damages-focused cases)
- **Supporting**: LDA (data validation), LSA (synthesis)
- **Outputs**: `legal_analysis` artifact
- **Exit Signal**: `issues` present
- **Entry Signal**: `facts` required

### Phase 3: RESEARCH_RETRIEVAL
- **Primary**: DEA
- **Supporting**: LDA (quant validation)
- **Outputs**: `authorities` artifact
- **Exit Signals**: `controlling_authority`, `contrary_authority`
- **Entry Signal**: `issues` required

### Phase 4: APPLICATION_ANALYSIS
- **Primary**: DEA (or LDA for damages modeling)
- **Supporting**: LDA (model validation), LSA (synthesis)
- **Outputs**: `analysis` artifact
- **Exit Signal**: `analysis` present
- **Entry Signal**: `controlling_authority` required

### Phase 5: DRAFT_REVIEW
- **Primary**: LSA
- **Supporting**: DEA (citation review), LDA (numerical review)
- **Outputs**: `draft` artifact
- **Exit Signals**: `draft`, `client_safe_summary`
- **Entry Signal**: `analysis` required

### Phase 6: DOCUMENT_ASSEMBLY ⚠️ **MISSING FROM CODE**
- **Primary**: DDA
- **Supporting**: DEA (citation validation), LSA (tone review)
- **Outputs**: `document` artifact
- **Exit Signal**: `document` present
- **Entry Signal**: `draft` required

---

## Current System Issue

### Problem
The `_build_phase_definitions()` method in `orchestrator/policy.py` only defines 5 phases (lines 256-376). **Phase 6 (DOCUMENT_ASSEMBLY) is missing**, so the DDA agent is never invoked.

### Fix Applied
Added DOCUMENT_ASSEMBLY phase definition:
```python
PhaseDefinition(
    phase=Phase.DOCUMENT_ASSEMBLY,
    description="Generate formal legal documents with proper formatting and citations.",
    default_primary_agent="dda",
    expected_artifacts=[
        {
            "name": "document",
            "description": "Court-ready legal document (complaint, motion, demand letter, etc.).",
        },
    ],
    exit_signals=["document"],
    entry_signals=["draft"],
    supporting_agents=[
        SupportingAgent(
            agent="dea",
            role="citation_validation",
            description="Verify all legal citations are properly formatted.",
        ),
        SupportingAgent(
            agent="lsa",
            role="tone_review",
            description="Ensure document tone is appropriate for the document type.",
        ),
    ],
)
```

---

## Document Type Determination

### Current Implementation
DDA currently defaults to "memorandum" if no document_type is specified.

### Proposed Enhancement
The orchestrator should determine document_type based on:
1. User's explicit request in matter payload
2. LLM analysis of user intent (summary field)
3. Case characteristics (settlement vs. litigation)

### Document Types Supported
- **complaint**: Formal civil complaint for filing in court
- **demand_letter**: Pre-litigation settlement demand
- **motion**: Motion to the court (requires motion_type)
- **memorandum**: Legal memo for internal use

### Recommended Logic
```python
def determine_document_type(matter: dict[str, Any]) -> str:
    # Explicit user specification
    if "document_type" in matter or "document_type" in matter.get("metadata", {}):
        return matter.get("document_type") or matter["metadata"]["document_type"]

    # Use LLM to analyze intent from summary
    summary = matter.get("summary", "").lower()

    # Keyword-based heuristics
    if any(word in summary for word in ["demand", "settlement", "negotiate"]):
        return "demand_letter"
    elif any(word in summary for word in ["file", "complaint", "sue", "lawsuit"]):
        return "complaint"
    elif any(word in summary for word in ["motion", "dismiss", "summary judgment"]):
        return "motion"
    else:
        # Call LLM to determine based on full context
        return llm_determine_document_type(matter)
```

---

## Testing the Complete Flow

### Expected End-to-End Output

**Input**: Personal injury car accident case
**Expected Final Output**:

```json
{
  "plan_id": "uuid",
  "status": "complete",
  "artifacts": {
    "lda": {
      "facts": {
        "fact_pattern_summary": [11 facts],
        "timeline": [5 events],
        ...
      }
    },
    "dea": {
      "legal_analysis": {
        "issues": [6 issues],
        "authorities": [8 citations],
        "analysis": "Full legal analysis..."
      }
    },
    "lsa": {
      "strategy": {
        "negotiation_positions": {...},
        "recommended_actions": [...]
      }
    },
    "dda": {
      "document": {
        "full_text": "SUPERIOR COURT OF CALIFORNIA\n\nJohn Doe,\n  Plaintiff,\nv.  No. XX-XXXX\nJane Smith,\n  Defendant.\n\nCOMPLAINT\n========\n\n..."
      }
    }
  }
}
```

---

## Next Steps

1. ✅ **Add DOCUMENT_ASSEMBLY phase** to orchestrator policy
2. ⏳ **Implement smart document type detection** using LLM
3. ⏳ **Update UI** to display formatted document instead of raw JSON
4. ⏳ **Test end-to-end** with various case types
5. ⏳ **Add document export** (PDF, DOCX) functionality

---

## Key Insights

### Why the System Failed Before
1. DOCUMENT_ASSEMBLY phase was missing → DDA never ran
2. UI showed raw JSON → Users couldn't see the (non-existent) document
3. extended_thinking incompatibility → LLM calls were failing silently

### Why It Will Work Now
1. All 6 phases are defined and will execute in order
2. Data propagates correctly through `propagated` dictionary
3. DDA receives all prior agent outputs (`facts`, `legal_analysis`, `strategy`)
4. UI extracts and displays `document.full_text` in readable format
5. LLM calls work with `extended_thinking=False`

### Critical Success Factors
- **Data extraction**: Orchestrator must extract artifacts by name (e.g., "facts" from LDA core)
- **Signal validation**: Exit signals must match artifact names
- **Agent cooperation**: Each agent must output data in expected structure
- **LLM prompts**: DDA section_generator must synthesize all prior analysis into coherent document

---

*Generated: 2025-10-27*
