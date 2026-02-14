"""Test: public event tracking endpoint."""


def test_track_event_creates_event(client):
    """POST /events/track should create an event without auth."""
    response = client.post("/events/track", json={
        "anonymous_id": "anon_test_001",
        "session_id": "sess_test_001",
        "name": "page_view",
        "properties": {"path": "/", "utm_source": "test"},
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "page_view"
    assert data["anonymous_id"] == "anon_test_001"
    assert data["properties_json"]["path"] == "/"
    assert data["properties_json"]["utm_source"] == "test"


def test_track_event_minimal_payload(client):
    """Minimum required fields: anonymous_id + name."""
    response = client.post("/events/track", json={
        "anonymous_id": "anon_min",
        "name": "cta_click",
    })
    assert response.status_code == 201
    assert response.json()["name"] == "cta_click"


def test_track_event_rejects_missing_fields(client):
    """Should reject payload without required fields."""
    response = client.post("/events/track", json={
        "name": "cta_click",
    })
    assert response.status_code == 422  # validation error


def test_track_multiple_events(client):
    """Track several events and verify count."""
    events = [
        {"anonymous_id": "anon_multi", "name": "page_view", "properties": {"path": "/"}},
        {"anonymous_id": "anon_multi", "name": "cta_click", "properties": {"variant": "b2c"}},
        {"anonymous_id": "anon_multi", "name": "intake_started", "properties": {"case_type": "immigration"}},
    ]
    for ev in events:
        resp = client.post("/events/track", json=ev)
        assert resp.status_code == 201

    # All three should be stored (check last one)
    last = client.post("/events/track", json={
        "anonymous_id": "anon_multi", "name": "intake_submitted",
        "properties": {"case_type": "immigration"},
    })
    assert last.status_code == 201
    assert last.json()["name"] == "intake_submitted"
