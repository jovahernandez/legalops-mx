from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import InterpreterRequest, Matter, User
from app.schemas import InterpreterRequestCreate, InterpreterRequestOut

router = APIRouter(prefix="/interpreters", tags=["interpreters"])


@router.post("/", response_model=InterpreterRequestOut, status_code=201)
def create_request(
    body: InterpreterRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    matter = db.query(Matter).filter(Matter.id == body.matter_id, Matter.tenant_id == current_user.tenant_id).first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")

    req = InterpreterRequest(
        tenant_id=current_user.tenant_id,
        matter_id=body.matter_id,
        language=body.language,
        modality=body.modality,
        date_pref=body.date_pref,
        notes=body.notes,
        status="requested",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.get("/", response_model=list[InterpreterRequestOut])
def list_requests(
    matter_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(InterpreterRequest).filter(InterpreterRequest.tenant_id == current_user.tenant_id)
    if matter_id:
        q = q.filter(InterpreterRequest.matter_id == matter_id)
    return q.order_by(InterpreterRequest.created_at.desc()).all()


@router.patch("/{request_id}/confirm", response_model=InterpreterRequestOut)
def confirm_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = (
        db.query(InterpreterRequest)
        .filter(InterpreterRequest.id == request_id, InterpreterRequest.tenant_id == current_user.tenant_id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    req.status = "confirmed"
    db.commit()
    db.refresh(req)
    return req
