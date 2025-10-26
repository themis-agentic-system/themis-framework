"""Intake memo generator."""

from __future__ import annotations

from textwrap import dedent

from packs.personal_injury.generators.base import BaseGenerator, Section


class IntakeMemoGenerator(BaseGenerator):
    template_name = "Intake Memo"

    def sections(self):
        yield Section(
            "Client Overview",
            dedent(
                f"""
                Client: {self.party_by_role('plaintiff')}
                Opposing Party: {self.party_by_role('defendant')}
                Jurisdiction: {self.matter.metadata.jurisdiction}
                Cause of Action: {self.matter.metadata.cause_of_action or 'Unknown'}
                Phase: {self.matter.metadata.phase or 'Intake'}
                """
            ).strip(),
        )
        yield Section(
            "Incident Summary",
            self.matter.fact_pattern.incident_description or "No description provided.",
        )
        yield Section("Key Dates", self.format_timeline())
        yield Section(
            "Insurance Coverage",
            "\n".join(
                f"- {policy.carrier} ({policy.coverage_limits or 'limits unknown'})"
                for policy in self.matter.insurance
            )
            or "No insurance data provided.",
        )
        yield Section(
            "Action Items",
            "\n".join(
                f"- {deadline.name} due {deadline.due.isoformat()} ({deadline.description or 'no notes'})"
                for deadline in self.matter.deadlines
            )
            or "No deadlines captured.",
        )
