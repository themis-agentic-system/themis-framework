"""Damages calculator utility."""

from __future__ import annotations

from typing import Dict

from packs.personal_injury.schema import PersonalInjuryMatter


def damages_calculator(matter: PersonalInjuryMatter) -> Dict[str, float]:
    damages = matter.damages
    totals = {
        "specials": damages.specials,
        "generals": damages.generals,
        "wage_loss": damages.wage_loss,
        "future_medical": damages.future_medical,
        "punitive": damages.punitive,
        "total": damages.total(),
    }
    return totals
