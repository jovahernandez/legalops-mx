"""Tests for pipeline Kanban view and stage changes."""

import uuid
from datetime import datetime, timedelta, timezone

from app.models import Intake, Matter, Event


SEED_TENANT = uuid.UUID("00000000-0000-0000-0000-000000000001")


def test_get_pipeline_empty(client, auth_headers):
    """Pipeline returns all stages even when empty."""
    resp = client.get("/app/pipeline/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "stages" in data
    assert "stage_counts" in data
    for stage in ["new_intake", "qualified", "matter_created", "docs_pending",
                  "case_packet_pending", "approved", "closed"]:
        assert stage in data["stages"]
        assert data["stage_counts"][stage] == 0


def test_get_pipeline_with_data(client, db, seed_tenant, seed_user, auth_headers):
    """Pipeline returns intakes and matters in correct stages."""
    intake = Intake(
        tenant_id=seed_tenant.id, channel="web",
        raw_payload_json={"full_name": "Test Client", "case_type": "immigration"},
        status="new", pipeline_stage="new_intake",
    )
    db.add(intake)
    db.flush()

    matter = Matter(
        tenant_id=seed_tenant.id, intake_id=intake.id,
        type="immigration", jurisdiction="US",
        urgency_score=75, status="open",
        pipeline_stage="docs_pending",
    )
    db.add(matter)
    db.commit()

    resp = client.get("/app/pipeline/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["stage_counts"]["new_intake"] == 1
    assert data["stage_counts"]["docs_pending"] == 1

    # Verify intake card data
    intake_card = data["stages"]["new_intake"][0]
    assert intake_card["entity_type"] == "intake"
    assert intake_card["client_name"] == "Test Client"

    # Verify matter card data
    matter_card = data["stages"]["docs_pending"][0]
    assert matter_card["entity_type"] == "matter"
    assert matter_card["urgency_score"] == 75


def test_change_intake_stage(client, db, seed_tenant, seed_user, auth_headers):
    """Moving an intake to a new stage persists and tracks event."""
    intake = Intake(
        tenant_id=seed_tenant.id, channel="web",
        raw_payload_json={"full_name": "Stage Test"},
        status="new", pipeline_stage="new_intake",
    )
    db.add(intake)
    db.commit()

    resp = client.patch(
        f"/app/pipeline/intake/{intake.id}/stage",
        json={"stage": "qualified"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["pipeline_stage"] == "qualified"

    # Verify event was tracked
    events = db.query(Event).filter(
        Event.name == "pipeline_stage_changed",
        Event.tenant_id == seed_tenant.id,
    ).all()
    assert len(events) == 1
    assert events[0].properties_json["from_stage"] == "new_intake"
    assert events[0].properties_json["to_stage"] == "qualified"


def test_change_matter_stage(client, db, seed_tenant, seed_user, auth_headers):
    """Moving a matter to a new stage persists and tracks event."""
    matter = Matter(
        tenant_id=seed_tenant.id, type="immigration",
        jurisdiction="US", urgency_score=50, status="open",
        pipeline_stage="matter_created",
    )
    db.add(matter)
    db.commit()

    resp = client.patch(
        f"/app/pipeline/matter/{matter.id}/stage",
        json={"stage": "docs_pending"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["pipeline_stage"] == "docs_pending"
    assert data["next_action"] is not None


def test_change_stage_invalid(client, db, seed_tenant, seed_user, auth_headers):
    """Invalid stage returns 400."""
    intake = Intake(
        tenant_id=seed_tenant.id, channel="web",
        raw_payload_json={}, status="new", pipeline_stage="new_intake",
    )
    db.add(intake)
    db.commit()

    resp = client.patch(
        f"/app/pipeline/intake/{intake.id}/stage",
        json={"stage": "nonexistent_stage"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_pipeline_requires_auth(client):
    """Pipeline endpoint requires authentication."""
    resp = client.get("/app/pipeline/")
    assert resp.status_code == 401
