# Quickstart Guide

This guide walks through installing the Themis framework locally, running the API, and exercising the
sample practice pack.

## 1. Prerequisites

- Python 3.10 or newer
- `pip` (or another PEP-517 compatible installer)
- (Optional) Anthropic API key for live LLM calls – the framework falls back to a deterministic stub
  when the key is absent.

## 2. Install the project

```bash
# Clone the repository
git clone https://github.com/themis-agentic-system/themis-framework.git
cd themis-framework

# Create an isolated environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies and dev tooling
pip install -e .[dev]
```

## 3. Configure environment variables

Copy the sample environment file and edit it as needed:

```bash
cp .env.example .env
```

Populate `ANTHROPIC_API_KEY` to talk to Anthropic’s API.  Leave it unset to operate in stub mode.  Set
`THEMIS_API_KEY` if you want the HTTP API to require authentication tokens.

## 4. Run the FastAPI service

```bash
uvicorn api.main:app --reload
```

- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics (Prometheus exposition)

## 5. Exercise the personal-injury practice pack

```bash
python -m packs.pi_demand.run --matter packs/pi_demand/fixtures/nominal_collision_matter.json
```

The CLI validates the matter payload, executes the default task graph, and persists artifacts under
`outputs/<matter-slug>/` (timeline CSV, demand letter, complaint draft, evidence checklist, etc.).
Use `--list-fixtures` to discover other bundled matters.

## 6. Run the automated checks

```bash
# Execute the full pytest suite
make test

# Lint the codebase
make lint

# Smoke-test importability and packaging constraints
make qa
```

You now have a fully functioning local environment that mirrors the configuration used in CI.
