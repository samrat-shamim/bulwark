"""Tests for agent listing endpoint."""

import pytest
import uuid
from datetime import datetime, timezone


def _make_event(session_id="sess_agent_1"):
    return {
        "event_id": f"evt_{uuid.uuid4().hex[:12]}",
        "session_id": session_id,
        "agent_name": "test-agent",
        "environment": "test",
        "event_type": "tool_call",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration_ms": 100,
        "status": "success",
        "tool_name": "test_tool",
    }


async def test_list_agents(client, auth_headers):
    # Ingest an event so the agent has activity
    await client.post(
        "/v1/events/batch",
        json={"events": [_make_event()]},
        headers=auth_headers,
    )

    resp = await client.get("/v1/agents", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["agents"]) >= 1
    agent = data["agents"][0]
    assert "id" in agent
    assert "name" in agent


async def test_list_agents_no_auth(client):
    resp = await client.get("/v1/agents")
    assert resp.status_code == 422


async def test_rotate_api_key(client, auth_headers):
    resp = await client.post("/v1/agents/rotate-key", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["api_key"].startswith("bwk_")
    assert "warning" in data

    # Old key should no longer work
    old_resp = await client.get("/v1/agents", headers=auth_headers)
    assert old_resp.status_code == 401

    # New key should work
    new_headers = {"Authorization": f"Bearer {data['api_key']}"}
    new_resp = await client.get("/v1/agents", headers=new_headers)
    assert new_resp.status_code == 200
