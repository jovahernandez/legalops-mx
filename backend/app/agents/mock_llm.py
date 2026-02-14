"""
Mock LLM provider.

Returns deterministic responses per agent type.
Drop-in interface for replacing with Anthropic/OpenAI later.
"""

from typing import Any


class MockLLMProvider:
    """
    Interface:
        provider.generate(agent_name, prompt, context) -> str

    Replace this class with AnthropicProvider or OpenAIProvider
    to connect to real models.
    """

    def generate(self, agent_name: str, prompt: str, context: dict[str, Any] | None = None) -> str:
        handler = MOCK_RESPONSES.get(agent_name, _default_response)
        return handler(prompt, context or {})


# ---------------------------------------------------------------------------
# Per-agent mock response generators
# ---------------------------------------------------------------------------

def _intake_specialist(prompt: str, ctx: dict) -> str:
    case_type = ctx.get("case_type", "unknown")
    return (
        f"[MOCK] Intake analysis complete for case type: {case_type}.\n"
        f"Classification: {case_type}\n"
        f"Urgency: medium (no immediate court dates detected)\n"
        f"Missing info: [date_of_birth, country_of_origin, current_status]\n"
        f"Documents needed: [government_id, relevant_notices]\n"
        f"Next step: Schedule consultation with attorney for case evaluation.\n"
        f"NOTE: This is an automated summary – requires attorney review before any action."
    )


def _tax_solutions(prompt: str, ctx: dict) -> str:
    return (
        "[MOCK] Tax case preliminary summary:\n"
        "- Tax years in question: [needs input]\n"
        "- Notice type: [needs input – CP2000, CP501, etc.]\n"
        "- Estimated liability: [needs CPA review]\n"
        "- Missing documents: [IRS notices, W-2s/1099s, prior returns]\n"
        "- Recommendation for human review: Evaluate for OIC, installment agreement, or CNC.\n"
        "NOTE: No tax advice provided. All determinations require licensed CPA/EA review."
    )


def _paralegal_ops(prompt: str, ctx: dict) -> str:
    return (
        "[MOCK] Paralegal task list generated:\n"
        "1. Send document request email to client (template: DOC_REQ_01)\n"
        "2. Prepare filing checklist for jurisdiction\n"
        "3. Schedule follow-up call in 3 business days\n"
        "4. Verify court/county filing requirements (NOTE: varies by county)\n"
        "5. Prepare draft communication for attorney review\n"
        "NOTE: Filing requirements are general. Verify with specific court clerk."
    )


def _client_assistant(prompt: str, ctx: dict) -> str:
    return (
        "[MOCK] Client status update:\n"
        "- Your case is currently: in review\n"
        "- Documents pending: [government_id]\n"
        "- Next appointment: [pending scheduling]\n"
        "- Action items for you: Upload missing documents, confirm contact info\n"
        "NOTE: For legal questions, please speak with your assigned attorney."
    )


def _interpreter_coordinator(prompt: str, ctx: dict) -> str:
    language = ctx.get("language", "Spanish")
    modality = ctx.get("modality", "virtual")
    return (
        f"[MOCK] Interpreter coordination:\n"
        f"- Language requested: {language}\n"
        f"- Modality: {modality}\n"
        f"- Availability check: [simulated – 3 interpreters available]\n"
        f"- Suggested slot: Next available business day, 10:00 AM\n"
        f"- Confirmation status: pending\n"
        f"NOTE: This is scheduling coordination only. No legal interpretation provided."
    )


def _mx_divorce_intake(prompt: str, ctx: dict) -> str:
    return (
        "[MOCK] Divorcio incausado – intake summary:\n"
        "- Jurisdicción: México\n"
        "- Tipo: Divorcio incausado (unilateral, sin expresión de causa)\n"
        "- Documentos requeridos: [acta_matrimonio, identificación_oficial, comprobante_domicilio, CURP]\n"
        "- Datos faltantes: [domicilio_conyugal, régimen_patrimonial, hijos_menores]\n"
        "- Siguiente paso: Revisión por licenciado(a) antes de preparar demanda.\n"
        "NOTA: Este es un resumen operativo. NO constituye asesoría legal."
    )


def _default_response(prompt: str, ctx: dict) -> str:
    return (
        "[MOCK] Agent processing complete.\n"
        "Input received and analyzed. Output requires human review.\n"
        "NOTE: This is a placeholder response from the mock LLM."
    )


MOCK_RESPONSES: dict[str, Any] = {
    "intake_specialist": _intake_specialist,
    "tax_solutions_assistant": _tax_solutions,
    "paralegal_ops_assistant": _paralegal_ops,
    "client_personal_assistant": _client_assistant,
    "interpreter_coordinator": _interpreter_coordinator,
    "mx_divorce_intake": _mx_divorce_intake,
}
