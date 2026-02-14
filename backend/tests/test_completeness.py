"""Tests for vertical templates + matter completeness calculation."""

import uuid

from app.models import Intake, Matter, Document


def test_get_immigration_template(client):
    """Immigration template returns correct structure."""
    resp = client.get("/templates/immigration")
    assert resp.status_code == 200
    data = resp.json()
    assert data["vertical"] == "immigration"
    assert data["display_name"] == "Immigration (US)"
    assert len(data["required_documents"]) >= 3
    assert len(data["required_fields"]) >= 4


def test_get_nonexistent_template(client):
    """Requesting unknown vertical returns 404."""
    resp = client.get("/templates/unknown_vertical")
    assert resp.status_code == 404


def test_list_all_templates(client):
    """List templates returns all configured verticals."""
    resp = client.get("/templates/")
    assert resp.status_code == 200
    data = resp.json()
    verticals = [t["vertical"] for t in data]
    assert "immigration" in verticals
    assert "tax_resolution" in verticals
    assert "mx_divorce" in verticals


def test_completeness_missing_docs(client, db, seed_tenant, seed_user, auth_headers):
    """Completeness returns missing documents for immigration matter."""
    intake = Intake(
        tenant_id=seed_tenant.id, channel="web",
        raw_payload_json={
            "full_name": "Juan Perez",
            "phone": "+1-555-0101",
            "case_type": "immigration",
            "description": "NTA case",
            "language": "es",
        },
        status="converted",
    )
    db.add(intake)
    db.flush()

    matter = Matter(
        tenant_id=seed_tenant.id, intake_id=intake.id,
        type="immigration", jurisdiction="US",
        urgency_score=80, status="open",
        pipeline_stage="docs_pending",
    )
    db.add(matter)
    db.flush()

    # Upload only one doc (government_id) — others still missing
    db.add(Document(
        tenant_id=seed_tenant.id, matter_id=matter.id,
        kind="government_id", filename="passport.pdf", status="uploaded",
    ))
    db.commit()

    resp = client.get(f"/matters/{matter.id}/completeness", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["vertical"] == "immigration"
    assert data["docs_required"] >= 2  # government_id + immigration_notice + proof_of_address
    assert data["docs_uploaded"] >= 1
    assert len(data["docs_missing"]) >= 1  # At least immigration_notice is missing
    assert data["completeness_pct"] < 100.0
    assert data["is_complete"] is False


def test_completeness_all_docs(client, db, seed_tenant, seed_user, auth_headers):
    """Completeness is 100% when all required docs and fields are present."""
    intake = Intake(
        tenant_id=seed_tenant.id, channel="web",
        raw_payload_json={
            "full_name": "Complete Client",
            "phone": "+1-555-9999",
            "case_type": "immigration",
            "description": "Full case",
            "language": "en",
        },
        status="converted",
    )
    db.add(intake)
    db.flush()

    matter = Matter(
        tenant_id=seed_tenant.id, intake_id=intake.id,
        type="immigration", jurisdiction="US",
        urgency_score=50, status="open",
    )
    db.add(matter)
    db.flush()

    # Upload all required docs
    for kind in ["government_id", "immigration_notice", "proof_of_address"]:
        db.add(Document(
            tenant_id=seed_tenant.id, matter_id=matter.id,
            kind=kind, filename=f"{kind}.pdf", status="uploaded",
        ))
    db.commit()

    resp = client.get(f"/matters/{matter.id}/completeness", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["completeness_pct"] == 100.0
    assert data["is_complete"] is True
    assert len(data["docs_missing"]) == 0
    assert len(data["fields_missing"]) == 0


def test_completeness_missing_fields(client, db, seed_tenant, seed_user, auth_headers):
    """Missing required intake fields are reported in completeness."""
    intake = Intake(
        tenant_id=seed_tenant.id, channel="web",
        raw_payload_json={
            "full_name": "Partial",
            # missing phone, case_type, description, language
        },
        status="converted",
    )
    db.add(intake)
    db.flush()

    matter = Matter(
        tenant_id=seed_tenant.id, intake_id=intake.id,
        type="immigration", jurisdiction="US",
        urgency_score=50, status="open",
    )
    db.add(matter)
    db.commit()

    resp = client.get(f"/matters/{matter.id}/completeness", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert len(data["fields_missing"]) >= 3  # phone, case_type, description, language
    assert data["is_complete"] is False


def test_completeness_requires_auth(client, db, seed_tenant):
    """Completeness endpoint requires authentication."""
    matter = Matter(
        tenant_id=seed_tenant.id, type="immigration",
        jurisdiction="US", urgency_score=50, status="open",
    )
    db.add(matter)
    db.commit()

    resp = client.get(f"/matters/{matter.id}/completeness")
    assert resp.status_code == 401
