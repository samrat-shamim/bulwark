"""Tests for event ingestion and listing."""

import pytest
import uuid
from datetime import datetime, timezone


def _make_event(session_id="sess_1", event_type="tool_call", **overrides):
    event = {
        "event_id": f"evt_{uuid.uuid4().hex[:12]}",
        "session_id": session_id,
        "agent_name": "test-agent",
        "environment": "test",
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration_ms": 150,
        "status": "success",
        "tool_name": "web_search",
        "input": {"q": "test"},
    }
    event.update(overrides)
    return event


# --- Batch Ingest ---


async def test_batch_ingest_success(client, auth_headers):
    events = [_make_event() for _ in range(3)]
    resp = await client.post(
        "/v1/events/batch", json={"events": events}, headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["accepted"] == 3
    assert data["errors"] == 0


async def test_batch_ingest_creates_session(client, auth_headers):
    events = [_make_event(session_id="new_session_42")]
    resp = await client.post(
        "/v1/events/batch", json={"events": events}, headers=auth_headers
    )
    assert resp.status_code == 200

    # Session should now exist
    resp = await client.get("/v1/sessions", headers=auth_headers)
    sessions = resp.json()["sessions"]
    ids = [s["id"] for s in sessions]
    assert "new_session_42" in ids


async def test_batch_ingest_empty_list(client, auth_headers):
    resp = await client.post(
        "/v1/events/batch", json={"events": []}, headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["accepted"] == 0


async def test_batch_ingest_no_auth(client):
    """Missing Authorization header returns 422 (FastAPI header validation)."""
    events = [_make_event()]
    resp = await client.post("/v1/events/batch", json={"events": events})
    assert resp.status_code == 422


async def test_batch_ingest_bad_api_key(client):
    events = [_make_event()]
    resp = await client.post(
        "/v1/events/batch",
        json={"events": events},
        headers={"Authorization": "Bearer bad_key_123"},
    )
    assert resp.status_code == 401


# --- List Events ---


async def test_list_events(client, auth_headers):
    events = [_make_event(session_id="sess_list") for _ in range(5)]
    await client.post(
        "/v1/events/batch", json={"events": events}, headers=auth_headers
    )

    resp = await client.get("/v1/events", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["events"]) >= 5


async def test_list_events_filter_by_session(client, auth_headers):
    await client.post(
        "/v1/events/batch",
        json={"events": [_make_event(session_id="sess_a")]},
        headers=auth_headers,
    )
    await client.post(
        "/v1/events/batch",
        json={"events": [_make_event(session_id="sess_b")]},
        headers=auth_headers,
    )

    resp = await client.get(
        "/v1/events", params={"session_id": "sess_a"}, headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert all(e["session_id"] == "sess_a" for e in data["events"])


async def test_list_events_limit(client, auth_headers):
    events = [_make_event(session_id="sess_limit") for _ in range(10)]
    await client.post(
        "/v1/events/batch", json={"events": events}, headers=auth_headers
    )

    resp = await client.get(
        "/v1/events", params={"limit": 3}, headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["events"]) <= 3


async def test_list_events_no_auth(client):
    """Missing Authorization header returns 422."""
    resp = await client.get("/v1/events")
    assert resp.status_code == 422
