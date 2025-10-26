"""Scenario and phase workflows for personal injury matters."""

from __future__ import annotations

from dataclasses import dataclass

from packs.personal_injury import config
from packs.personal_injury.knowledge.negotiation_playbooks import negotiation_steps
from packs.personal_injury.schema import PersonalInjuryMatter


@dataclass(slots=True)
class PhasePlan:
    name: str
    description: str
    documents: list[config.DocumentConfig]
    checklist: list[str]


PHASES: dict[str, PhasePlan] = {}


def _register_phase(phase: str, description: str, checklist: list[str]):
    PHASES[phase] = PhasePlan(
        name=phase,
        description=description,
        documents=config.available_documents(phase),
        checklist=checklist,
    )


_register_phase(
    "intake",
    "Initial fact gathering, conflict checks, and insurance discovery.",
    [
        "Confirm engagement and retainer.",
        "Collect client statements and photos.",
        "Request police reports and medical records.",
    ] + negotiation_steps("intake"),
)

_register_phase(
    "pre_suit",
    "Pre-litigation negotiation and demand preparation.",
    [
        "Finalize damages calculation.",
        "Serve policy limit demand with supporting exhibits.",
        "Calendar statute of limitations and pre-suit notice requirements.",
    ] + negotiation_steps("pre_suit"),
)

_register_phase(
    "litigation",
    "Active litigation including pleadings and discovery.",
    [
        "File complaint and serve defendants.",
        "Exchange written discovery and take depositions.",
        "Update case budget and evaluate settlement posture.",
    ] + negotiation_steps("litigation"),
)

_register_phase(
    "adr",
    "Alternative dispute resolution including mediation and settlement conferences.",
    [
        "Prepare mediation statement and exhibits.",
        "Coordinate attendee availability and authority.",
        "Draft settlement memorandum of understanding.",
    ],
)

_register_phase(
    "trial",
    "Trial preparation and presentation.",
    [
        "Draft motions in limine and trial brief.",
        "Finalize witness and exhibit lists.",
        "Prepare jury instructions and verdict form.",
    ],
)


def active_phase(matter: PersonalInjuryMatter) -> PhasePlan:
    phase = (matter.metadata.phase or "intake").lower()
    return PHASES.get(phase, PHASES["intake"])


def workflow_summary(matter: PersonalInjuryMatter) -> dict[str, list[str]]:
    plan = active_phase(matter)
    return {
        "phase": plan.name,
        "documents": [doc.title for doc in plan.documents],
        "checklist": plan.checklist,
    }
