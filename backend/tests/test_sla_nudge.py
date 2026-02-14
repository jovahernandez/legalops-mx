"""Tests for SLA nudge service — approval breach detection + task creation."""

import uuid
from datetime import datetime, timedelta, timezone

from app.models import Approval, Matter, Task, Event
from app.services.sla_nudge import check_sla_breaches


def test_sla_breach_creates_task(db, seed_tenant, seed_user):
    """Approval pending > sla_hours creates a nudge task."""
    matter = Matter(
        tenant_id=seed_tenant.id, type="immigration",
        jurisdiction="US", urgency_score=50, status="open",
    )
    db.add(matter)
    db.flush()

    # Create approval that's been pending for 6 hours (over 4h SLA)
    approval = Approval(
        tenant_id=seed_tenant.id,
        matter_id=matter.id,
        object_type="agent_run",
        object_id=uuid.uuid4(),
        status="pending",
        requested_by=seed_user.id,
    )
    db.add(approval)
    db.commit()

    # Manually backdate created_at to simulate time passing
    approval.created_at = datetime.now(timezone.utc) - timedelta(hours=6)
    db.commit()

    results = check_sla_breaches(db, seed_tenant.id, sla_hours=4)
    assert len(results) == 1
    assert results[0]["approval_id"] == str(approval.id)
    assert results[0]["hours_pending"] >= 5.0

    # Verify task was created
    tasks = db.query(Task).filter(Task.tenant_id == seed_tenant.id).all()
    assert len(tasks) == 1
    assert "[SLA Nudge]" in tasks[0].title
    assert str(approval.id)[:8] in tasks[0].title

    # Verify events were tracked
    events = db.query(Event).filter(
        Event.tenant_id == seed_tenant.id,
        Event.name == "approval_sla_breached",
    ).all()
    assert len(events) == 1


def test_sla_no_breach_within_threshold(db, seed_tenant, seed_user):
    """Approval within SLA hours does NOT trigger nudge."""
    matter = Matter(
        tenant_id=seed_tenant.id, type="immigration",
        jurisdiction="US", urgency_score=50, status="open",
    )
    db.add(matter)
    db.flush()

    approval = Approval(
        tenant_id=seed_tenant.id,
        matter_id=matter.id,
        object_type="agent_run",
        object_id=uuid.uuid4(),
        status="pending",
        requested_by=seed_user.id,
    )
    db.add(approval)
    db.commit()
    # created_at defaults to now, so it's within the 4h threshold

    results = check_sla_breaches(db, seed_tenant.id, sla_hours=4)
    assert len(results) == 0

    tasks = db.query(Task).filter(Task.tenant_id == seed_tenant.id).all()
    assert len(tasks) == 0


def test_sla_idempotent(db, seed_tenant, seed_user):
    """Running check_sla_breaches twice does not duplicate nudge tasks."""
    matter = Matter(
        tenant_id=seed_tenant.id, type="immigration",
        jurisdiction="US", urgency_score=50, status="open",
    )
    db.add(matter)
    db.flush()

    approval = Approval(
        tenant_id=seed_tenant.id,
        matter_id=matter.id,
        object_type="agent_run",
        object_id=uuid.uuid4(),
        status="pending",
        requested_by=seed_user.id,
    )
    db.add(approval)
    db.commit()

    approval.created_at = datetime.now(timezone.utc) - timedelta(hours=6)
    db.commit()

    # First run
    results1 = check_sla_breaches(db, seed_tenant.id, sla_hours=4)
    assert len(results1) == 1

    # Second run — should NOT create another task
    results2 = check_sla_breaches(db, seed_tenant.id, sla_hours=4)
    assert len(results2) == 0

    tasks = db.query(Task).filter(Task.tenant_id == seed_tenant.id).all()
    assert len(tasks) == 1


def test_sla_ignores_decided_approvals(db, seed_tenant, seed_user):
    """Approved/rejected approvals are not flagged as breaches."""
    matter = Matter(
        tenant_id=seed_tenant.id, type="immigration",
        jurisdiction="US", urgency_score=50, status="open",
    )
    db.add(matter)
    db.flush()

    approval = Approval(
        tenant_id=seed_tenant.id,
        matter_id=matter.id,
        object_type="agent_run",
        object_id=uuid.uuid4(),
        status="approved",  # already decided
        requested_by=seed_user.id,
    )
    db.add(approval)
    db.commit()

    approval.created_at = datetime.now(timezone.utc) - timedelta(hours=10)
    db.commit()

    results = check_sla_breaches(db, seed_tenant.id, sla_hours=4)
    assert len(results) == 0
