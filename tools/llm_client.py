"""LLM client for interacting with language models (Anthropic Claude)."""

from __future__ import annotations

import json
import os
from typing import Any

from anthropic import Anthropic


class LLMClient:
    """Wrapper for Anthropic Claude API with structured output support."""

    def __init__(self, api_key: str | None = None, model: str = "claude-3-5-sonnet-20241022"):
        """Initialize the LLM client.

        Args:
            api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var.
            model: The Claude model to use.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY must be set in environment or passed to constructor"
            )
        self.client = Anthropic(api_key=self.api_key)
        self.model = model

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, Any] | None = None,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Generate a structured JSON response from the LLM.

        Args:
            system_prompt: System instructions that define the agent's role and behavior.
            user_prompt: The user's request or the data to analyze.
            response_format: Optional JSON schema defining expected response structure.
            max_tokens: Maximum tokens to generate.

        Returns:
            Parsed JSON response from the LLM.
        """
        messages = [{"role": "user", "content": user_prompt}]

        # If response format is provided, add it to the system prompt
        if response_format:
            schema_instruction = (
                "\n\nYou MUST respond with valid JSON matching this schema:\n"
                f"{json.dumps(response_format, indent=2)}"
            )
            system_prompt = system_prompt + schema_instruction

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
        )

        # Extract text content
        content = response.content[0].text if response.content else ""

        # Try to parse as JSON
        try:
            # Look for JSON in the response (handles cases where LLM adds explanation)
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)
            else:
                # No JSON found, return as-is wrapped in a dict
                return {"response": content}
        except json.JSONDecodeError:
            # If parsing fails, return the raw content
            return {"response": content}

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> str:
        """Generate a text response from the LLM.

        Args:
            system_prompt: System instructions that define the agent's role and behavior.
            user_prompt: The user's request or the data to analyze.
            max_tokens: Maximum tokens to generate.

        Returns:
            Text response from the LLM.
        """
        messages = [{"role": "user", "content": user_prompt}]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
        )

        # Extract text content
        return response.content[0].text if response.content else ""


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
