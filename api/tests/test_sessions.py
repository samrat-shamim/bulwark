"""Tests for session CRUD and kill switch."""

import pytest
import uuid
from datetime import datetime, timezone


def _make_event(session_id="sess_kill_1", event_type="tool_call"):
    return {
        "event_id": f"evt_{uuid.uuid4().hex[:12]}",
        "session_id": session_id,
        "agent_name": "test-agent",
        "environment": "test",
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration_ms": 100,
        "status": "success",
        "tool_name": "test_tool",
    }


async def _seed_session(client, auth_headers, session_id="sess_test"):
    """Helper: ingest an event so the session exists."""
    await client.post(
        "/v1/events/batch",
        json={"events": [_make_event(session_id=session_id)]},
        headers=auth_headers,
    )


# --- List Sessions ---


async def test_list_sessions(client, auth_headers):
    await _seed_session(client, auth_headers, "sess_list_1")
    await _seed_session(client, auth_headers, "sess_list_2")

    resp = await client.get("/v1/sessions", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    ids = [s["id"] for s in data["sessions"]]
    assert "sess_list_1" in ids
    assert "sess_list_2" in ids


async def test_list_sessions_no_auth(client):
    resp = await client.get("/v1/sessions")
    assert resp.status_code == 422


# --- Session Detail ---


async def test_session_detail(client, auth_headers):
    await _seed_session(client, auth_headers, "sess_detail")

    resp = await client.get("/v1/sessions/sess_detail", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["session"]["id"] == "sess_detail"
    assert "events" in data


async def test_session_detail_not_found(client, auth_headers):
    resp = await client.get("/v1/sessions/nonexistent", headers=auth_headers)
    assert resp.status_code == 404


# --- Session Status (Kill Switch Polling) ---


async def test_session_status_alive(client, auth_headers):
    await _seed_session(client, auth_headers, "sess_alive")

    # No auth needed for status check
    resp = await client.get("/v1/sessions/sess_alive/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_id"] == "sess_alive"
    assert data["killed"] is False


async def test_session_status_no_auth_required(client, auth_headers):
    await _seed_session(client, auth_headers, "sess_noauth")
    resp = await client.get("/v1/sessions/sess_noauth/status")
    assert resp.status_code == 200


# --- Kill Session ---


async def test_kill_session(client, auth_headers):
    await _seed_session(client, auth_headers, "sess_to_kill")

    resp = await client.post("/v1/sessions/sess_to_kill/kill", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_id"] == "sess_to_kill"
    assert "killed_at" in data

    # Verify status reflects kill
    status_resp = await client.get("/v1/sessions/sess_to_kill/status")
    assert status_resp.json()["killed"] is True


async def test_kill_session_no_auth(client, auth_headers):
    await _seed_session(client, auth_headers, "sess_kill_noauth")
    resp = await client.post("/v1/sessions/sess_kill_noauth/kill")
    assert resp.status_code == 422


async def test_kill_session_not_found(client, auth_headers):
    resp = await client.post("/v1/sessions/nonexistent/kill", headers=auth_headers)
    assert resp.status_code == 404


async def test_kill_session_idempotent(client, auth_headers):
    await _seed_session(client, auth_headers, "sess_double_kill")

    resp1 = await client.post("/v1/sessions/sess_double_kill/kill", headers=auth_headers)
    resp2 = await client.post("/v1/sessions/sess_double_kill/kill", headers=auth_headers)

    assert resp1.status_code == 200
    assert resp2.status_code == 200
