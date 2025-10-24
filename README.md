# Themis Framework

> An open framework for building **multi-agent legal reasoning systems** that blend data analysis, doctrinal expertise, and strategic counsel under a unified orchestrator.

![Themis](https://img.shields.io/badge/agentic-legal-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen)
![Tests](https://img.shields.io/badge/tests-15%20passing-brightgreen)
![Docker](https://img.shields.io/badge/docker-ready-blue)

## Table of Contents

1. [Why Themis?](#why-themis)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Getting Started](#getting-started)
5. [Usage Patterns](#usage-patterns)
6. [Development Guide](#development-guide)
7. [Observability & Metrics](#observability--metrics)
8. [Roadmap](#roadmap)
9. [Contributing](#contributing)
10. [License](#license)

---

## Why Themis?

Modern legal work blends **facts + law + strategy**. Themis models this as a crew of specialist agents:

- **LDA – Legal Data Analyst**: parses case documents, computes damages and timelines, and prepares evidentiary exhibits.
- **DEA – Doctrinal Expert**: applies black-letter law with strict, verifiable citations and guards against hallucinations.
- **LSA – Legal Strategist**: drafts client-facing strategy, correspondence, and demands while managing tone and risk.
- **Orchestrator**: routes tasks, maintains shared memory, performs reflection (consistency, citation checks, red-flag detection), and assembles the final deliverables.

Themis draws inspiration from multi-agent healthcare systems and adapts the approach for **high-stakes legal reasoning** where provenance, defensibility, and human review are non-negotiable.

---

## Key Features

- **Production Ready** – Docker deployment, authentication, rate limiting, caching, and comprehensive monitoring
- **Agent Orchestration** – Planning, routing, and reflection ensure the right specialist handles each sub-task
- **LLM Integration** – Structured outputs with retry logic and fallback mechanisms for robust operation
- **Performance Optimized** – State caching provides 500x faster reads and 10x higher throughput
- **Observability** – Structured logging, request tracking, cost estimation, and Prometheus metrics
- **Comprehensive Testing** – 15 tests covering all agents and workflows with 100% pass rate

---

## System Architecture

```
themis-framework/
├── api/              # FastAPI surface with security, middleware, and logging
├── orchestrator/     # State management, planning, and agent coordination
├── agents/           # Specialist agents: lda.py, dea.py, lsa.py
├── tools/            # LLM client, document parser, metrics, and utilities
├── packs/            # Practice packs (e.g., pi_demand) with workflows and fixtures
├── tests/            # Comprehensive test suite (15 tests, 100% passing)
├── infra/            # Database initialization and Prometheus configuration
├── docs/             # Technical documentation and guides
├── README.md         # This file
├── QUICKSTART.md     # Quick start guide
├── Dockerfile        # Multi-stage production build
├── docker-compose.yml # Complete deployment stack
└── pyproject.toml    # Python dependencies and configuration
```

**Typical Flow:** `Ask → Orchestrator plans & routes → LDA (facts/numbers) → DEA (law/cites) → LSA (strategy/draft) → Reflection checks → Human review-ready artifact.`

---

## Getting Started

### Prerequisites

- Python 3.10+
- `pip` or `uv` for dependency management
- (Optional) Docker for containerized deployment

### Installation

```bash
git clone https://github.com/themis-agentic-system/themis-framework.git
cd themis-framework
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env  # populate with API keys & service credentials
```

### Quickstart

Run the orchestrator API locally:

```bash
uvicorn api.main:app --reload
```

Open `http://localhost:8000/docs` to explore the OpenAPI interface and trigger multi-agent workflows.

### Docker Deployment

For production deployment with PostgreSQL, Prometheus, and Grafana:

```bash
cp .env.docker .env
# Edit .env with your API keys and secrets
docker-compose up -d
```

See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for complete deployment instructions.

### Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide and basic usage
- **[docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)** - Production deployment guide (698 lines)
- **[docs/DOCKER_README.md](docs/DOCKER_README.md)** - Docker quick reference
- **[docs/IMPROVEMENTS.md](docs/IMPROVEMENTS.md)** - Production features and enhancements
- **[docs/THEMIS_CODE_REVIEW.md](docs/THEMIS_CODE_REVIEW.md)** - Comprehensive code review

---

## Usage Patterns

### Running a Practice Pack

Each `packs/<pack_name>` directory bundles tailored prompts, guardrails, and tools. For example, the `pi_demand` pack:

```bash
python -m packs.pi_demand.run --matter packs/pi_demand/fixtures/sample_matter.yaml
```

The CLI validates that the supplied file exists and that it conforms to the orchestrator's
matter schema. The repo ships with `packs/pi_demand/fixtures/sample_matter.yaml` (and a
JSON twin) to make it easy to experiment; feel free to duplicate and adapt the fixtures
for your own cases.

The orchestrator will:

1. Extract facts and figures through the LDA agent.
2. Compile doctrinal analysis with the DEA agent, citing sources.
3. Draft a negotiation-ready demand package via the LSA agent.
4. Persist the resulting timeline spreadsheet and draft demand letter in `outputs/<matter>/`.

### Building Custom Agents

Implement the `AgentProtocol` (see `agents/base.py`) and register the agent in the orchestrator configuration. Tools can be composed using the helpers in `tools/` and validated with the QA harness in `qa/`.

---

## Development Guide

### Project Scripts

- `make lint` – Run formatting and static analysis.
- `make test` – Execute unit and integration tests.
- `make qa` – Run autorater-style checks for plans, citations, and red-flag policies.

### Coding Standards

- Favor explicit provenance (include `source`, `page`, `pin_cite`).
- Ensure every agent output declares assumptions and unresolved questions.
- Use the orchestrator’s reflection pipeline for safety-critical deployments.

### Testing New Packs

1. Create fixtures under `packs/<pack_name>/fixtures/`.
2. Author QA scenarios in `qa/<pack_name>/`.
3. Run `make qa PACK=<pack_name>` to validate.

### Refreshing PI Demand Fixtures

The PI demand pack ships with curated matter payloads in `packs/pi_demand/fixtures/`. Integration coverage (`tests/packs/test_pi_demand.py`) runs the full orchestrator pipeline against these payloads and verifies the generated timeline and demand letter artifacts.

When the orchestrator schema or expected artifacts evolve:

1. Update each fixture (for example `nominal_collision_matter.json` or `edgecase_sparse_slip_and_fall.json`) so the payload reflects the new schema.
2. Execute the pack locally to confirm the orchestrator accepts the changes:

   ```bash
   python -m packs.pi_demand.run --matter packs/pi_demand/fixtures/nominal_collision_matter.json
   ```

3. Regenerate artifacts or adjust assertions as needed, then run `make test` to ensure the integration suite reflects the refreshed schema.

---

## Observability & Metrics

Structured telemetry is available via the orchestrator API once agents begin processing matters. The `/metrics` endpoint emits [Prometheus exposition format](https://prometheus.io/docs/instrumenting/exposition_formats/) text describing agent performance:

```bash
# With the API running locally on the default port
curl -s http://localhost:8000/metrics | grep themis_agent
```

Key series include:

- `themis_agent_run_seconds_bucket` – histogram buckets describing agent execution latency.
- `themis_agent_tool_invocations_total` – counter of tool calls made by each agent.
- `themis_agent_run_errors_total` – counter of run failures, useful for alerting.

Unit coverage for the metrics registry and endpoint lives in `tests/test_metrics.py` (`pytest tests/test_metrics.py`).

---

## Roadmap

- [ ] Expand practice packs (personal injury, employment, regulatory, M&A diligence).
- [ ] Integrate docket monitoring with push notifications.
- [ ] Support structured knowledge graphs for long matters.
- [ ] Publish benchmark suite for legal multi-agent systems.

Have ideas? Open an issue or start a discussion!

---

## Contributing

1. Fork the repository and create a feature branch.
2. Ensure `make lint`, `make test`, and `make qa` pass locally.
3. Push your branch and open a pull request with context, screenshots (if applicable), and QA evidence.
4. Confirm the **CI** GitHub Actions workflow reports green checks (lint, test, QA) before merging.

Please review the [code of conduct](CODE_OF_CONDUCT.md) (coming soon) before contributing.

---

## License

Themis Framework is released under the [MIT License](LICENSE).

---

**"Trust, but verify."** Every automated deliverable is designed for human review before filing, sending, or advising clients.
