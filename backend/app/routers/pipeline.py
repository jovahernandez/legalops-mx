"""Kanban pipeline view – unified intake + matter pipeline by stage.

Supports both MX (9-stage) and US (7-stage) pipeline flows.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Intake, Matter, Event, Document, Approval, AgentRun, User
from app.schemas import PipelineView, PipelineItem, PipelineStageChange

router = APIRouter(prefix="/app/pipeline", tags=["pipeline"])

# MX pipeline stages (default)
MX_PIPELINE_STAGES = [
    "new_lead",
    "intake_completed",
    "docs_pending",
    "expediente_draft",
    "pending_approval",
    "approved",
    "contract_onboarding",
    "in_progress",
    "closed",
]

# US pipeline stages (legacy)
US_PIPELINE_STAGES = [
    "new_intake",
    "qualified",
    "matter_created",
    "docs_pending",
    "case_packet_pending",
    "approved",
    "closed",
]

# Unified: accept all stages from both flows
ALL_VALID_STAGES = list(set(MX_PIPELINE_STAGES + US_PIPELINE_STAGES))


def _next_action_for_stage(stage: str) -> str:
    return {
        # MX stages
        "new_lead": "Revisar lead y contactar",
        "intake_completed": "Verificar datos y crear expediente",
        "docs_pending": "Recopilar documentos faltantes",
        "expediente_draft": "Generar borrador de expediente",
        "pending_approval": "Revisar y aprobar expediente",
        "approved": "Enviar convenio/contrato al cliente",
        "contract_onboarding": "Confirmar firma y onboarding",
        "in_progress": "Dar seguimiento al caso",
        "closed": "Archivado",
        # US stages
        "new_intake": "Review intake and qualify",
        "qualified": "Create matter from intake",
        "matter_created": "Upload required documents",
        "case_packet_pending": "Review and approve case packet",
    }.get(stage, "")


@router.get("/", response_model=PipelineView)
def get_pipeline(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get unified Kanban pipeline view for tenant. Uses MX stages by default."""
    tid = current_user.tenant_id
    now = datetime.now(timezone.utc)

    active_stages = MX_PIPELINE_STAGES
    stages: dict[str, list[PipelineItem]] = {s: [] for s in active_stages}

    # Intakes not yet converted
    intakes = (
        db.query(Intake)
        .filter(Intake.tenant_id == tid, Intake.status.in_(["new", "processing"]))
        .order_by(Intake.created_at.asc())
        .all()
    )
    for intake in intakes:
        stage = intake.pipeline_stage or "new_lead"
        if stage not in stages:
            stage = "new_lead"
        payload = intake.raw_payload_json or {}
        days = (now - intake.created_at).days if intake.created_at else 0
        stages[stage].append(PipelineItem(
            id=intake.id,
            entity_type="intake",
            pipeline_stage=stage,
            type=payload.get("case_type"),
            client_name=payload.get("nombre_completo") or payload.get("full_name"),
            urgency_score=0,
            created_at=intake.created_at,
            intake_id=intake.id,
            days_in_stage=days,
            next_action=_next_action_for_stage(stage),
        ))

    # Matters
    matters = (
        db.query(Matter)
        .filter(Matter.tenant_id == tid)
        .order_by(Matter.urgency_score.desc(), Matter.created_at.asc())
        .all()
    )
    for matter in matters:
        stage = matter.pipeline_stage or "docs_pending"
        if stage not in stages:
            stage = "docs_pending"
        days = (now - matter.created_at).days if matter.created_at else 0
        client_name = None
        if matter.intake_id:
            intake = db.query(Intake).filter(Intake.id == matter.intake_id).first()
            if intake and intake.raw_payload_json:
                client_name = intake.raw_payload_json.get("nombre_completo") or intake.raw_payload_json.get("full_name")
        stages[stage].append(PipelineItem(
            id=matter.id,
            entity_type="matter",
            pipeline_stage=stage,
            type=matter.type,
            client_name=client_name,
            urgency_score=matter.urgency_score,
            created_at=matter.created_at,
            intake_id=matter.intake_id,
            matter_id=matter.id,
            days_in_stage=days,
            next_action=_next_action_for_stage(stage),
        ))

    stage_counts = {s: len(items) for s, items in stages.items()}
    return PipelineView(stages=stages, stage_counts=stage_counts)


@router.patch("/intake/{intake_id}/stage", response_model=PipelineItem)
def change_intake_stage(
    intake_id: str,
    body: PipelineStageChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Move an intake to a new pipeline stage."""
    if body.stage not in ALL_VALID_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage: {body.stage}")

    intake = (
        db.query(Intake)
        .filter(Intake.id == intake_id, Intake.tenant_id == current_user.tenant_id)
        .first()
    )
    if not intake:
        raise HTTPException(status_code=404, detail="Intake not found")

    old_stage = intake.pipeline_stage or "new_lead"
    intake.pipeline_stage = body.stage

    db.add(Event(
        tenant_id=current_user.tenant_id,
        anonymous_id=str(current_user.id),
        user_id=current_user.id,
        name="pipeline_stage_changed",
        properties_json={
            "entity_type": "intake",
            "entity_id": str(intake.id),
            "from_stage": old_stage,
            "to_stage": body.stage,
        },
    ))

    db.commit()
    db.refresh(intake)

    payload = intake.raw_payload_json or {}
    now = datetime.now(timezone.utc)
    return PipelineItem(
        id=intake.id,
        entity_type="intake",
        pipeline_stage=intake.pipeline_stage,
        type=payload.get("case_type"),
        client_name=payload.get("nombre_completo") or payload.get("full_name"),
        created_at=intake.created_at,
        intake_id=intake.id,
        days_in_stage=(now - intake.created_at).days if intake.created_at else 0,
        next_action=_next_action_for_stage(body.stage),
    )


@router.patch("/matter/{matter_id}/stage", response_model=PipelineItem)
def change_matter_stage(
    matter_id: str,
    body: PipelineStageChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Move a matter to a new pipeline stage."""
    if body.stage not in ALL_VALID_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage: {body.stage}")

    matter = (
        db.query(Matter)
        .filter(Matter.id == matter_id, Matter.tenant_id == current_user.tenant_id)
        .first()
    )
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")

    old_stage = matter.pipeline_stage or "docs_pending"
    matter.pipeline_stage = body.stage

    db.add(Event(
        tenant_id=current_user.tenant_id,
        anonymous_id=str(current_user.id),
        user_id=current_user.id,
        name="pipeline_stage_changed",
        properties_json={
            "entity_type": "matter",
            "entity_id": str(matter.id),
            "from_stage": old_stage,
            "to_stage": body.stage,
        },
    ))

    db.commit()
    db.refresh(matter)

    client_name = None
    if matter.intake_id:
        intake = db.query(Intake).filter(Intake.id == matter.intake_id).first()
        if intake and intake.raw_payload_json:
            client_name = intake.raw_payload_json.get("nombre_completo") or intake.raw_payload_json.get("full_name")

    now = datetime.now(timezone.utc)
    return PipelineItem(
        id=matter.id,
        entity_type="matter",
        pipeline_stage=matter.pipeline_stage,
        type=matter.type,
        client_name=client_name,
        urgency_score=matter.urgency_score,
        created_at=matter.created_at,
        intake_id=matter.intake_id,
        matter_id=matter.id,
        days_in_stage=(now - matter.created_at).days if matter.created_at else 0,
        next_action=_next_action_for_stage(body.stage),
    )
