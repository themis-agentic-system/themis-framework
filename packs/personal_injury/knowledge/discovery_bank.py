"""Discovery question bank."""

from __future__ import annotations

from packs.personal_injury.schema import PersonalInjuryMatter

BASE_INTERROGATORIES: list[str] = [
    "Identify all persons who witnessed the incident.",
    "Describe with specificity the actions you took immediately prior to the incident.",
    "State all facts supporting any contention that Plaintiff was negligent.",
]

BASE_DOCUMENT_REQUESTS: list[str] = [
    "All photographs, videos, or diagrams depicting the incident scene.",
    "All insurance policies that may provide coverage for the claims alleged.",
    "All documents supporting any affirmative defense asserted.",
]

BASE_ADMISSION_REQUESTS: list[str] = [
    "Admit that Defendant was operating the vehicle involved in the collision.",
    "Admit that Plaintiff sustained injuries as a result of the incident.",
    "Admit that Plaintiff incurred medical expenses following the incident.",
]


def interrogatories(matter: PersonalInjuryMatter) -> list[str]:
    base = list(BASE_INTERROGATORIES)
    if matter.medical_providers:
        base.append("Identify all healthcare providers who treated Plaintiff for the injuries alleged.")
    return base


def document_requests(matter: PersonalInjuryMatter) -> list[str]:
    return list(BASE_DOCUMENT_REQUESTS)


def admission_requests(matter: PersonalInjuryMatter) -> list[str]:
    return list(BASE_ADMISSION_REQUESTS)
