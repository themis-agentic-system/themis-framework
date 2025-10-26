---
description: Generate demand letter for personal injury case
---

Generate a demand letter for the matter at: $ARGUMENTS

**Workflow:**

1. Load the matter file and validate schema
2. Run LDA agent to extract facts and calculate damages
3. Run DEA agent to identify legal issues and authorities
4. Run LSA agent to develop negotiation strategy
5. Run DDA agent to draft formal demand letter

**Required Matter Fields:**
- parties (plaintiff and defendant)
- documents (incident reports, medical records)
- events (timeline of incident and treatment)
- damages (economic and non-economic)
- goals (settlement target)

**Output:**
- Professional demand letter (demand_letter.txt)
- Timeline of events (timeline.csv)
- Medical expense summary (medical_expenses.csv)
- Supporting evidence checklist

Use the personal injury practice pack workflow:
```bash
python -m packs.personal_injury.run --matter $ARGUMENTS
```
