# Themis Framework

Themis is a Python framework for coordinating legal reasoning agents behind a FastAPI surface.  The
project packages a set of async agents (fact intake, doctrinal analysis, strategic planning, and
document drafting) and an orchestrator that turns matters into execution plans, executes them with
traceability, and persists artifacts for review.

## Highlights

- **Agent roster** – Four specialised agents (`agents/`) share a common base class and rely on
  instrumented tools for fact extraction, legal analysis, strategy, and drafting.
- **Task-graph orchestrator** – The orchestrator builds a phased DAG for each matter, caches state in
  SQLite, and records traces while invoking agents in dependency order.
- **Secure API surface** – A FastAPI service exposes planning/execution endpoints with request
  logging, rate limiting, payload guards, audit trails, API-key auth, and Prometheus-style metrics
  export.
- **Practice packs** – CLI workflows demonstrate how orchestrated runs can persist drafts, timelines,
  and checklists for specific practice areas (e.g., personal injury).
- **LLM abstraction** – Tooling seamlessly switches between Anthropic’s SDK and a deterministic stub
  for offline development while keeping structured output contracts stable.

## Quick start

1. **Clone and enter the project**
   ```bash
   git clone https://github.com/themis-agentic-system/themis-framework.git
   cd themis-framework
   ```
2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -e .[dev]
   ```
3. **Configure environment variables** – Copy `.env.example` to `.env` and optionally set
   `ANTHROPIC_API_KEY`.  Without a key the framework runs in deterministic stub mode.
4. **Launch the API**
   ```bash
   uvicorn api.main:app --reload
   ```
   - Interactive docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health
   - Metrics: http://localhost:8000/metrics
   To require authentication, export `THEMIS_API_KEY` before starting the server.

## Running the orchestrator from the CLI

The personal-injury practice pack demonstrates end-to-end execution:

```bash
python -m packs.pi_demand.run --matter packs/pi_demand/fixtures/nominal_collision_matter.json
```

The CLI validates the matter payload, runs the orchestrator, and saves generated artifacts (timeline
CSV, demand letter, complaint draft, evidence checklist, etc.) under `outputs/<matter-slug>/`.

## Testing and quality gates

- Run the full pytest suite (57 tests):
  ```bash
  make test
  ```
- Lint the codebase with Ruff:
  ```bash
  make lint
  ```
- Smoke-test importability of public modules:
  ```bash
  make qa
  ```
  The commands above are defined in the project Makefile.

## Project layout

```
api/             FastAPI application, middleware, and auth glue
agents/          Agent implementations and shared tooling
connectors/      Plug-in registry for external systems
orchestrator/    Planning policy, state management, routing, and persistence
packs/           Practice-pack CLIs, schemas, and fixtures
tests/           Pytest suites covering agents, orchestration, and packs
tools/           LLM client, document parser, metrics registry, utilities
infra/           SQL and observability configuration snippets
qa/              Lightweight smoke tests for packaging/import checks
```

## Documentation

Extended guides live in `docs/`:

- `docs/DEPLOYMENT_GUIDE.md` – Step-by-step production deployment notes
- `docs/DOCKER_README.md` – Container image build and compose instructions
- `docs/IMPLEMENTATION_SUMMARY.md` – Architectural rationale
- `docs/SECURITY_IMPROVEMENTS.md` – Hardened API controls and checklist
- `docs/GOVERNANCE.md` – Maintenance workflow and review policy

See `docs/README.md` for the complete index.

## License

The project is distributed under the MIT License.  See `pyproject.toml` for metadata.
