"""Complaint generator built on shared schema."""

from __future__ import annotations

from textwrap import dedent

from packs.personal_injury.generators.base import BaseGenerator, Section
from packs.personal_injury.rules import jury_instructions_for, pleading_elements


class ComplaintGenerator(BaseGenerator):
    template_name = "Complaint"

    def sections(self):
        yield Section(
            "Caption",
            dedent(
                f"""
                IN THE {self.matter.metadata.venue or 'SUPERIOR'} COURT OF {self.matter.metadata.jurisdiction.upper()}
                {self.party_by_role('plaintiff')} v. {self.party_by_role('defendant')}
                """
            ).strip(),
        )
        yield Section(
            "Parties",
            "\n".join(
                f"- {party.role.title()}: {party.name} (counsel: {party.counsel or 'n/a'})"
                for party in self.matter.parties
            ),
        )
        yield Section("Jurisdiction & Venue", "\n".join(self._jurisdiction_paragraphs()))
        yield Section("Factual Allegations", self._facts())
        for count, elements in pleading_elements(self.matter).items():
            body = "\n".join(f"- {element}" for element in elements)
            yield Section(f"Cause of Action: {count}", body)
        yield Section("Damages", self._damages())
        instructions = jury_instructions_for(self.matter)
        if instructions:
            yield Section("Requested Jury Instructions", "\n".join(f"- {inst}" for inst in instructions))

    def _jurisdiction_paragraphs(self):
        return [
            f"This Court has jurisdiction because the incident occurred in {self.matter.metadata.jurisdiction}.",
            "Venue is proper because the parties reside or do business in this venue.",
        ]

    def _facts(self) -> str:
        parts = [self.matter.fact_pattern.incident_description]
        timeline = self.format_timeline()
        if timeline:
            parts.append("Timeline:\n" + timeline)
        evidence = self.list_evidence()
        if evidence:
            parts.append("Evidence:\n" + evidence)
        return "\n\n".join(filter(None, parts))

    def _damages(self) -> str:
        damages = self.matter.damages
        lines = [
            f"Special damages: ${damages.specials:,.2f}",
            f"General damages: ${damages.generals:,.2f}",
            f"Wage loss: ${damages.wage_loss:,.2f}",
            f"Future medical: ${damages.future_medical:,.2f}",
        ]
        if damages.punitive:
            lines.append(f"Punitive damages sought in the amount of ${damages.punitive:,.2f}.")
        return "\n".join(lines)
