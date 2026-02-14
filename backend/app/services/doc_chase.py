"""Document chase cadence service (stub).

Creates MessageDraft + Approval for document reminders.
Does NOT send real messages — only creates drafts behind approval gate.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Matter, Document, Approval, MessageDraft, Event, Intake
from app.routers.templates import VERTICAL_TEMPLATES


def check_doc_reminders(
    db: Session,
    tenant_id,
    reminder_hours: int = 48,
) -> list[dict]:
    """Find matters with missing docs older than reminder_hours.

    Creates MessageDraft + Approval for each reminder.
    Returns list of created reminders.
    """
    threshold = datetime.now(timezone.utc) - timedelta(hours=reminder_hours)

    # Find matters in docs_pending stage older than threshold
    matters = (
        db.query(Matter)
        .filter(
            Matter.tenant_id == tenant_id,
            Matter.pipeline_stage == "docs_pending",
            Matter.created_at < threshold,
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

        # Check if we already sent a reminder recently (24h)
        recent = (
            db.query(MessageDraft)
            .filter(
                MessageDraft.matter_id == matter.id,
                MessageDraft.content.contains("[DOC REMINDER]"),
                MessageDraft.created_at > datetime.now(timezone.utc) - timedelta(hours=24),
            )
            .first()
        )
        if recent:
            continue

        # Get client info from intake
        client_name = "Client"
        if matter.intake_id:
            intake = db.query(Intake).filter(Intake.id == matter.intake_id).first()
            if intake and intake.raw_payload_json:
                client_name = intake.raw_payload_json.get("full_name", client_name)

        missing_list = "\n".join(f"  - {d.label}" for d in missing)
        content = (
            f"[DOC REMINDER] Dear {client_name},\n\n"
            f"We are still missing the following documents for your case:\n"
            f"{missing_list}\n\n"
            f"Please upload these at your earliest convenience to avoid delays.\n\n"
            f"Thank you."
        )

        draft = MessageDraft(
            tenant_id=tenant_id,
            matter_id=matter.id,
            channel="email",
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
            name="doc_reminder_draft_created",
            properties_json={
                "matter_id": str(matter.id),
                "missing_docs": len(missing),
            },
        ))

        results.append({
            "matter_id": str(matter.id),
            "missing_docs": [d.key for d in missing],
            "draft_id": str(draft.id),
        })

    if results:
        db.commit()

    return results
