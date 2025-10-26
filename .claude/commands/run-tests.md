---
description: Run Themis test suite with coverage reporting
---

Run the complete Themis test suite:

```bash
# Run all tests with verbose output
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=agents --cov=orchestrator --cov=tools --cov-report=term-missing

# Run QA smoke tests
python -m pytest qa/ -v
```

If $ARGUMENTS is provided, run specific test file:
```bash
python -m pytest tests/test_$ARGUMENTS.py -v
```

**Check for:**
- All tests passing (target: >85% pass rate)
- Coverage above 80%
- No deprecation warnings
- QA smoke tests all green

If any tests fail, analyze the failure and suggest fixes.
