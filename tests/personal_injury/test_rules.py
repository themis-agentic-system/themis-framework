from __future__ import annotations

from copy import deepcopy

from packs.personal_injury.knowledge.exemplar_filings import (
    exemplar_complaint_captions,
    key_authorities,
)
from packs.personal_injury.rules import (
    affirmative_defenses,
    comparative_fault_apportionment,
    damages_multiplier,
    jury_instructions_for,
    statute_of_limitations,
)
from packs.personal_injury.schema import load_matter


def test_unknown_jurisdiction_uses_dynamic_profile(sample_payload):
    payload = deepcopy(sample_payload)
    payload["matter"]["metadata"]["jurisdiction"] = "Wyoming"
    matter = load_matter(payload)

    limitation = statute_of_limitations(matter)
    assert limitation is not None

    instructions = jury_instructions_for(matter)
    assert instructions

    multiplier = damages_multiplier(matter)
    assert multiplier > 0

    fault = comparative_fault_apportionment(matter)
    assert set(fault) == {"plaintiff", "defendant"}

    defenses = affirmative_defenses(matter)
    assert isinstance(defenses, list)

    authorities = key_authorities("Wyoming")
    assert authorities

    caption = exemplar_complaint_captions("Wyoming")
    assert caption
