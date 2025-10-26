"""Witness and exhibit list generator."""

from __future__ import annotations

from packs.personal_injury.generators.base import BaseGenerator, Section


class WitnessExhibitListGenerator(BaseGenerator):
    template_name = "Witness & Exhibit Lists"

    def sections(self):
        yield Section("Witness List", self._witnesses())
        yield Section("Exhibit List", self._exhibits())

    def _witnesses(self) -> str:
        entries = []
        for witness in self.matter.fact_pattern.witnesses:
            entries.append(f"- {witness}")
        if not entries:
            entries.append("- Witnesses to be supplemented per rule disclosures.")
        return "\n".join(entries)

    def _exhibits(self) -> str:
        exhibits = []
        for idx, evidence in enumerate(self.matter.fact_pattern.evidence, start=1):
            exhibits.append(f"Exhibit {idx}: {evidence}")
        if not exhibits:
            exhibits.append("No exhibits identified.")
        return "\n".join(exhibits)
