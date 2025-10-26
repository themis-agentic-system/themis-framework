"""Knowledge assets supporting personal injury workflows."""

from .damages import damages_calculator
from .discovery_bank import admission_requests, document_requests, interrogatories
from .exemplar_filings import exemplar_complaint_captions, key_authorities
from .fact_patterns import FACT_PATTERNS
from .negotiation_playbooks import NEGOTIATION_STEPS, negotiation_steps, topic_checklist

__all__ = [
    "FACT_PATTERNS",
    "NEGOTIATION_STEPS",
    "admission_requests",
    "damages_calculator",
    "document_requests",
    "exemplar_complaint_captions",
    "interrogatories",
    "key_authorities",
    "negotiation_steps",
    "topic_checklist",
]
