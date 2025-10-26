"""Document generators for the personal injury pack."""

from .answer import AnswerGenerator
from .complaint import ComplaintGenerator
from .demand import DemandLetterGenerator
from .deposition import DepositionOutlineGenerator
from .discovery import DiscoveryGenerator
from .intake import IntakeMemoGenerator
from .jury import JuryInstructionGenerator
from .lists import WitnessExhibitListGenerator
from .mediation import MediationBriefGenerator
from .settlement import SettlementAgreementGenerator
from .trial import TrialBriefGenerator

__all__ = [
    "AnswerGenerator",
    "ComplaintGenerator",
    "DemandLetterGenerator",
    "DepositionOutlineGenerator",
    "DiscoveryGenerator",
    "IntakeMemoGenerator",
    "JuryInstructionGenerator",
    "MediationBriefGenerator",
    "SettlementAgreementGenerator",
    "TrialBriefGenerator",
    "WitnessExhibitListGenerator",
]
