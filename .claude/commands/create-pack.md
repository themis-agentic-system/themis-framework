---
description: Create a new practice pack with boilerplate
---

Create a new practice pack: $ARGUMENTS

**Steps:**

1. **Create Directory Structure:**
```bash
mkdir -p packs/$ARGUMENTS/fixtures
touch packs/$ARGUMENTS/__init__.py
```

2. **Create Schema (packs/$ARGUMENTS/schema.py):**
```python
"""Schema definitions for $ARGUMENTS practice pack."""

MATTER_SCHEMA = {
    "type": "object",
    "properties": {
        "case_type": {"type": "string"},
        "parties": {"type": "array"},
        "documents": {"type": "array"},
        "events": {"type": "array"},
        "goals": {"type": "object"},
        # Add domain-specific fields
    },
    "required": ["case_type", "parties", "documents"]
}
```

3. **Create Run Script (packs/$ARGUMENTS/run.py):**
```python
"""CLI for $ARGUMENTS practice pack."""

import asyncio
import sys
from pathlib import Path
from orchestrator.service import OrchestratorService

async def main():
    matter_file = sys.argv[1] if len(sys.argv) > 1 else None
    if not matter_file:
        print("Usage: python -m packs.$ARGUMENTS.run --matter <file>")
        sys.exit(1)

    # Load matter
    import json
    with open(matter_file) as f:
        matter = json.load(f)

    # Validate schema
    # ... validation code ...

    # Execute workflow
    service = OrchestratorService()
    result = await service.execute(matter)

    # Save outputs
    output_dir = Path("output/$ARGUMENTS")
    output_dir.mkdir(parents=True, exist_ok=True)
    # ... save artifacts ...

    print(f"Workflow complete. Results in {output_dir}")

if __name__ == "__main__":
    asyncio.run(main())
```

4. **Create Sample Fixture (packs/$ARGUMENTS/fixtures/sample_matter.json)**

5. **Create README (packs/$ARGUMENTS/README.md)**

6. **Add Tests (tests/packs/test_$ARGUMENTS_pack.py)**

Generate all boilerplate files and provide usage instructions.
