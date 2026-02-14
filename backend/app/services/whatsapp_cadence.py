"""WhatsApp draft cadence service (simulated).

Creates MessageDraft with channel=whatsapp for document reminders.
Does NOT send real WhatsApp messages — only creates drafts behind approval gate.
Configurable cadence: 24h first reminder, 48h second reminder.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Matter, Document, Approval, MessageDraft, Event, Intake
from app.routers.templates import VERTICAL_TEMPLATES


def check_whatsapp_reminders(
    db: Session,
    tenant_id,
    first_reminder_hours: int = 24,
    second_reminder_hours: int = 48,
) -> list[dict]:
    """Find matters needing WhatsApp doc reminders.

    Creates MessageDraft (channel=whatsapp) + Approval for each reminder.
    Returns list of created reminders.
    """
    now = datetime.now(timezone.utc)
    first_threshold = now - timedelta(hours=first_reminder_hours)
    second_threshold = now - timedelta(hours=second_reminder_hours)

    # Find matters in docs_pending stage
    matters = (
        db.query(Matter)
        .filter(
            Matter.tenant_id == tenant_id,
            Matter.pipeline_stage == "docs_pending",
            Matter.created_at < first_threshold,
        )
        .all()
    )

    results = []
    for matter in matters:
        template = VERTICAL_TEMPLATES.get(matter.type)
        if not template:
            continue

        # Check which docs are missing
        docs = db.query(Document).filter(
            Document.matter_id == matter.id,
            Document.status.in_(["uploaded", "verified"]),
        ).all()
        uploaded_kinds = {d.kind for d in docs}
        missing = [d for d in template.required_documents if d.required and d.key not in uploaded_kinds]

        if not missing:
            continue

        # Check if we already sent a WhatsApp reminder recently (12h)
        recent = (
            db.query(MessageDraft)
            .filter(
                MessageDraft.matter_id == matter.id,
                MessageDraft.channel == "whatsapp",
                MessageDraft.content.contains("[RECORDATORIO]"),
                MessageDraft.created_at > now - timedelta(hours=12),
            )
            .first()
        )
        if recent:
            continue

        # Count existing whatsapp reminders to determine cadence step
        existing_count = (
            db.query(MessageDraft)
            .filter(
                MessageDraft.matter_id == matter.id,
                MessageDraft.channel == "whatsapp",
                MessageDraft.content.contains("[RECORDATORIO]"),
            )
            .count()
        )

        # Only send up to 2 reminders
        if existing_count >= 2:
            continue

        # For second reminder, only if past second_threshold
        if existing_count == 1 and matter.created_at > second_threshold:
            continue

        # Get client info
        client_name = "Cliente"
        client_phone = ""
        if matter.intake_id:
            intake = db.query(Intake).filter(Intake.id == matter.intake_id).first()
            if intake and intake.raw_payload_json:
                client_name = (
                    intake.raw_payload_json.get("nombre_completo")
                    or intake.raw_payload_json.get("full_name", client_name)
                )
                client_phone = intake.raw_payload_json.get("phone", "")

        reminder_num = existing_count + 1
        missing_list = "\n".join(f"  - {d.label}" for d in missing)
        content = (
            f"[RECORDATORIO #{reminder_num}] Hola {client_name},\n\n"
            f"Le recordamos que aún necesitamos los siguientes documentos "
            f"para avanzar con su caso:\n"
            f"{missing_list}\n\n"
            f"Por favor envíelos por este medio o súbalos a la plataforma.\n\n"
            f"Gracias por su confianza."
        )

        draft = MessageDraft(
            tenant_id=tenant_id,
            matter_id=matter.id,
            channel="whatsapp",
            content=content,
            status="needs_approval",
        )
        db.add(draft)
        db.flush()

        approval = Approval(
            tenant_id=tenant_id,
            matter_id=matter.id,
            object_type="message_draft",
            object_id=draft.id,
            status="pending",
        )
        db.add(approval)

        db.add(Event(
            tenant_id=tenant_id,
            anonymous_id="system",
            name="whatsapp_reminder_draft_created",
            properties_json={
                "matter_id": str(matter.id),
                "reminder_number": reminder_num,
                "missing_docs": len(missing),
                "channel": "whatsapp",
                "client_phone": client_phone,
            },
        ))

        results.append({
            "matter_id": str(matter.id),
            "reminder_number": reminder_num,
            "missing_docs": [d.key for d in missing],
            "draft_id": str(draft.id),
            "channel": "whatsapp",
        })

    if results:
        db.commit()

    return results
