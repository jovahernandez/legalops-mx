from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Matter, Intake, User
from app.schemas import MatterCreate, MatterOut

router = APIRouter(prefix="/matters", tags=["matters"])


@router.get("/", response_model=list[MatterOut])
def list_matters(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Matter)
        .filter(Matter.tenant_id == current_user.tenant_id)
        .order_by(Matter.urgency_score.desc(), Matter.created_at.desc())
        .all()
    )


@router.post("/", response_model=MatterOut, status_code=201)
def create_matter(body: MatterCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # If created from an intake, mark intake as converted
    if body.intake_id:
        intake = db.query(Intake).filter(Intake.id == body.intake_id).first()
        if not intake:
            raise HTTPException(status_code=404, detail="Intake not found")
        intake.status = "converted"

    matter = Matter(
        tenant_id=current_user.tenant_id,
        intake_id=body.intake_id,
        type=body.type,
        jurisdiction=body.jurisdiction,
        urgency_score=body.urgency_score,
        status="open",
    )
    db.add(matter)
    db.commit()
    db.refresh(matter)
    return matter


@router.get("/{matter_id}", response_model=MatterOut)
def get_matter(matter_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    matter = db.query(Matter).filter(Matter.id == matter_id, Matter.tenant_id == current_user.tenant_id).first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    return matter
