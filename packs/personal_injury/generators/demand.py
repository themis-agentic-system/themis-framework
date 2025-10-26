"""Demand letter generator."""

from __future__ import annotations

from textwrap import dedent

from packs.personal_injury.generators.base import BaseGenerator, Section
from packs.personal_injury.rules import damages_multiplier, statute_of_limitations


class DemandLetterGenerator(BaseGenerator):
    template_name = "Demand Letter"

    def sections(self):
        damages_total = self.matter.damages.total()
        multiplier = damages_multiplier(self.matter)
        recommended = damages_total * multiplier if damages_total else 0
        yield Section(
            "Introduction",
            dedent(
                f"""
                This letter serves as a formal demand for settlement on behalf of {self.party_by_role('plaintiff')}.
                The incident occurred in {self.matter.metadata.jurisdiction} and gives rise to a {self.matter.metadata.cause_of_action or 'personal injury'} claim.
                """
            ).strip(),
        )
        yield Section("Liability", "\n".join(f"- {theory.name}: {', '.join(theory.facts)}" for theory in self.matter.liability) or "Liability facts pending.")
        yield Section(
            "Injuries and Treatment",
            "\n".join(
                f"- {injury.description} ({', '.join(injury.body_parts)})" for injury in self.matter.injuries
            )
            or "No injury details recorded.",
        )
        yield Section(
            "Medical Summary",
            "\n".join(
                f"- {provider.name}: {sum(record.balance or 0 for record in provider.records):,.2f}"
                for provider in self.matter.medical_providers
            )
            or "No medical billing data.",
        )
        yield Section(
            "Damages",
            dedent(
                f"""
                Specials: ${self.matter.damages.specials:,.2f}
                Generals: ${self.matter.damages.generals:,.2f}
                Wage Loss: ${self.matter.damages.wage_loss:,.2f}
                Future Medical: ${self.matter.damages.future_medical:,.2f}
                Punitive: ${self.matter.damages.punitive:,.2f}
                Total Claimed: ${damages_total:,.2f}
                Recommended Demand (multiplier {multiplier:.1f}): ${recommended:,.2f}
                """
            ).strip(),
        )
        sol = statute_of_limitations(self.matter)
        if sol:
            yield Section("Statute of Limitations", f"Claim must be filed by {sol.isoformat()}.")
        yield Section("Settlement Position", self._settlement_position())

    def _settlement_position(self) -> str:
        preferred = self.matter.objectives.get("settlement") if isinstance(self.matter.objectives, dict) else None
        fallback = self.matter.objectives.get("fallback") if isinstance(self.matter.objectives, dict) else None
        lines = [
            f"Demand: ${preferred:,.2f}" if isinstance(preferred, (int, float)) else f"Demand: {preferred or 'Not set'}",
            f"Lowest acceptable: ${fallback:,.2f}" if isinstance(fallback, (int, float)) else f"Lowest acceptable: {fallback or 'Not set'}",
        ]
        return "\n".join(lines)
