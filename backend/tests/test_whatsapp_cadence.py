"""Tests for WhatsApp draft cadence service."""

from datetime import datetime, timedelta, timezone

from app.models import Intake, Matter, Document, MessageDraft, Approval, Event
from app.services.whatsapp_cadence import check_whatsapp_reminders


def test_whatsapp_reminder_created(db, seed_tenant):
    """First WhatsApp reminder is created for matter with missing docs past 24h."""
    intake = Intake(
        tenant_id=seed_tenant.id, channel="web",
        raw_payload_json={
            "nombre_completo": "Laura García",
            "phone": "+52 55 1234 5678",
            "case_type": "mx_divorce",
            "descripcion": "Divorcio incausado",
        },
        status="converted",
    )
    db.add(intake)
    db.flush()

    matter = Matter(
        tenant_id=seed_tenant.id, intake_id=intake.id,
        type="mx_divorce", jurisdiction="MX",
        urgency_score=50, status="open",
        pipeline_stage="docs_pending",
    )
    db.add(matter)
    db.flush()

    # Upload only 1 of 4 required docs
    db.add(Document(
        tenant_id=seed_tenant.id, matter_id=matter.id,
        kind="ine_pasaporte", filename="ine.pdf", status="uploaded",
    ))
    db.commit()

    # Backdate matter to 25h ago (past first_reminder_hours=24)
    matter.created_at = datetime.now(timezone.utc) - timedelta(hours=25)
    db.commit()

    results = check_whatsapp_reminders(db, seed_tenant.id, first_reminder_hours=24)
    assert len(results) == 1
    assert results[0]["reminder_number"] == 1
    assert "acta_matrimonio" in results[0]["missing_docs"]

    # Verify MessageDraft was created
    drafts = db.query(MessageDraft).filter(
        MessageDraft.matter_id == matter.id,
        MessageDraft.channel == "whatsapp",
    ).all()
    assert len(drafts) == 1
    assert "[RECORDATORIO #1]" in drafts[0].content
    assert "Laura García" in drafts[0].content
    assert drafts[0].status == "needs_approval"

    # Verify Approval was created
    approvals = db.query(Approval).filter(
        Approval.object_type == "message_draft",
        Approval.object_id == drafts[0].id,
    ).all()
    assert len(approvals) == 1

    # Verify event tracked
    events = db.query(Event).filter(
        Event.name == "whatsapp_reminder_draft_created",
    ).all()
    assert len(events) == 1


def test_whatsapp_no_reminder_within_threshold(db, seed_tenant):
    """No reminder created if matter is within first_reminder_hours."""
    intake = Intake(
        tenant_id=seed_tenant.id, channel="web",
        raw_payload_json={
            "nombre_completo": "Recent Client",
            "phone": "+52 55 0000 0000",
            "case_type": "mx_divorce",
        },
        status="converted",
    )
    db.add(intake)
    db.flush()

    matter = Matter(
        tenant_id=seed_tenant.id, intake_id=intake.id,
        type="mx_divorce", jurisdiction="MX",
        urgency_score=50, status="open",
        pipeline_stage="docs_pending",
    )
    db.add(matter)
    db.commit()
    # created_at defaults to now — within 24h threshold

    results = check_whatsapp_reminders(db, seed_tenant.id, first_reminder_hours=24)
    assert len(results) == 0


def test_whatsapp_no_reminder_all_docs_uploaded(db, seed_tenant):
    """No reminder if all required docs are uploaded."""
    intake = Intake(
        tenant_id=seed_tenant.id, channel="web",
        raw_payload_json={
            "nombre_completo": "Complete Client",
            "phone": "+52 55 1111 2222",
            "case_type": "mx_divorce",
        },
        status="converted",
    )
    db.add(intake)
    db.flush()

    matter = Matter(
        tenant_id=seed_tenant.id, intake_id=intake.id,
        type="mx_divorce", jurisdiction="MX",
        urgency_score=50, status="open",
        pipeline_stage="docs_pending",
    )
    db.add(matter)
    db.flush()

    # Upload ALL 4 required docs
    for kind in ["acta_matrimonio", "ine_pasaporte", "curp", "comprobante_domicilio"]:
        db.add(Document(
            tenant_id=seed_tenant.id, matter_id=matter.id,
            kind=kind, filename=f"{kind}.pdf", status="uploaded",
        ))
    db.commit()

    matter.created_at = datetime.now(timezone.utc) - timedelta(hours=30)
    db.commit()

    results = check_whatsapp_reminders(db, seed_tenant.id, first_reminder_hours=24)
    assert len(results) == 0


def test_whatsapp_max_two_reminders(db, seed_tenant):
    """No more than 2 reminders per matter."""
    intake = Intake(
        tenant_id=seed_tenant.id, channel="web",
        raw_payload_json={
            "nombre_completo": "Max Reminders",
            "phone": "+52 55 3333 4444",
            "case_type": "mx_divorce",
        },
        status="converted",
    )
    db.add(intake)
    db.flush()

    matter = Matter(
        tenant_id=seed_tenant.id, intake_id=intake.id,
        type="mx_divorce", jurisdiction="MX",
        urgency_score=50, status="open",
        pipeline_stage="docs_pending",
    )
    db.add(matter)
    db.flush()

    db.add(Document(
        tenant_id=seed_tenant.id, matter_id=matter.id,
        kind="ine_pasaporte", filename="ine.pdf", status="uploaded",
    ))
    db.commit()

    # Backdate matter to 50h ago (past both thresholds)
    matter.created_at = datetime.now(timezone.utc) - timedelta(hours=50)
    db.commit()

    # First reminder
    results1 = check_whatsapp_reminders(db, seed_tenant.id, first_reminder_hours=24, second_reminder_hours=48)
    assert len(results1) == 1

    # Backdate the first draft so it's not "recent" (outside 12h cooldown)
    first_draft = db.query(MessageDraft).filter(
        MessageDraft.matter_id == matter.id,
        MessageDraft.channel == "whatsapp",
    ).first()
    first_draft.created_at = datetime.now(timezone.utc) - timedelta(hours=13)
    db.commit()

    # Second reminder
    results2 = check_whatsapp_reminders(db, seed_tenant.id, first_reminder_hours=24, second_reminder_hours=48)
    assert len(results2) == 1
    assert results2[0]["reminder_number"] == 2

    # Backdate second draft outside cooldown
    second_draft = db.query(MessageDraft).filter(
        MessageDraft.matter_id == matter.id,
        MessageDraft.channel == "whatsapp",
    ).order_by(MessageDraft.created_at.desc()).first()
    second_draft.created_at = datetime.now(timezone.utc) - timedelta(hours=13)
    db.commit()

    # Third attempt — should NOT create a reminder (max 2)
    results3 = check_whatsapp_reminders(db, seed_tenant.id, first_reminder_hours=24, second_reminder_hours=48)
    assert len(results3) == 0

    total_drafts = db.query(MessageDraft).filter(
        MessageDraft.matter_id == matter.id,
        MessageDraft.channel == "whatsapp",
    ).count()
    assert total_drafts == 2


def test_whatsapp_idempotent_within_cooldown(db, seed_tenant):
    """Running twice within 12h cooldown does not duplicate reminder."""
    intake = Intake(
        tenant_id=seed_tenant.id, channel="web",
        raw_payload_json={
            "nombre_completo": "Idempotent Client",
            "phone": "+52 55 5555 6666",
            "case_type": "mx_divorce",
        },
        status="converted",
    )
    db.add(intake)
    db.flush()

    matter = Matter(
        tenant_id=seed_tenant.id, intake_id=intake.id,
        type="mx_divorce", jurisdiction="MX",
        urgency_score=50, status="open",
        pipeline_stage="docs_pending",
    )
    db.add(matter)
    db.commit()

    matter.created_at = datetime.now(timezone.utc) - timedelta(hours=25)
    db.commit()

    # First run
    results1 = check_whatsapp_reminders(db, seed_tenant.id, first_reminder_hours=24)
    assert len(results1) == 1

    # Second run immediately — should be blocked by 12h cooldown
    results2 = check_whatsapp_reminders(db, seed_tenant.id, first_reminder_hours=24)
    assert len(results2) == 0

    total_drafts = db.query(MessageDraft).filter(
        MessageDraft.matter_id == matter.id,
        MessageDraft.channel == "whatsapp",
    ).count()
    assert total_drafts == 1
