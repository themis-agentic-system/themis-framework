"""Negotiation and scenario playbooks."""

from __future__ import annotations

from typing import Dict, List

NEGOTIATION_STEPS: Dict[str, List[str]] = {
    "intake": [
        "Confirm insurance coverage",
        "Collect medical authorizations",
        "Schedule recorded statement (if appropriate)",
    ],
    "pre_suit": [
        "Send policy limit demand",
        "Prepare mediation package",
        "Update lien information",
    ],
    "litigation": [
        "Evaluate comparative negligence arguments",
        "Consider Rule 68 offer",
        "Update trial budget",
    ],
}

TOPIC_CHECKLISTS: Dict[str, List[str]] = {
    "deposition": [
        "Background and employment",
        "Incident chronology",
        "Medical treatment history",
        "Prior claims or injuries",
        "Damages and impact",
    ],
    "mediation": [
        "Evaluation of liability",
        "Damages model",
        "Insurance coverage",
        "Settlement authority",
    ],
}


def negotiation_steps(phase: str) -> List[str]:
    return NEGOTIATION_STEPS.get(phase, [])


def topic_checklist(topic: str) -> List[str]:
    return TOPIC_CHECKLISTS.get(topic, [])


__all__ = ["NEGOTIATION_STEPS", "TOPIC_CHECKLISTS", "negotiation_steps", "topic_checklist"]
