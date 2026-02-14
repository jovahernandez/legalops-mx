"""Approval SLA nudge service.

Checks for approvals pending longer than threshold and creates nudge tasks.
Called on-demand from analytics endpoint or via a scheduled job (stub).
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Approval, Task, Event


def check_sla_breaches(
    db: Session,
    tenant_id,
    sla_hours: int = 4,
) -> list[dict]:
    """Find approvals pending longer than sla_hours, create nudge tasks.

    Returns list of breached approval dicts.
    """
    threshold = datetime.now(timezone.utc) - timedelta(hours=sla_hours)

    breached = (
        db.query(Approval)
        .filter(
            Approval.tenant_id == tenant_id,
            Approval.status == "pending",
            Approval.created_at < threshold,
        )
        .all()
    )

    results = []
    for approval in breached:
        # Check if we already created a nudge task for this approval
        existing_nudge = (
            db.query(Task)
            .filter(
                Task.tenant_id == tenant_id,
                Task.title.contains(str(approval.id)),
                Task.title.contains("Nudge"),
            )
            .first()
        )
        if existing_nudge:
            continue

        # Create nudge task
        hours_pending = (datetime.now(timezone.utc) - approval.created_at).total_seconds() / 3600
        task = Task(
            tenant_id=tenant_id,
            matter_id=approval.matter_id,
            title=f"[SLA Nudge] Approval {str(approval.id)[:8]} pending {hours_pending:.0f}h",
            description=(
                f"Approval for {approval.object_type} has been pending for "
                f"{hours_pending:.1f} hours (SLA: {sla_hours}h). "
                f"Please review and approve/reject."
            ),
            status="pending",
        )
        db.add(task)

        # Track event
        db.add(Event(
            tenant_id=tenant_id,
            anonymous_id="system",
            name="approval_sla_breached",
            properties_json={
                "approval_id": str(approval.id),
                "hours_pending": round(hours_pending, 1),
                "sla_hours": sla_hours,
                "object_type": approval.object_type,
            },
        ))
        db.add(Event(
            tenant_id=tenant_id,
            anonymous_id="system",
            name="approval_nudged",
            properties_json={
                "approval_id": str(approval.id),
            },
        ))

        results.append({
            "approval_id": str(approval.id),
            "hours_pending": round(hours_pending, 1),
            "object_type": approval.object_type,
            "matter_id": str(approval.matter_id) if approval.matter_id else None,
        })

    if results:
        db.commit()

    return results
