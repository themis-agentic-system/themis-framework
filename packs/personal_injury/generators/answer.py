"""Answer and responsive pleading generator."""

from __future__ import annotations

from packs.personal_injury.generators.base import BaseGenerator, Section
from packs.personal_injury.rules import affirmative_defenses


class AnswerGenerator(BaseGenerator):
    template_name = "Answer"

    def sections(self):
        yield Section(
            "General Denial",
            "Defendant denies each and every allegation not expressly admitted herein and demands strict proof thereof.",
        )
        yield Section(
            "Admissions",
            "\n".join(self._admissions()) or "No affirmative admissions at this stage.",
        )
        defenses = affirmative_defenses(self.matter)
        if defenses:
            yield Section("Affirmative Defenses", "\n".join(f"- {defense}" for defense in defenses))

    def _admissions(self):
        return [
            f"Admits jurisdiction in {self.matter.metadata.jurisdiction}.",
            "Admits identity of parties as alleged.",
        ]
