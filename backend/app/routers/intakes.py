"""Public intake endpoint – no auth required."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Intake, Tenant
from app.schemas import IntakeCreate, IntakeOut
from app.rate_limit import limiter

router = APIRouter(tags=["intakes"])


@router.post("/public/intake", response_model=IntakeOut, status_code=201)
@limiter.limit("10/minute")
def create_public_intake(request: Request, body: IntakeCreate, db: Session = Depends(get_db)):
    """Public endpoint: anyone can submit an intake. No auth required."""
    tenant = db.query(Tenant).filter(Tenant.id == body.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    intake = Intake(
        tenant_id=body.tenant_id,
        channel=body.channel,
        raw_payload_json=body.raw_payload,
        status="new",
    )
    db.add(intake)
    db.commit()
    db.refresh(intake)
    return intake


@router.get("/intakes/", response_model=list[IntakeOut])
def list_intakes(
    tenant_id: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Intake)
    if tenant_id:
        q = q.filter(Intake.tenant_id == tenant_id)
    return q.order_by(Intake.created_at.desc()).all()


@router.get("/intakes/{intake_id}", response_model=IntakeOut)
def get_intake(intake_id: str, db: Session = Depends(get_db)):
    intake = db.query(Intake).filter(Intake.id == intake_id).first()
    if not intake:
        raise HTTPException(status_code=404, detail="Intake not found")
    return intake
