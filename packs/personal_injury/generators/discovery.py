"""Written discovery generator."""

from __future__ import annotations

from textwrap import dedent

from packs.personal_injury.generators.base import BaseGenerator, Section
from packs.personal_injury.knowledge.discovery_bank import (
    admission_requests,
    document_requests,
    interrogatories,
)


class DiscoveryGenerator(BaseGenerator):
    template_name = "Discovery Package"

    def sections(self):
        yield Section("Instructions", self._instructions())
        yield Section("Definitions", self._definitions())
        yield Section(
            "Interrogatories",
            "\n".join(f"Interrogatory No. {idx+1}: {text}" for idx, text in enumerate(interrogatories(self.matter)))
            or "No interrogatories configured.",
        )
        yield Section(
            "Requests for Production",
            "\n".join(
                f"Request for Production No. {idx+1}: {text}" for idx, text in enumerate(document_requests(self.matter))
            )
            or "No production requests configured.",
        )
        yield Section(
            "Requests for Admission",
            "\n".join(
                f"Request for Admission No. {idx+1}: {text}" for idx, text in enumerate(admission_requests(self.matter))
            )
            or "No admission requests configured.",
        )

    def _instructions(self) -> str:
        return dedent(
            """
            Responding party shall answer separately and fully under oath within the time provided by the applicable rules.
            If an objection is made, identify the grounds and answer to the extent the request is not objectionable.
            """
        ).strip()

    def _definitions(self) -> str:
        return dedent(
            """
            "DOCUMENT" means any writing, electronic data, or tangible item in the possession, custody, or control of a party.
            "IDENTIFY" when used with respect to a person requires the name, address, phone number, and relationship to the parties.
            "INCIDENT" refers to the occurrence described in the pleadings giving rise to this action.
            """
        ).strip()
