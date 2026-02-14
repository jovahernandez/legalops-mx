"""
Policy Engine – Unauthorized Practice of Law (UPL) guard.

Scans text output for patterns that could constitute legal advice.
If detected, flags the output as BLOCKED and requires human review.
"""

import re
from dataclasses import dataclass, field


@dataclass
class PolicyCheckResult:
    is_blocked: bool = False
    flags: list[str] = field(default_factory=list)
    details: list[str] = field(default_factory=list)


# Patterns that suggest the system is giving legal advice
# Organized by language (EN + ES) since we serve US + MX
LEGAL_ADVICE_PATTERNS_EN = [
    (r"\byou should file\b", "Directive to file a legal document"),
    (r"\byou must file\b", "Directive to file a legal document"),
    (r"\bi recommend (filing|suing|demanding|petitioning)", "Recommending legal action"),
    (r"\byou should (sue|demand|petition|appeal|file)", "Advising specific legal action"),
    (r"\byour best (legal )?option is\b", "Prescribing legal strategy"),
    (r"\bfile form [A-Z0-9-]+\b", "Directing to file a specific form"),
    (r"\byou (have|need) a (strong|good|valid) case\b", "Assessing legal merits"),
    (r"\byou will (likely )?win\b", "Predicting legal outcomes"),
    (r"\bguarantee[ds]?\b.*\b(outcome|result|approval)\b", "Guaranteeing legal outcomes"),
    (r"\bas your (lawyer|attorney|legal counsel)\b", "Impersonating attorney"),
    (r"\bmy legal (advice|opinion|recommendation)\b", "Presenting as legal advice"),
    (r"\blegally (obligated|required|bound) to\b", "Stating legal obligations"),
]

LEGAL_ADVICE_PATTERNS_ES = [
    (r"\bdebes (presentar|demandar|apelar|solicitar)\b", "Aconsejando acción legal específica"),
    (r"\bte recomiendo (demandar|presentar|apelar)", "Recomendando acción legal"),
    (r"\bpresenta (el|la|los|las) (formulario|forma|demanda|solicitud)\b", "Dirigiendo a presentar documento legal"),
    (r"\btienes un (buen|fuerte) caso\b", "Evaluando méritos legales"),
    (r"\bcomo tu abogado\b", "Haciéndose pasar por abogado"),
    (r"\bmi consejo legal\b", "Presentando como consejo legal"),
    (r"\bestás legalmente obligado\b", "Afirmando obligaciones legales"),
    (r"\bvas a ganar\b", "Prediciendo resultado legal"),
]

ALL_PATTERNS = LEGAL_ADVICE_PATTERNS_EN + LEGAL_ADVICE_PATTERNS_ES


class PolicyEngine:
    """Checks agent output for unauthorized practice of law indicators."""

    def __init__(self, extra_patterns: list[tuple[str, str]] | None = None):
        self.patterns = ALL_PATTERNS.copy()
        if extra_patterns:
            self.patterns.extend(extra_patterns)

    def check(self, text: str) -> PolicyCheckResult:
        """Scan text for UPL patterns. Returns blocked=True if any match."""
        result = PolicyCheckResult()
        text_lower = text.lower()

        for pattern, description in self.patterns:
            if re.search(pattern, text_lower):
                result.is_blocked = True
                result.flags.append("UPL_DETECTED")
                result.details.append(f"Pattern matched: {description}")

        # Dedup flags
        result.flags = list(set(result.flags))
        return result

    def check_and_annotate(self, output: dict) -> dict:
        """Check all string fields in an agent output dict.

        Adds compliance_flags to the output if issues are found.
        """
        compliance_flags = []

        for key, value in output.items():
            if isinstance(value, str):
                check = self.check(value)
                if check.is_blocked:
                    compliance_flags.extend(
                        [f"{key}: {d}" for d in check.details]
                    )
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        check = self.check(item)
                        if check.is_blocked:
                            compliance_flags.extend(
                                [f"{key}[]: {d}" for d in check.details]
                            )

        if compliance_flags:
            output["compliance_flags"] = compliance_flags
            output["_policy_status"] = "BLOCKED – requires human review"

        return output
