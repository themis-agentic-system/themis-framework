"""Settlement agreement generator."""

from __future__ import annotations

from textwrap import dedent

from packs.personal_injury.generators.base import BaseGenerator, Section


class SettlementAgreementGenerator(BaseGenerator):
    template_name = "Settlement Agreement"

    def sections(self):
        yield Section("Parties", self._parties())
        yield Section("Consideration", self._consideration())
        yield Section("Release", self._release())
        yield Section("Additional Terms", self._terms())

    def _parties(self) -> str:
        return dedent(
            f"""
            This settlement agreement is entered between {self.party_by_role('plaintiff')} ("Plaintiff") and {self.party_by_role('defendant')} ("Defendant").
            """
        ).strip()

    def _consideration(self) -> str:
        amount = self.matter.objectives.get("settlement") if isinstance(self.matter.objectives, dict) else None
        if isinstance(amount, (int, float)):
            consideration = f"Defendant shall pay Plaintiff ${amount:,.2f} in full satisfaction of the claims."
        else:
            consideration = "Defendant shall pay confidential consideration as agreed by the parties."
        return consideration

    def _release(self) -> str:
        return dedent(
            """
            Plaintiff releases and forever discharges Defendant and all related parties from any and all claims arising out of the incident described in the pleadings.
            This release includes known and unknown claims to the fullest extent permitted by law.
            """
        ).strip()

    def _terms(self) -> str:
        return dedent(
            """
            The parties agree to execute mutually agreeable dismissal documents, bear their own fees and costs, and cooperate on any lien resolution.
            Confidentiality and non-disparagement provisions apply unless prohibited by law.
            """
        ).strip()
