"""Configuration registry for the personal injury practice pack."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Type

from packs.personal_injury.generators import (
    AnswerGenerator,
    ComplaintGenerator,
    DemandLetterGenerator,
    DepositionOutlineGenerator,
    DiscoveryGenerator,
    IntakeMemoGenerator,
    JuryInstructionGenerator,
    MediationBriefGenerator,
    SettlementAgreementGenerator,
    TrialBriefGenerator,
    WitnessExhibitListGenerator,
)
from packs.personal_injury.generators.base import BaseGenerator
from packs.personal_injury.schema import PersonalInjuryMatter

PACK_ANALYTICS_TAG = "pack:personal_injury"


@dataclass(slots=True)
class DocumentConfig:
    key: str
    title: str
    generator: Type["BaseGenerator"]
    phase: str
    tags: List[str]


DOCUMENTS: Dict[str, DocumentConfig] = {
    "intake_memo": DocumentConfig(
        key="intake_memo",
        title="Case Intake Memorandum",
        generator=IntakeMemoGenerator,
        phase="intake",
        tags=[PACK_ANALYTICS_TAG, "doc:intake_memo"],
    ),
    "demand_letter": DocumentConfig(
        key="demand_letter",
        title="Settlement Demand Letter",
        generator=DemandLetterGenerator,
        phase="pre_suit",
        tags=[PACK_ANALYTICS_TAG, "doc:demand_letter"],
    ),
    "complaint": DocumentConfig(
        key="complaint",
        title="Civil Complaint",
        generator=ComplaintGenerator,
        phase="litigation",
        tags=[PACK_ANALYTICS_TAG, "doc:complaint"],
    ),
    "answer": DocumentConfig(
        key="answer",
        title="Answer / Responsive Pleading",
        generator=AnswerGenerator,
        phase="litigation",
        tags=[PACK_ANALYTICS_TAG, "doc:answer"],
    ),
    "discovery": DocumentConfig(
        key="discovery",
        title="Written Discovery Package",
        generator=DiscoveryGenerator,
        phase="litigation",
        tags=[PACK_ANALYTICS_TAG, "doc:discovery"],
    ),
    "deposition_outline": DocumentConfig(
        key="deposition_outline",
        title="Deposition Outline",
        generator=DepositionOutlineGenerator,
        phase="litigation",
        tags=[PACK_ANALYTICS_TAG, "doc:deposition_outline"],
    ),
    "mediation_brief": DocumentConfig(
        key="mediation_brief",
        title="Mediation Statement",
        generator=MediationBriefGenerator,
        phase="adr",
        tags=[PACK_ANALYTICS_TAG, "doc:mediation_brief"],
    ),
    "trial_brief": DocumentConfig(
        key="trial_brief",
        title="Trial Brief",
        generator=TrialBriefGenerator,
        phase="trial",
        tags=[PACK_ANALYTICS_TAG, "doc:trial_brief"],
    ),
    "witness_exhibit_lists": DocumentConfig(
        key="witness_exhibit_lists",
        title="Witness & Exhibit Lists",
        generator=WitnessExhibitListGenerator,
        phase="trial",
        tags=[PACK_ANALYTICS_TAG, "doc:lists"],
    ),
    "jury_instructions": DocumentConfig(
        key="jury_instructions",
        title="Proposed Jury Instructions",
        generator=JuryInstructionGenerator,
        phase="trial",
        tags=[PACK_ANALYTICS_TAG, "doc:jury_instructions"],
    ),
    "settlement_agreement": DocumentConfig(
        key="settlement_agreement",
        title="Settlement Agreement",
        generator=SettlementAgreementGenerator,
        phase="adr",
        tags=[PACK_ANALYTICS_TAG, "doc:settlement_agreement"],
    ),
}


def build_generator(key: str, matter: PersonalInjuryMatter) -> BaseGenerator:
    config = DOCUMENTS[key]
    return config.generator(matter)


def available_documents(phase: str | None = None) -> List[DocumentConfig]:
    values = list(DOCUMENTS.values())
    if phase:
        values = [config for config in values if config.phase == phase]
    return sorted(values, key=lambda cfg: cfg.key)
