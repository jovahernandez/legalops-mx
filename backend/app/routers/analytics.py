"""Analytics endpoints – KPIs, funnels, and drop-off analysis."""

from datetime import datetime, timedelta, timezone
from statistics import median

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import (
    Intake, Matter, Approval, Event, Lead, AgentRun, MessageDraft, User, Document, Task,
)
from app.schemas import AnalyticsOverview, FunnelStep, FunnelResponse, PilotKPIs
from app.services.sla_nudge import check_sla_breaches
from app.services.doc_chase import check_doc_reminders

router = APIRouter(prefix="/app/analytics", tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
def get_overview(
    days: int = Query(default=7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """KPI overview for the current tenant over the last N days."""
    tid = current_user.tenant_id
    since = datetime.now(timezone.utc) - timedelta(days=days)

    intakes_total = (
        db.query(func.count(Intake.id))
        .filter(Intake.tenant_id == tid, Intake.created_at >= since)
        .scalar() or 0
    )
    matters_total = (
        db.query(func.count(Matter.id))
        .filter(Matter.tenant_id == tid, Matter.created_at >= since)
        .scalar() or 0
    )
    approvals_pending = (
        db.query(func.count(Approval.id))
        .filter(Approval.tenant_id == tid, Approval.status == "pending")
        .scalar() or 0
    )
    approvals_approved = (
        db.query(func.count(Approval.id))
        .filter(Approval.tenant_id == tid, Approval.status == "approved", Approval.decided_at >= since)
        .scalar() or 0
    )
    approvals_rejected = (
        db.query(func.count(Approval.id))
        .filter(Approval.tenant_id == tid, Approval.status == "rejected", Approval.decided_at >= since)
        .scalar() or 0
    )
    leads_total = (
        db.query(func.count(Lead.id))
        .filter(Lead.tenant_id == tid, Lead.created_at >= since)
        .scalar() or 0
    )
    events_total = (
        db.query(func.count(Event.id))
        .filter(Event.tenant_id == tid, Event.created_at >= since)
        .scalar() or 0
    )

    # Median time to approve (in Python for DB compatibility)
    approved_rows = (
        db.query(Approval.created_at, Approval.decided_at)
        .filter(
            Approval.tenant_id == tid,
            Approval.status == "approved",
            Approval.decided_at.isnot(None),
            Approval.decided_at >= since,
        )
        .all()
    )
    tta_hours = None
    if approved_rows:
        deltas = [
            (r.decided_at - r.created_at).total_seconds() / 3600
            for r in approved_rows
            if r.decided_at and r.created_at
        ]
        if deltas:
            tta_hours = round(median(deltas), 1)

    return AnalyticsOverview(
        period=f"{days}d",
        intakes_total=intakes_total,
        matters_total=matters_total,
        approvals_pending=approvals_pending,
        approvals_approved=approvals_approved,
        approvals_rejected=approvals_rejected,
        time_to_approve_median_hours=tta_hours,
        leads_total=leads_total,
        events_total=events_total,
    )


@router.get("/funnel", response_model=FunnelResponse)
def get_funnel(
    vertical: str = Query(default="immigration"),
    days: int = Query(default=30, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Funnel by vertical: intake → matter → agent_run → approval → sent."""
    tid = current_user.tenant_id
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Step 1: Intakes for this vertical
    intakes = (
        db.query(func.count(Intake.id))
        .filter(Intake.tenant_id == tid, Intake.created_at >= since)
        .scalar() or 0
    )

    # Step 2: Matters of this type
    matters = (
        db.query(func.count(Matter.id))
        .filter(Matter.tenant_id == tid, Matter.type == vertical, Matter.created_at >= since)
        .scalar() or 0
    )

    # Step 3: Agent runs on those matters
    matter_ids_q = (
        db.query(Matter.id)
        .filter(Matter.tenant_id == tid, Matter.type == vertical, Matter.created_at >= since)
    )
    agent_runs = (
        db.query(func.count(AgentRun.id))
        .filter(AgentRun.matter_id.in_(matter_ids_q), AgentRun.created_at >= since)
        .scalar() or 0
    )

    # Step 4: Approvals requested
    approvals_requested = (
        db.query(func.count(Approval.id))
        .filter(Approval.matter_id.in_(matter_ids_q), Approval.created_at >= since)
        .scalar() or 0
    )

    # Step 5: Approvals approved
    approvals_approved = (
        db.query(func.count(Approval.id))
        .filter(
            Approval.matter_id.in_(matter_ids_q),
            Approval.status == "approved",
            Approval.decided_at >= since,
        )
        .scalar() or 0
    )

    # Step 6: Messages sent
    messages_sent = (
        db.query(func.count(MessageDraft.id))
        .filter(
            MessageDraft.matter_id.in_(matter_ids_q),
            MessageDraft.status == "sent",
            MessageDraft.created_at >= since,
        )
        .scalar() or 0
    )

    raw_steps = [
        ("Intakes Submitted", intakes),
        ("Converted to Matter", matters),
        ("Agent Run Created", agent_runs),
        ("Approval Requested", approvals_requested),
        ("Approval Approved", approvals_approved),
        ("Message Sent", messages_sent),
    ]

    steps = []
    for i, (name, count) in enumerate(raw_steps):
        conv = None
        if i > 0 and raw_steps[i - 1][1] > 0:
            conv = round(count / raw_steps[i - 1][1] * 100, 1)
        steps.append(FunnelStep(name=name, count=count, conversion_from_previous=conv))

    return FunnelResponse(vertical=vertical, period=f"{days}d", steps=steps)


@router.get("/pilot-kpis", response_model=PilotKPIs)
def get_pilot_kpis(
    days: int = Query(default=7, ge=1, le=90),
    sla_hours: int = Query(default=4, ge=1, le=72),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Pilot-specific KPIs: time_to_first_response, approval SLA, doc completeness, pipeline distribution."""
    tid = current_user.tenant_id
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # --- Time to first response (intake_submitted → first internal action) ---
    # Approximated: intake.created_at → first task or agent_run on the linked matter
    intake_matters = (
        db.query(Intake.created_at, Matter.created_at)
        .join(Matter, Matter.intake_id == Intake.id)
        .filter(Intake.tenant_id == tid, Intake.created_at >= since)
        .all()
    )
    ttfr_hours = None
    if intake_matters:
        deltas = [
            (m_created - i_created).total_seconds() / 3600
            for i_created, m_created in intake_matters
            if i_created and m_created
        ]
        if deltas:
            ttfr_hours = round(median(deltas), 1)

    # --- Time to approval median ---
    approved_rows = (
        db.query(Approval.created_at, Approval.decided_at)
        .filter(
            Approval.tenant_id == tid,
            Approval.status == "approved",
            Approval.decided_at.isnot(None),
            Approval.decided_at >= since,
        )
        .all()
    )
    tta_hours = None
    if approved_rows:
        deltas = [
            (r.decided_at - r.created_at).total_seconds() / 3600
            for r in approved_rows
            if r.decided_at and r.created_at
        ]
        if deltas:
            tta_hours = round(median(deltas), 1)

    # --- Doc completeness at 72h ---
    threshold_72h = datetime.now(timezone.utc) - timedelta(hours=72)
    matters_older_72h = (
        db.query(Matter)
        .filter(Matter.tenant_id == tid, Matter.created_at <= threshold_72h, Matter.created_at >= since)
        .all()
    )
    doc_complete_count = 0
    for matter in matters_older_72h:
        from app.routers.templates import VERTICAL_TEMPLATES
        template = VERTICAL_TEMPLATES.get(matter.type)
        if not template:
            doc_complete_count += 1
            continue
        required = [d for d in template.required_documents if d.required]
        if not required:
            doc_complete_count += 1
            continue
        docs = db.query(Document).filter(
            Document.matter_id == matter.id,
            Document.status.in_(["uploaded", "verified"]),
        ).all()
        uploaded_kinds = {d.kind for d in docs}
        if all(d.key in uploaded_kinds for d in required):
            doc_complete_count += 1

    doc_72h_pct = None
    if matters_older_72h:
        doc_72h_pct = round(doc_complete_count / len(matters_older_72h) * 100, 1)

    # --- consult_scheduled stub event count ---
    consult_count = (
        db.query(func.count(Event.id))
        .filter(Event.tenant_id == tid, Event.name == "consult_scheduled", Event.created_at >= since)
        .scalar() or 0
    )

    # --- Pipeline stage distribution ---
    stage_dist: dict[str, int] = {}
    intake_stages = (
        db.query(Intake.pipeline_stage, func.count(Intake.id))
        .filter(Intake.tenant_id == tid, Intake.status.in_(["new", "processing"]))
        .group_by(Intake.pipeline_stage)
        .all()
    )
    for stage, count in intake_stages:
        stage_dist[stage or "new_intake"] = stage_dist.get(stage or "new_intake", 0) + count

    matter_stages = (
        db.query(Matter.pipeline_stage, func.count(Matter.id))
        .filter(Matter.tenant_id == tid)
        .group_by(Matter.pipeline_stage)
        .all()
    )
    for stage, count in matter_stages:
        stage_dist[stage or "matter_created"] = stage_dist.get(stage or "matter_created", 0) + count

    # --- SLA breaches (also runs nudge creation) ---
    breaches = check_sla_breaches(db, tid, sla_hours)

    # --- Also run doc chase check ---
    check_doc_reminders(db, tid, reminder_hours=48)

    return PilotKPIs(
        period=f"{days}d",
        time_to_first_response_median_hours=ttfr_hours,
        time_to_approval_median_hours=tta_hours,
        doc_completeness_72h_pct=doc_72h_pct,
        consult_scheduled_count=consult_count,
        pipeline_stage_distribution=stage_dist,
        sla_breaches=len(breaches),
    )
