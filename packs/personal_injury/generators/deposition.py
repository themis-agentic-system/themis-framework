"""Deposition outline generator."""

from __future__ import annotations

from packs.personal_injury.generators.base import BaseGenerator, Section
from packs.personal_injury.knowledge.negotiation_playbooks import topic_checklist


class DepositionOutlineGenerator(BaseGenerator):
    template_name = "Deposition Outline"

    def sections(self):
        yield Section("Goals", self._goals())
        yield Section("Background", self.format_timeline())
        yield Section("Key Topics", "\n".join(f"- {item}" for item in topic_checklist("deposition")))
        yield Section("Exhibits", self.list_evidence())

    def _goals(self) -> str:
        goals = []
        for key in ("liability", "damages", "impeachment"):
            if isinstance(self.matter.notes, dict) and key in self.matter.notes:
                goals.append(f"- {key.title()}: {self.matter.notes[key]}")
        if not goals:
            goals.append("- Establish chronology and admissions of liability.")
        return "\n".join(goals)
