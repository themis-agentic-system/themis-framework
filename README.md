# Themis Framework

> An open framework for building **multi-agent legal reasoning systems** — blending data analysis, doctrinal expertise, and strategic counsel under a unified orchestrator.

![Themis](https://img.shields.io/badge/agentic-legal-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-orange)

## Why Themis?
Modern legal work blends **facts + law + strategy**. Themis models this as a crew of specialist agents:
- **LDA – Legal Data Analyst**: parses case docs, computes damages/timelines, builds exhibits.
- **DEA – Doctrinal Expert**: applies black-letter law with strict, verifiable citations.
- **LSA – Legal Strategist**: drafts client-facing strategy, letters, demands; adapts tone and risk.
- **Orchestrator**: routes tasks, keeps memory, performs reflection (consistency, citations, red-flags).

Inspired by multi-agent health systems (DS/DE/HC + Orchestrator), adapted for **high-stakes legal reasoning**.

---

## Features (alpha)
- **Orchestrated agents** with task routing + reflection checks
- **RAG with provenance** (file:page, pin-cites required)
- **Analytics** via pandas/duckdb → XLSX exhibits (demands, timelines)
- **Tooling layer**: files/OCR, legal search, docket timelines
- **Guardrails**: no-send without review, red-flag policy

---

## Architecture
themis-framework/
api/                # FastAPI surface for orchestration
orchestrator/       # router (intent → plan), memory, reflection (QA/ethics)
agents/             # lda.py, dea.py, lsa.py (specialists)
tools/              # files.py, legal_search.py, docket.py, tabular.py, timeline.py
packs/              # practice packs (pi_demand, crim_motions, etc.)
qa/                 # autorater-like tests for plans, citations, red-flags
infra/              # docker-compose, (optional) terraform
README.md
.env.example
pyproject.toml

**Flow:** Ask → Orchestrator plans & routes → LDA (facts/numbers) → DEA (law/cites) → LSA (strategy/draft) → Reflection checks → Single review-ready artifact.

---
