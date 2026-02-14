"""Test: analytics funnel and overview endpoints."""

import uuid
from app.models import Intake, Matter, AgentRun, Approval, Event, Lead


def test_overview_returns_zeroes_when_empty(client, seed_user, auth_headers):
    """Overview should return zero counts for a fresh tenant."""
    response = client.get("/app/analytics/overview?days=7", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["period"] == "7d"
    assert data["intakes_total"] == 0
    assert data["matters_total"] == 0
    assert data["approvals_pending"] == 0
    assert data["leads_total"] == 0
    assert data["events_total"] == 0
    assert data["time_to_approve_median_hours"] is None


def test_overview_counts_intakes_and_matters(client, db, seed_tenant, seed_user, auth_headers):
    """Overview should count intakes and matters for the tenant."""
    # Create 2 intakes
    for i in range(2):
        db.add(Intake(
            tenant_id=seed_tenant.id,
            channel="web",
            raw_payload_json={"test": i},
            status="new",
        ))
    # Create 1 matter
    intake = Intake(
        tenant_id=seed_tenant.id,
        channel="web",
        raw_payload_json={"for_matter": True},
        status="converted",
    )
    db.add(intake)
    db.flush()
    db.add(Matter(
        tenant_id=seed_tenant.id,
        intake_id=intake.id,
        type="immigration",
        jurisdiction="US",
        status="open",
    ))
    db.commit()

    response = client.get("/app/analytics/overview?days=7", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["intakes_total"] == 3  # 2 + 1 for the matter
    assert data["matters_total"] == 1


def test_funnel_returns_steps(client, seed_user, auth_headers):
    """Funnel should return 6 steps even when empty."""
    response = client.get(
        "/app/analytics/funnel?vertical=immigration&days=30",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["vertical"] == "immigration"
    assert data["period"] == "30d"
    assert len(data["steps"]) == 6
    step_names = [s["name"] for s in data["steps"]]
    assert "Intakes Submitted" in step_names
    assert "Converted to Matter" in step_names
    assert "Approval Approved" in step_names


def test_overview_requires_auth(client):
    """Overview should 401 without auth headers."""
    response = client.get("/app/analytics/overview?days=7")
    assert response.status_code == 401


def test_funnel_requires_auth(client):
    """Funnel should 401 without auth headers."""
    response = client.get("/app/analytics/funnel?vertical=immigration&days=30")
    assert response.status_code == 401
