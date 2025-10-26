---
description: Run full case analysis workflow on a matter file
---

Analyze the case file at: $ARGUMENTS

Follow these steps:

1. **Load the Matter**: Read and validate the matter JSON file
2. **Extract Facts (LDA)**: Parse documents, build timeline, analyze key facts
3. **Identify Issues (DEA)**: Spot legal issues and research applicable law
4. **Assess Strategy (LSA)**: Evaluate strengths, weaknesses, and strategic options
5. **Generate Summary**: Produce a comprehensive case analysis report

**Output should include:**
- Fact pattern summary with timeline
- Legal issues identified with strength assessment
- Applicable authorities and citations
- Strategic recommendations
- Risk assessment and contingencies

Use the orchestrator service with all agents: LDA → DEA → LSA
