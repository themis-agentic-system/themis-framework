"""Jury instruction generator."""

from __future__ import annotations

from packs.personal_injury.generators.base import BaseGenerator, Section
from packs.personal_injury.rules import jury_instructions_for


class JuryInstructionGenerator(BaseGenerator):
    template_name = "Jury Instructions"

    def sections(self):
        instructions = jury_instructions_for(self.matter)
        body = "\n".join(f"- {instruction}" for instruction in instructions) or "No instructions available."
        yield Section("Proposed Instructions", body)
