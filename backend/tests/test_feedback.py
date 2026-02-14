"""Tests for feedback collection endpoint."""

from app.models import Feedback


def test_submit_feedback(client, db, seed_tenant):
    """Feedback is stored in the database."""
    resp = client.post("/feedback/", json={
        "page": "/help",
        "rating": 5,
        "text": "Great prep kit!",
        "anonymous_id": "anon_test_001",
        "context": {"case_type": "immigration"},
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["page"] == "/help"
    assert data["rating"] == 5

    # Verify in database
    feedbacks = db.query(Feedback).all()
    assert len(feedbacks) == 1
    assert feedbacks[0].text == "Great prep kit!"
    assert feedbacks[0].anonymous_id == "anon_test_001"


def test_submit_feedback_minimal(client, db):
    """Feedback with only required fields succeeds."""
    resp = client.post("/feedback/", json={
        "page": "/app/pipeline",
        "rating": 3,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["rating"] == 3


def test_submit_feedback_invalid_rating(client):
    """Rating outside 1-5 returns validation error."""
    resp = client.post("/feedback/", json={
        "page": "/help",
        "rating": 0,
    })
    assert resp.status_code == 422

    resp = client.post("/feedback/", json={
        "page": "/help",
        "rating": 6,
    })
    assert resp.status_code == 422


def test_list_feedback_requires_auth(client):
    """GET /feedback/ requires authentication."""
    resp = client.get("/feedback/")
    assert resp.status_code == 401


def test_list_feedback(client, db, seed_tenant, seed_user, auth_headers):
    """Authenticated user can list feedback for their tenant."""
    # Submit some feedback first
    db.add(Feedback(
        tenant_id=seed_tenant.id,
        page="/help",
        rating=4,
        text="Good",
        anonymous_id="anon_1",
    ))
    db.add(Feedback(
        tenant_id=seed_tenant.id,
        page="/app/pipeline",
        rating=5,
        text="Love the Kanban view",
        anonymous_id="anon_2",
    ))
    db.commit()

    resp = client.get("/feedback/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
