"""Test: public intake creates intake, then converts to matter."""

import uuid


def test_public_intake_creates_intake(client, seed_tenant):
    """Public endpoint should create an intake without auth."""
    response = client.post("/public/intake", json={
        "tenant_id": str(seed_tenant.id),
        "channel": "web",
        "raw_payload": {
            "full_name": "Test Client",
            "phone": "+1-555-0000",
            "case_type": "immigration",
            "description": "Need help with visa application",
            "language": "en",
        },
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "new"
    assert data["tenant_id"] == str(seed_tenant.id)
    assert data["raw_payload_json"]["full_name"] == "Test Client"
    return data["id"]


def test_public_intake_rejects_invalid_tenant(client):
    """Intake with non-existent tenant should 404."""
    response = client.post("/public/intake", json={
        "tenant_id": str(uuid.uuid4()),
        "channel": "web",
        "raw_payload": {"test": True},
    })
    assert response.status_code == 404


def test_full_intake_to_matter_flow(client, seed_tenant, seed_user, auth_headers):
    """End-to-end: create intake → convert to matter."""
    # Step 1: Create intake (public)
    intake_resp = client.post("/public/intake", json={
        "tenant_id": str(seed_tenant.id),
        "channel": "web",
        "raw_payload": {
            "full_name": "Maria Test",
            "case_type": "tax_resolution",
            "description": "Got IRS notice CP2000",
        },
    })
    assert intake_resp.status_code == 201
    intake_id = intake_resp.json()["id"]

    # Step 2: Convert intake to matter (authenticated)
    matter_resp = client.post("/matters/", json={
        "intake_id": intake_id,
        "type": "tax_resolution",
        "jurisdiction": "US",
        "urgency_score": 60,
    }, headers=auth_headers)
    assert matter_resp.status_code == 201
    matter = matter_resp.json()
    assert matter["type"] == "tax_resolution"
    assert matter["intake_id"] == intake_id
    assert matter["urgency_score"] == 60

    # Step 3: Verify intake status changed to "converted"
    intake_check = client.get(f"/intakes/{intake_id}")
    assert intake_check.status_code == 200
    assert intake_check.json()["status"] == "converted"

    # Step 4: Run agent on matter
    agent_resp = client.post("/agents/run", json={
        "matter_id": matter["id"],
        "agent_name": "tax_solutions_assistant",
        "input_data": {
            "full_name": "Maria Test",
            "notice_type": "CP2000",
            "tax_years": "2021-2022",
        },
    }, headers=auth_headers)
    assert agent_resp.status_code == 201
    agent_run = agent_resp.json()
    assert agent_run["agent_name"] == "tax_solutions_assistant"
    assert agent_run["status"] in ("needs_approval", "completed", "blocked")
    assert "case_packet" in agent_run["output_json"]
