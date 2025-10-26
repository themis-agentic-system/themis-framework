"""Trial brief generator."""

from __future__ import annotations

from packs.personal_injury.generators.base import BaseGenerator, Section
from packs.personal_injury.knowledge.exemplar_filings import key_authorities


class TrialBriefGenerator(BaseGenerator):
    template_name = "Trial Brief"

    def sections(self):
        yield Section("Issues for Trial", self._issues())
        yield Section("Evidentiary Outline", self.list_evidence())
        yield Section("Witness Strategy", self._witness_strategy())
        yield Section(
            "Authorities",
            "\n".join(f"- {authority}" for authority in key_authorities(self.matter.metadata.jurisdiction)),
        )

    def _issues(self) -> str:
        issues = []
        for theory in self.matter.liability:
            issues.append(f"- Whether {self.party_by_role('defendant')} breached duties under {theory.name}.")
        if not issues:
            issues.append("- Liability and damages remain contested.")
        return "\n".join(issues)

    def _witness_strategy(self) -> str:
        witnesses = self.matter.fact_pattern.witnesses
        if witnesses:
            return "\n".join(f"- {witness}" for witness in witnesses)
        return "No witness list provided."
