"""Mediation brief generator."""

from __future__ import annotations

from textwrap import dedent

from packs.personal_injury.generators.base import BaseGenerator, Section
from packs.personal_injury.rules import comparative_fault_apportionment


class MediationBriefGenerator(BaseGenerator):
    template_name = "Mediation Brief"

    def sections(self):
        yield Section("Case Summary", self.matter.fact_pattern.incident_description)
        yield Section("Damages", self._damages_analysis())
        apportionment = comparative_fault_apportionment(self.matter)
        yield Section(
            "Liability Assessment",
            dedent(
                f"""
                Plaintiff fault allocation: {apportionment['plaintiff']}%
                Defendant fault allocation: {apportionment['defendant']}%
                """
            ).strip(),
        )
        yield Section("Settlement History", self._history())
        yield Section("Mediation Objectives", self._objectives())

    def _damages_analysis(self) -> str:
        damages = self.matter.damages
        total = damages.total()
        return dedent(
            f"""
            Total damages claimed: ${total:,.2f}
            Past specials: ${damages.specials:,.2f}
            General damages: ${damages.generals:,.2f}
            Future medical: ${damages.future_medical:,.2f}
            Wage loss: ${damages.wage_loss:,.2f}
            """
        ).strip()

    def _history(self) -> str:
        offers = self.matter.notes.get("negotiation_history") if isinstance(self.matter.notes, dict) else None
        if isinstance(offers, list):
            return "\n".join(f"- {entry}" for entry in offers)
        return "No prior settlement discussions recorded."

    def _objectives(self) -> str:
        objectives = []
        for key, label in (("settlement", "Target Number"), ("fallback", "Walk-away")):
            value = self.matter.objectives.get(key) if isinstance(self.matter.objectives, dict) else None
            if value is not None:
                if isinstance(value, (int, float)):
                    objectives.append(f"- {label}: ${value:,.2f}")
                else:
                    objectives.append(f"- {label}: {value}")
        if not objectives:
            objectives.append("- Preserve trial posture while exploring creative resolutions.")
        return "\n".join(objectives)
