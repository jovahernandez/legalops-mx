"""
OpenAI LLM provider.

Drop-in replacement for MockLLMProvider.
Falls back to mock if OPENAI_API_KEY is not set.
"""

import json
from typing import Any

from app.config import settings


class OpenAIProvider:
    """
    Interface:
        provider.generate(agent_name, prompt, context) -> str
        provider.generate_prepkit(case_type, description, language) -> dict
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

    def generate_prepkit(self, case_type: str, description: str, language: str = "es") -> dict:
        """Generate a structured PrepKit with explicit JSON schema.

        Returns dict with keys:
            checklist_docs, questions_for_lawyer,
            next_steps_informational, disclaimer
        """
        if not self._client:
            # Fallback: return template-based defaults
            return self._mock_prepkit(case_type, language)

        lang_instruction = (
            "Responde COMPLETAMENTE en español." if language == "es"
            else "Respond ENTIRELY in English."
        )

        system_msg = (
            "You are a legal operations assistant for a platform in Mexico/LATAM. "
            "You NEVER provide legal advice. You produce document checklists and "
            "preparation guides ONLY. All outputs require review by a licensed "
            "professional (abogado con cédula profesional).\n\n"
            "STRICT PROHIBITIONS – never include ANY of the following:\n"
            "- Directives like 'haz demanda', 'procede X', 'presenta denuncia'\n"
            "- Recommendations to sue, file, appeal, or take specific legal action\n"
            "- Predictions about case outcomes ('vas a ganar', 'you will win')\n"
            "- Statements impersonating an attorney ('como tu abogado')\n"
            "- Any language that could constitute unauthorized practice of law\n\n"
            "Focus ONLY on:\n"
            "- Document checklists (what papers to gather)\n"
            "- Questions the person should ASK their lawyer\n"
            "- Informational next steps (e.g. 'schedule a consultation')\n\n"
            f"{lang_instruction}\n\n"
            "You MUST respond with valid JSON matching this exact schema:\n"
            "{\n"
            '  "checklist_docs": ["string array of documents to gather"],\n'
            '  "questions_for_lawyer": ["string array of questions to ask a lawyer"],\n'
            '  "next_steps_informational": ["string array of informational next steps"],\n'
            '  "disclaimer": "string disclaimer that this is NOT legal advice"\n'
            "}\n"
            "Return ONLY the JSON object, no markdown, no extra text."
        )

        user_msg = (
            f"Case type: {case_type}\n"
            f"Client description: {description}\n\n"
            "Generate a structured PrepKit for this person."
        )

        try:
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.3,
                max_tokens=1500,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content or "{}"
            parsed = json.loads(raw)

            # Validate expected keys exist
            return {
                "checklist_docs": parsed.get("checklist_docs", []),
                "questions_for_lawyer": parsed.get("questions_for_lawyer", []),
                "next_steps_informational": parsed.get("next_steps_informational", []),
                "disclaimer": parsed.get("disclaimer", self._default_disclaimer(language)),
            }
        except Exception:
            return self._mock_prepkit(case_type, language)

    def _mock_prepkit(self, case_type: str, language: str) -> dict:
        """Template-based fallback when OpenAI is unavailable."""
        if language == "es":
            return {
                "checklist_docs": [
                    "Identificación oficial (INE/pasaporte)",
                    "Comprobante de domicilio reciente",
                    "Documentos relacionados con su caso",
                ],
                "questions_for_lawyer": [
                    "¿Qué tipo de profesional debo consultar para mi caso?",
                    "¿Cuáles son los plazos legales relevantes?",
                    "¿Qué costos debo considerar?",
                ],
                "next_steps_informational": [
                    "Reúna los documentos de la lista",
                    "Agende una consulta con un abogado con cédula profesional",
                    "Prepare un resumen cronológico de los hechos",
                ],
                "disclaimer": self._default_disclaimer("es"),
            }
        return {
            "checklist_docs": [
                "Government-issued photo ID",
                "Proof of address",
                "Documents related to your case",
            ],
            "questions_for_lawyer": [
                "What type of professional should I consult?",
                "What are the relevant legal deadlines?",
                "What costs should I expect?",
            ],
            "next_steps_informational": [
                "Gather the documents on the checklist",
                "Schedule a consultation with a licensed attorney",
                "Prepare a chronological summary of events",
            ],
            "disclaimer": self._default_disclaimer("en"),
        }

    @staticmethod
    def _default_disclaimer(language: str) -> str:
        if language == "es":
            return (
                "Esta herramienta NO proporciona asesoría legal. "
                "Toda la información es orientativa y debe ser revisada por "
                "un profesional con cédula. No se crea relación abogado-cliente."
            )
        return (
            "This tool does NOT provide legal advice. All information is for "
            "informational purposes only and must be reviewed by a licensed "
            "professional. No attorney-client relationship is created."
        )
