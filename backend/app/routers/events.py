"""Public event tracking endpoint with in-memory rate limiting."""

import time
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event
from app.schemas import EventCreate, EventOut

router = APIRouter(prefix="/events", tags=["events"])


# ---------------------------------------------------------------------------
# Simple in-memory rate limiter (replace with Redis in production)
# ---------------------------------------------------------------------------
_rate_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 120  # requests per window
RATE_WINDOW = 60  # seconds


def _check_rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    _rate_store[ip] = [t for t in _rate_store[ip] if now - t < RATE_WINDOW]
    if len(_rate_store[ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests")
    _rate_store[ip].append(now)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/track", response_model=EventOut, status_code=201)
def track_event(
    body: EventCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Public endpoint: track an analytics event. Rate-limited by IP."""
    _check_rate_limit(request)

    event = Event(
        tenant_id=body.tenant_id,
        anonymous_id=body.anonymous_id,
        user_id=body.user_id,
        session_id=body.session_id,
        name=body.name,
        properties_json=body.properties,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
