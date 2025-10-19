# Themis Framework

> An open framework for building **multi-agent legal reasoning systems** that blend data analysis, doctrinal expertise, and strategic counsel under a unified orchestrator.

![Themis](https://img.shields.io/badge/agentic-legal-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-orange)

## Table of Contents

1. [Why Themis?](#why-themis)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Getting Started](#getting-started)
5. [Usage Patterns](#usage-patterns)
6. [Development Guide](#development-guide)
7. [Roadmap](#roadmap)
8. [Contributing](#contributing)
9. [License](#license)

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

- **Agent Orchestration** – Planning, routing, and reflection ensure the right specialist handles each sub-task.
- **Retrieval-Augmented Generation (RAG)** – Built-in provenance tracking (file + page + pin-cites) promotes verifiability.
- **Analytics Pipeline** – Pandas/DuckDB powered analytics that export XLSX exhibits (demands, timelines, damages models).
- **Rich Tooling Layer** – OCR, document ingestion, legal search, docket timelines, tabular helpers, and timeline builders.
- **Guardrails & Ethics** – “No-send” gates, red-flag policies, and consistency checks prevent unsupervised dispatch.

---

## System Architecture

```
themis-framework/
├── api/              # FastAPI surface for orchestration + external integrations
├── orchestrator/     # Intent parsing, planning, memory, and reflection logic
├── agents/           # Specialist agents: lda.py, dea.py, lsa.py
├── tools/            # Tool adapters: files.py, legal_search.py, docket.py, tabular.py, timeline.py
├── packs/            # Practice packs (e.g., pi_demand, crim_motions) combining agents + workflows
├── qa/               # Autorater-style tests for plans, citations, and red-flag policies
├── infra/            # Deployment assets (Docker Compose, optional Terraform)
├── README.md
├── .env.example
└── pyproject.toml
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
git clone https://github.com/<your-org>/themis-framework.git
cd themis-framework
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env  # populate with API keys & service credentials
```

### Scaffolding the Repository

The repo ships with a **minimal runnable scaffold** so you can experiment immediately:

```text
themis-framework/
├── api/                  # FastAPI app surface (uvicorn api.main:app --reload)
├── orchestrator/         # Planning/execution services + shared state helpers
├── agents/               # Stub LDA/DEA/LSA agents implementing the BaseAgent API
├── tools/                # Tool registry placeholder for future integrations
├── packs/pi_demand/      # Sample practice pack with an async CLI entry point
├── qa/                   # Placeholder for autorater + guardrail tests
├── infra/                # Deployment artifacts (add Docker/Terraform as needed)
├── pyproject.toml        # Poetry/setuptools metadata + dependencies
└── .env.example          # Template for API keys and service URLs
```

Key bootstrap commands:

```bash
# 1. Install runtime + dev dependencies
pip install -e .[dev]

# 2. Launch the FastAPI scaffold (serves /health + orchestrator stubs)
uvicorn api.main:app --reload

# 3. Exercise the sample practice pack (expects a YAML path)
python -m packs.pi_demand.run --matter path/to/matter.yaml
```

As you add real logic, replace the stubbed TODOs in `agents/`, enrich the orchestrator service, and expand the tool registry.

### Quickstart

Run the orchestrator API locally:

```bash
uvicorn api.main:app --reload
```

Open `http://localhost:8000/docs` to explore the OpenAPI interface and trigger multi-agent workflows.

---

## Usage Patterns

### Running a Practice Pack

Each `packs/<pack_name>` directory bundles tailored prompts, guardrails, and tools. For example, the `pi_demand` pack:

```bash
python -m packs.pi_demand.run --matter data/sample_matter.yaml
```

The orchestrator will:

1. Extract facts and figures through the LDA agent.
2. Compile doctrinal analysis with the DEA agent, citing sources.
3. Draft a negotiation-ready demand package via the LSA agent.
4. Run reflection checks before producing the final deliverables in `/outputs/`.

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

---

## Roadmap

- [ ] Expand practice packs (employment, regulatory, M&A diligence).
- [ ] Add courtroom presentation agent for visuals and demonstratives.
- [ ] Integrate docket monitoring with push notifications.
- [ ] Support structured knowledge graphs for long matters.
- [ ] Publish benchmark suite for legal multi-agent systems.

Have ideas? Open an issue or start a discussion!

---

## Contributing

1. Fork the repository and create a feature branch.
2. Ensure `make lint` and `make test` pass locally.
3. Submit a pull request with context, screenshots (if applicable), and QA evidence.

Please review the [code of conduct](CODE_OF_CONDUCT.md) (coming soon) before contributing.

---

## License

Themis Framework is released under the [MIT License](LICENSE).

---

**"Trust, but verify."** Every automated deliverable is designed for human review before filing, sending, or advising clients.
