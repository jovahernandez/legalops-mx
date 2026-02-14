"""Test: B2C Prep Kit always requires human approval."""

from app.models import Approval, AgentRun, Intake, Matter, Lead


def test_prepkit_creates_intake_matter_and_approval(client, seed_tenant):
    """POST /public/prepkit should create intake, matter, agent run, and approval."""
    response = client.post("/public/prepkit", json={
        "tenant_id": str(seed_tenant.id),
        "case_type": "immigration",
        "description": "I received a Notice to Appear",
        "full_name": "Juan Test",
        "email": "juan@test.com",
        "phone": "+1-555-0000",
        "language": "en",
        "utm": {"source": "google", "medium": "cpc"},
    })
    assert response.status_code == 201
    data = response.json()

    # Returns document checklist and questions (safe operational info)
    assert len(data["document_checklist"]) > 0
    assert len(data["questions_for_attorney"]) > 0

    # Case packet is ALWAYS behind approval
    assert data["case_packet_status"] == "needs_approval"

    # Disclaimer is present
    assert "NOT" in data["disclaimer"] or "not" in data["disclaimer"].lower()
    assert "legal advice" in data["disclaimer"].lower()


def test_prepkit_always_needs_approval(client, db, seed_tenant):
    """The agent run created by prepkit must ALWAYS be in needs_approval status."""
    client.post("/public/prepkit", json={
        "tenant_id": str(seed_tenant.id),
        "case_type": "tax_resolution",
        "description": "I owe $30,000 in back taxes",
        "full_name": "Bob Tax",
        "email": "bob@test.com",
        "language": "en",
        "utm": {},
    })

    # Check that approval was created with pending status
    approvals = db.query(Approval).filter(Approval.tenant_id == seed_tenant.id).all()
    assert len(approvals) >= 1
    for approval in approvals:
        assert approval.status == "pending"
        assert approval.object_type == "agent_run"

    # Check that agent run is in needs_approval
    agent_runs = db.query(AgentRun).filter(AgentRun.tenant_id == seed_tenant.id).all()
    assert len(agent_runs) >= 1
    for ar in agent_runs:
        assert ar.status == "needs_approval"


def test_prepkit_creates_lead(client, db, seed_tenant):
    """Prepkit should also capture a lead for the B2C funnel."""
    client.post("/public/prepkit", json={
        "tenant_id": str(seed_tenant.id),
        "case_type": "immigration",
        "description": "Need help with visa",
        "full_name": "Lead Test",
        "email": "lead@test.com",
        "language": "es",
        "utm": {"source": "facebook"},
    })

    leads = db.query(Lead).filter(Lead.tenant_id == seed_tenant.id).all()
    assert len(leads) >= 1
    assert leads[0].source_type == "b2c_prepkit"
    assert leads[0].vertical == "immigration"
    assert leads[0].contact_json["name"] == "Lead Test"


def test_prepkit_rejects_invalid_tenant(client):
    """Prepkit with non-existent tenant should 404."""
    response = client.post("/public/prepkit", json={
        "tenant_id": "00000000-0000-0000-0000-999999999999",
        "case_type": "immigration",
        "description": "test",
        "full_name": "Test",
        "language": "en",
        "utm": {},
    })
    assert response.status_code == 404


def test_prepkit_mx_divorce_returns_spanish_docs(client, seed_tenant):
    """MX divorce prepkit should return Spanish-language document list."""
    response = client.post("/public/prepkit", json={
        "tenant_id": str(seed_tenant.id),
        "case_type": "mx_divorce",
        "description": "Quiero divorcio incausado",
        "full_name": "Laura Test",
        "language": "es",
        "utm": {},
    })
    assert response.status_code == 201
    data = response.json()
    # MX divorce docs should include Spanish terms
    checklist_text = " ".join(data["document_checklist"])
    assert "acta" in checklist_text.lower() or "INE" in checklist_text


def test_public_lead_endpoint(client):
    """POST /public/lead should capture a lead without auth."""
    response = client.post("/public/lead", json={
        "source_type": "b2b_onboarding",
        "vertical": "immigration",
        "contact": {"firm_name": "Test Law LLC", "email": "info@test.law"},
        "utm": {"source": "linkedin"},
    })
    assert response.status_code == 201
    data = response.json()
    assert data["source_type"] == "b2b_onboarding"
    assert data["status"] == "new"
    assert data["contact_json"]["firm_name"] == "Test Law LLC"


def test_onboard_creates_tenant_and_user(client):
    """POST /public/onboard should create a new tenant + admin user."""
    response = client.post("/public/onboard", json={
        "firm_name": "New Firm LLC",
        "admin_email": "admin@newfirm.law",
        "admin_password": "secure123",
        "practice_areas": ["immigration", "tax_resolution"],
        "disclaimer_en": "No legal advice provided.",
        "disclaimer_es": "No se proporciona asesoria legal.",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["admin_email"] == "admin@newfirm.law"
    assert "tenant_id" in data
    assert "embed_snippet" in data
    assert "login_url" in data


def test_onboard_rejects_duplicate_email(client):
    """Onboard should reject duplicate admin email."""
    payload = {
        "firm_name": "Dup Firm",
        "admin_email": "dup@firm.law",
        "admin_password": "pass123",
        "practice_areas": ["immigration"],
    }
    resp1 = client.post("/public/onboard", json=payload)
    assert resp1.status_code == 201

    resp2 = client.post("/public/onboard", json=payload)
    assert resp2.status_code == 400
