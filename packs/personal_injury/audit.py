"""Audit utilities for cataloging personal injury assets."""

from __future__ import annotations

from typing import Dict, List

from packs.personal_injury import config, knowledge
from packs.personal_injury.knowledge import discovery_bank
from packs.personal_injury.schema import required_fields
from packs.personal_injury.workflows import PHASES
from packs.personal_injury.knowledge.negotiation_playbooks import NEGOTIATION_STEPS


def catalog_assets() -> Dict[str, List[str]]:
    """Return a catalog of variables, templates, automations, and knowledge assets."""

    documents = {key: cfg.title for key, cfg in config.DOCUMENTS.items()}
    knowledge_assets = {
        "fact_patterns": list(knowledge.FACT_PATTERNS.keys()),
        "negotiation_playbooks": list(NEGOTIATION_STEPS.keys()),
        "discovery_requests": {
            "interrogatories": discovery_bank.BASE_INTERROGATORIES,
            "requests_for_production": discovery_bank.BASE_DOCUMENT_REQUESTS,
            "requests_for_admission": discovery_bank.BASE_ADMISSION_REQUESTS,
        },
    }
    return {
        "documents": documents,
        "phases": {name: [doc.key for doc in plan.documents] for name, plan in PHASES.items()},
        "knowledge_assets": knowledge_assets,
        "schema_required": required_fields(),
        "analytics_tags": sorted({tag for cfg in config.DOCUMENTS.values() for tag in cfg.tags}),
    }
