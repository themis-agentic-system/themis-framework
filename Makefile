PYTHON ?= python3

.PHONY: test lint qa

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

qa:
	$(PYTHON) -m pytest qa
