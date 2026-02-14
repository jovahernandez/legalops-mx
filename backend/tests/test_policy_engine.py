"""Test: policy engine blocks legal-advice-like output."""

from app.agents.policy_engine import PolicyEngine


def test_policy_blocks_legal_advice_english():
    engine = PolicyEngine()

    # Should block: directive to file
    result = engine.check("You should file Form I-130 immediately.")
    assert result.is_blocked is True
    assert "UPL_DETECTED" in result.flags

    # Should block: recommending legal action
    result = engine.check("I recommend filing a lawsuit against the agency.")
    assert result.is_blocked is True

    # Should block: guaranteeing outcomes
    result = engine.check("I can guarantee approval of your application.")
    assert result.is_blocked is True

    # Should block: impersonating attorney
    result = engine.check("As your attorney, here is my legal advice.")
    assert result.is_blocked is True

    # Should block: assessing merits
    result = engine.check("You have a strong case for asylum.")
    assert result.is_blocked is True


def test_policy_blocks_legal_advice_spanish():
    engine = PolicyEngine()

    # Should block: directive in Spanish
    result = engine.check("Debes presentar tu demanda antes del viernes.")
    assert result.is_blocked is True

    # Should block: recommendation in Spanish
    result = engine.check("Te recomiendo demandar al empleador.")
    assert result.is_blocked is True

    # Should block: impersonating in Spanish
    result = engine.check("Como tu abogado, te digo que hagas esto.")
    assert result.is_blocked is True


def test_policy_allows_operational_text():
    engine = PolicyEngine()

    # Should NOT block: operational/factual
    result = engine.check("Your documents have been received. Our team will review them.")
    assert result.is_blocked is False

    result = engine.check("Please upload your identification document.")
    assert result.is_blocked is False

    result = engine.check("Your appointment is scheduled for Monday at 10 AM.")
    assert result.is_blocked is False

    result = engine.check("Missing documents: birth certificate, passport copy.")
    assert result.is_blocked is False


def test_policy_check_and_annotate():
    engine = PolicyEngine()

    output = {
        "case_packet": "You should file Form I-485 now.",
        "next_actions": ["Review documents"],
    }

    annotated = engine.check_and_annotate(output)
    assert "compliance_flags" in annotated
    assert len(annotated["compliance_flags"]) > 0
    assert annotated["_policy_status"] == "BLOCKED – requires human review"


def test_policy_annotate_clean_output():
    engine = PolicyEngine()

    output = {
        "case_packet": "Case received. Pending document review.",
        "next_actions": ["Send document request email"],
    }

    annotated = engine.check_and_annotate(output)
    assert annotated.get("compliance_flags") is None or len(annotated.get("compliance_flags", [])) == 0
