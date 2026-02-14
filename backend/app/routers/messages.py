"""Message drafting with mandatory Human Approval Gate."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import MessageDraft, Approval, Matter, User
from app.schemas import MessageDraftCreate, MessageDraftOut

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/draft", response_model=MessageDraftOut, status_code=201)
def create_draft(
    body: MessageDraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a message draft. Always requires approval before sending."""
    matter = db.query(Matter).filter(Matter.id == body.matter_id, Matter.tenant_id == current_user.tenant_id).first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")

    draft = MessageDraft(
        tenant_id=current_user.tenant_id,
        matter_id=body.matter_id,
        channel=body.channel,
        content=body.content,
        status="needs_approval",
    )
    db.add(draft)
    db.flush()

    # Auto-create approval request (Human Approval Gate)
    approval = Approval(
        tenant_id=current_user.tenant_id,
        matter_id=body.matter_id,
        object_type="message_draft",
        object_id=draft.id,
        status="pending",
        requested_by=current_user.id,
    )
    db.add(approval)
    db.commit()
    db.refresh(draft)
    return draft


@router.get("/", response_model=list[MessageDraftOut])
def list_drafts(
    matter_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(MessageDraft)
        .filter(MessageDraft.matter_id == matter_id, MessageDraft.tenant_id == current_user.tenant_id)
        .order_by(MessageDraft.created_at.desc())
        .all()
    )


@router.post("/{draft_id}/send")
def send_message(
    draft_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Simulate sending. Only allowed if status == approved."""
    draft = (
        db.query(MessageDraft)
        .filter(MessageDraft.id == draft_id, MessageDraft.tenant_id == current_user.tenant_id)
        .first()
    )
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    if draft.status != "approved":
        raise HTTPException(status_code=400, detail=f"Draft must be approved before sending (current: {draft.status})")

    draft.status = "sent"
    db.commit()
    return {"status": "sent", "channel": draft.channel, "simulated": True}
