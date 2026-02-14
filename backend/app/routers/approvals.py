"""Human Approval Gate – approve or reject agent outputs / message drafts."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Approval, AgentRun, MessageDraft, User
from app.schemas import ApprovalDecision, ApprovalOut

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/", response_model=list[ApprovalOut])
def list_approvals(
    status: str | None = "pending",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Approval).filter(Approval.tenant_id == current_user.tenant_id)
    if status:
        q = q.filter(Approval.status == status)
    return q.order_by(Approval.created_at.desc()).all()


@router.post("/{approval_id}/approve", response_model=ApprovalOut)
def approve(
    approval_id: str,
    body: ApprovalDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    approval = _get_approval(approval_id, current_user, db)
    approval.status = "approved"
    approval.decided_by = current_user.id
    approval.decided_at = datetime.now(timezone.utc)
    approval.notes = body.notes

    # Cascade: update the related object's status
    _cascade_status(approval, "approved", db)

    db.commit()
    db.refresh(approval)
    return approval


@router.post("/{approval_id}/reject", response_model=ApprovalOut)
def reject(
    approval_id: str,
    body: ApprovalDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    approval = _get_approval(approval_id, current_user, db)
    approval.status = "rejected"
    approval.decided_by = current_user.id
    approval.decided_at = datetime.now(timezone.utc)
    approval.notes = body.notes

    _cascade_status(approval, "rejected", db)

    db.commit()
    db.refresh(approval)
    return approval


# ---- helpers ---------------------------------------------------------------

def _get_approval(approval_id: str, current_user: User, db: Session) -> Approval:
    approval = (
        db.query(Approval)
        .filter(Approval.id == approval_id, Approval.tenant_id == current_user.tenant_id)
        .first()
    )
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    if approval.status != "pending":
        raise HTTPException(status_code=400, detail=f"Approval already {approval.status}")
    return approval


def _cascade_status(approval: Approval, new_status: str, db: Session):
    """When an approval is decided, update the related object."""
    if approval.object_type == "agent_run":
        obj = db.query(AgentRun).filter(AgentRun.id == approval.object_id).first()
        if obj:
            obj.status = "completed" if new_status == "approved" else "blocked"
    elif approval.object_type == "message_draft":
        obj = db.query(MessageDraft).filter(MessageDraft.id == approval.object_id).first()
        if obj:
            obj.status = "approved" if new_status == "approved" else "draft"
