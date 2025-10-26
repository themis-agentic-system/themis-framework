"""LLM client for interacting with language models (Anthropic Claude).

The real application talks to Anthropic's Claude models. For the purposes of
our open-source test environment we still need the orchestration pipeline to
run even when no API key is available. This module therefore provides a client
that operates in two modes:

* When an ``ANTHROPIC_API_KEY`` is available, requests are proxied to the
  official Anthropic SDK.
* Otherwise, the client falls back to a deterministic stub that heuristically
  extracts information from the supplied prompts. The stub never performs
  network operations but mirrors the shape of the responses expected by the
  rest of the system.
"""

from __future__ import annotations

import ast
import json
import logging
import os
import re
from collections.abc import Iterable
from typing import Any

from anthropic import Anthropic
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger("themis.llm_client")


class LLMClient:
    """Wrapper for Anthropic Claude API with structured output support."""

    def __init__(self, api_key: str | None = None, model: str = "claude-3-5-sonnet-20241022"):
        """Initialise the client.

        Args:
            api_key: Anthropic API key. If ``None`` the environment variable
                ``ANTHROPIC_API_KEY`` is consulted.
            model: Claude model to use when the API key is present.
        """

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self._stub_mode = not self.api_key
        self.client = None if self._stub_mode else Anthropic(api_key=self.api_key)

    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _call_anthropic_api(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        max_tokens: int,
    ) -> str:
        """Call Anthropic API with retry logic.

        Retries up to 3 times with exponential backoff (2s, 4s, 8s).
        This handles transient network errors and rate limiting gracefully.
        """
        logger.debug(f"Calling Anthropic API (model: {self.model}, max_tokens: {max_tokens})")
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
        )
        content = response.content[0].text if response.content else ""
        logger.debug(f"Received response from Anthropic API ({len(content)} chars)")
        return content

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, Any] | None = None,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Generate a structured JSON response from the LLM.

        Automatically retries on failure with exponential backoff.
        """
        if self._stub_mode:
            return self._generate_structured_stub(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_format=response_format,
                max_tokens=max_tokens,
            )

        messages = [{"role": "user", "content": user_prompt}]

        if response_format:
            schema_instruction = (
                "\n\nYou MUST respond with valid JSON matching this schema:\n"
                f"{json.dumps(response_format, indent=2)}"
            )
            system_prompt = system_prompt + schema_instruction

        content = await self._call_anthropic_api(system_prompt, messages, max_tokens)

        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)
            return {"response": content}
        except json.JSONDecodeError:
            return {"response": content}

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> str:
        """Generate a plain-text response from the LLM.

        Automatically retries on failure with exponential backoff.
        """
        if self._stub_mode:
            return self._generate_text_stub(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=max_tokens,
            )

        messages = [{"role": "user", "content": user_prompt}]
        return await self._call_anthropic_api(system_prompt, messages, max_tokens)

    # ------------------------------------------------------------------
    # Stub implementation helpers
    # ------------------------------------------------------------------

    def _generate_structured_stub(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, Any] | None,
        max_tokens: int,
    ) -> dict[str, Any]:
        if not response_format:
            return {
                "response": self._generate_text_stub(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_tokens=max_tokens,
                )
            }

        keys = set(response_format.keys())

        if {"summary", "key_facts", "dates", "parties_mentioned"}.issubset(keys):
            return self._stub_document_parse(user_prompt)
        if "issues" in keys:
            return {"issues": self._stub_issue_spotter(user_prompt)}
        if {
            "objectives",
            "actions",
            "positions",
            "leverage_points",
            "proposed_concessions",
            "contingencies",
            "assumptions",
        }.issubset(keys):
            return self._stub_strategy_template(user_prompt)
        if {"confidence", "weaknesses", "evidentiary_gaps", "unknowns", "potential_problems"}.issubset(keys):
            return self._stub_risk_assessment(user_prompt)

        result: dict[str, Any] = {}
        for key, template in response_format.items():
            if isinstance(template, dict):
                result[key] = {}
            elif isinstance(template, list):
                result[key] = []
            else:
                result[key] = ""
        return result

    def _generate_text_stub(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
    ) -> str:
        context = self._extract_line(user_prompt, "Matter Context:") or "the presented matter"
        parties = self._extract_line(user_prompt, "Parties:")
        party_sentence = f"The parties involved are {parties}." if parties else ""

        issue_lines = self._extract_bullets(user_prompt, "Legal Issues Identified:")
        if issue_lines:
            issues_sentence = f"Key legal issues include {self._natural_join(issue_lines)}."
        else:
            issues_sentence = "Key legal issues will require further investigation."

        authorities = self._extract_bullets(user_prompt, "Authorities:")
        if authorities:
            authorities_sentence = (
                f"Supporting authorities such as {self._natural_join(authorities)} guide the analysis."
            )
        else:
            authorities_sentence = "No authorities were supplied, so additional research is required."

        follow_up_sentence = (
            "Further factual development should focus on resolving open questions and strengthening the evidentiary record."
        )

        paragraphs = [
            f"The matter concerns {context}. {party_sentence}".strip(),
            issues_sentence,
            authorities_sentence,
            follow_up_sentence,
        ]

        return "\n\n".join(paragraph for paragraph in paragraphs if paragraph)

    def _stub_document_parse(self, user_prompt: str) -> dict[str, Any]:
        content = self._extract_section(
            user_prompt,
            "Document Content:",
            stop_markers=("Please provide",),
        )
        sentences = self._split_sentences(content)
        summary = " ".join(sentences[:2]).strip()
        if not summary and content:
            summary = content[:200].strip()

        key_facts = self._dedupe([sentence.strip() for sentence in sentences[:3] if sentence.strip()])
        if not key_facts and content:
            key_facts = [segment.strip() for segment in content.splitlines() if segment.strip()][:3]

        dates = self._dedupe(re.findall(r"\d{4}-\d{2}-\d{2}", content))
        parties_line = self._extract_line(user_prompt, "Parties:")
        parties = []
        if parties_line:
            parties = self._dedupe(
                [segment.strip() for segment in re.split(r",| and ", parties_line) if segment.strip()]
            )

        return {
            "summary": summary or "Summary unavailable from document stub.",
            "key_facts": key_facts,
            "dates": dates,
            "parties_mentioned": parties,
        }

    def _stub_issue_spotter(self, user_prompt: str) -> list[dict[str, Any]]:
        text = user_prompt.lower()
        sentences = self._split_sentences(user_prompt)

        def issue_for(
            keyword: str,
            *,
            label: str,
            area: str,
            fact_keywords: Iterable[str],
            strength: str = "moderate",
        ) -> dict[str, Any] | None:
            if keyword not in text:
                return None
            facts = [
                sentence.strip()
                for sentence in sentences
                if any(token in sentence.lower() for token in fact_keywords)
            ]
            if not facts:
                facts = ["Referenced facts in provided materials."]
            return {
                "issue": label,
                "area_of_law": area,
                "facts": self._dedupe(facts)[:3],
                "strength": strength,
            }

        mappings = [
            ("breach", "Breach of contract", "Contract", ["breach", "contract", "deliver"], "strong"),
            ("neglig", "Negligence", "Tort", ["neglig", "injur", "collision", "fail"], "strong"),
            ("damage", "Damages assessment", "Damages", ["damage", "loss", "therapy", "income"], "moderate"),
            ("settlement", "Settlement posture", "Negotiation", ["settlement", "offer", "demand"], "moderate"),
        ]

        issues: list[dict[str, Any]] = []
        for keyword, label, area, fact_keywords, strength in mappings:
            issue = issue_for(
                keyword,
                label=label,
                area=area,
                fact_keywords=fact_keywords,
                strength=strength,
            )
            if issue:
                issues.append(issue)

        if not issues:
            first_sentence = sentences[0].strip() if sentences else "Additional facts are required to identify issues."
            issues.append(
                {
                    "issue": "Further issue spotting required",
                    "area_of_law": "General",
                    "facts": [first_sentence],
                    "strength": "unknown",
                }
            )

        return issues[:5]

    def _stub_strategy_template(self, user_prompt: str) -> dict[str, Any]:
        goals_raw = self._extract_line(user_prompt, "Client Goals:")
        goals: dict[str, Any] = {}
        if goals_raw:
            try:
                goals = ast.literal_eval(goals_raw)
            except (SyntaxError, ValueError):
                pass

        key_facts = self._extract_bullets(user_prompt, "Key Facts:")
        legal_issues = self._extract_bullets(user_prompt, "Legal Issues:")

        opening_position = goals.get("settlement") or goals.get("opening")
        fallback_position = goals.get("fallback") or goals.get("minimum")

        objectives = (
            goals.get("settlement")
            or (legal_issues[0] if legal_issues else None)
            or "Advance the client's negotiating posture"
        )

        actions = [
            "Prepare negotiation brief highlighting the strongest liability facts.",
            "Engage opposing counsel with a settlement framework anchored to the client's objectives.",
        ]
        if key_facts:
            actions.append(f"Emphasise: {key_facts[0]}")
        actions.append("Outline follow-up evidence needed to solidify damages claims.")

        positions = {
            "opening": opening_position or objectives,
            "ideal": goals.get("ideal") or opening_position or objectives,
            "minimum": goals.get("minimum") or fallback_position or "Secure meaningful monetary recovery",
            "fallback": fallback_position or "Escalate to litigation if negotiations stall",
        }

        leverage_points = key_facts[:2] if key_facts else legal_issues[:2]
        if not leverage_points:
            leverage_points = ["Well-documented liability narrative"]

        concessions = []
        if goals.get("fallback"):
            concessions.append(f"Consider fallback outcome of {goals['fallback']}")
        concessions.append("Remain flexible on payment structure if headline value is protected.")

        contingencies = [
            "Coordinate with trial team should negotiations fail to progress.",
            "Revisit settlement authority upon receipt of new information.",
        ]

        assumptions = [
            "Opposing counsel is open to early dialogue.",
            "Client can rapidly supply supplemental documentation when requested.",
        ]

        return {
            "objectives": objectives,
            "actions": self._dedupe(actions),
            "positions": positions,
            "leverage_points": self._dedupe(leverage_points),
            "proposed_concessions": self._dedupe(concessions),
            "contingencies": contingencies,
            "assumptions": assumptions,
        }

    def _stub_risk_assessment(self, user_prompt: str) -> dict[str, Any]:
        issues = self._extract_bullets(user_prompt, "Legal Issues:")
        key_facts = self._extract_bullets(user_prompt, "Key Facts:")

        weaknesses = [
            "Need to substantiate damages with updated records.",
            "Monitor for comparative fault allegations from the defence.",
        ]
        evidentiary_gaps = ["Outstanding discovery on economic losses."]
        if key_facts:
            evidentiary_gaps.append(f"Corroborate: {key_facts[-1]}")

        unknowns = ["Awaiting opposing counsel's position on liability."]
        if issues:
            unknowns.append("Assess strength of secondary issues through further investigation.")

        potential_problems = [
            "Delays in treatment or document production could undermine leverage.",
        ]

        return {
            "confidence": 68,
            "weaknesses": self._dedupe(weaknesses),
            "evidentiary_gaps": self._dedupe(evidentiary_gaps),
            "unknowns": self._dedupe(unknowns),
            "potential_problems": potential_problems,
        }

    # ------------------------------------------------------------------
    # Utility helpers for stub mode
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_line(text: str, header: str) -> str:
        prefix = header.strip()
        for raw_line in text.splitlines():
            stripped = raw_line.strip()
            if stripped.startswith(prefix):
                remainder = stripped[len(prefix) :].lstrip()
                if remainder.startswith(":"):
                    remainder = remainder[1:].strip()
                return remainder
        return ""

    @staticmethod
    def _extract_section(
        text: str,
        header: str,
        *,
        stop_markers: tuple[str, ...] = (),
    ) -> str:
        lines = text.splitlines()
        capture = False
        collected: list[str] = []
        for raw_line in lines:
            stripped = raw_line.strip()
            if not capture:
                if stripped.startswith(header):
                    capture = True
                continue
            if stop_markers and any(marker in stripped for marker in stop_markers):
                break
            collected.append(raw_line.rstrip())
        return "\n".join(collected).strip()

    @staticmethod
    def _extract_bullets(text: str, header: str) -> list[str]:
        lines = text.splitlines()
        capture = False
        bullets: list[str] = []
        for raw_line in lines:
            stripped = raw_line.strip()
            if not capture:
                if stripped.startswith(header):
                    capture = True
                continue
            if not stripped:
                break
            if stripped.startswith("-") or stripped.startswith("•"):
                bullet = stripped.lstrip("-• ").strip()
                if bullet:
                    bullets.append(bullet)
            elif bullets:
                bullets[-1] = f"{bullets[-1]} {stripped}".strip()
        return LLMClient._dedupe(bullets)

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        fragments = re.split(r"(?<=[.!?])\s+", text.strip()) if text else []
        return [fragment.strip() for fragment in fragments if fragment.strip()]

    @staticmethod
    def _dedupe(items: Iterable[Any]) -> list[Any]:
        seen: set[Any] = set()
        result: list[Any] = []
        for item in items:
            marker = json.dumps(item, sort_keys=True) if isinstance(item, (dict, list)) else item
            if marker in seen:
                continue
            seen.add(marker)
            result.append(item)
        return result

    @staticmethod
    def _natural_join(items: Iterable[str]) -> str:
        values = [item.strip().rstrip(".") for item in items if item.strip()]
        if not values:
            return ""
        if len(values) == 1:
            return values[0]
        if len(values) == 2:
            return " and ".join(values)
        return ", ".join(values[:-1]) + ", and " + values[-1]


# Global singleton for easy access
_llm_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Get or create the global LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def set_llm_client(client: LLMClient) -> None:
    """Set the global LLM client instance (useful for testing)."""
    global _llm_client
    _llm_client = client
