"""Feedback collection endpoint – supports both public and authenticated users."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Feedback, Event, User
from app.schemas import FeedbackCreate, FeedbackOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackOut, status_code=201)
def submit_feedback(
    body: FeedbackCreate,
    db: Session = Depends(get_db),
):
    """Public endpoint: submit feedback from any page. No auth required."""
    fb = Feedback(
        anonymous_id=body.anonymous_id,
        page=body.page,
        rating=body.rating,
        text=body.text,
        context_json=body.context,
    )
    db.add(fb)

    # Track event
    db.add(Event(
        anonymous_id=body.anonymous_id or "unknown",
        name="feedback_submitted",
        properties_json={
            "page": body.page,
            "rating": body.rating,
            "has_text": bool(body.text),
        },
    ))

    db.commit()
    db.refresh(fb)
    return fb


@router.get("/", response_model=list[FeedbackOut])
def list_feedback(
    page: str | None = None,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Authenticated: list feedback for this tenant."""
    q = db.query(Feedback)
    if current_user.tenant_id:
        q = q.filter(
            (Feedback.tenant_id == current_user.tenant_id) | (Feedback.tenant_id.is_(None))
        )
    if page:
        q = q.filter(Feedback.page == page)
    return q.order_by(Feedback.created_at.desc()).limit(limit).all()
