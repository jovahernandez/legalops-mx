"""
OpenAI LLM provider.

Drop-in replacement for MockLLMProvider.
Falls back to mock if OPENAI_API_KEY is not set.
"""

from typing import Any

from app.config import settings


class OpenAIProvider:
    """
    Interface:
        provider.generate(agent_name, prompt, context) -> str
    """

    def __init__(self):
        self._client = None
        if settings.OPENAI_API_KEY:
            from openai import OpenAI
            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate(self, agent_name: str, prompt: str, context: dict[str, Any] | None = None) -> str:
        if not self._client:
            from app.agents.mock_llm import MockLLMProvider
            return MockLLMProvider().generate(agent_name, prompt, context)

        language = (context or {}).get("language", "es")
        lang_instruction = (
            "Responde en español." if language == "es"
            else "Respond in English."
        )

        system_msg = (
            "You are a legal operations assistant for a platform in Mexico/LATAM. "
            "You NEVER provide legal advice. You produce operational summaries, "
            "document checklists, and preparation guides. All outputs require "
            "review by a licensed professional (abogado con cédula). "
            f"{lang_instruction}"
        )

        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1500,
        )
        return response.choices[0].message.content or ""
