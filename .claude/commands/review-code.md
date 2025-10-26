---
description: Perform code review on recent changes
---

Perform a comprehensive code review:

**Review Checklist:**

1. **Code Quality**
   - Type hints on all function signatures
   - Docstrings for public functions and classes
   - Line length ≤120 characters
   - Proper use of `from __future__ import annotations`

2. **Legal Standards**
   - Provenance tracking in agent responses
   - Citation verification mechanisms
   - No hallucination risks
   - Human review requirements documented

3. **Error Handling**
   - Graceful fallbacks for missing data
   - Proper exception handling with logging
   - Unresolved issues tracked in responses

4. **Testing**
   - Tests for new functionality
   - Edge cases covered
   - Mock LLM calls in tests
   - Fixtures used for test data

5. **Security**
   - No hardcoded credentials
   - Input validation present
   - Sensitive data redaction in logs

Run linting:
```bash
make lint
# or
ruff check --fix .
```

If $ARGUMENTS provided, review specific file:
```bash
# Focus review on: $ARGUMENTS
```

Provide detailed feedback with specific line numbers and improvement suggestions.
