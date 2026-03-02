"""Tests for stats endpoint."""

import pytest
import uuid
from datetime import datetime, timezone


async def test_stats(client, auth_headers):
    # Seed some activity
    event = {
        "event_id": f"evt_{uuid.uuid4().hex[:12]}",
        "session_id": "sess_stats",
        "agent_name": "test-agent",
        "environment": "test",
        "event_type": "tool_call",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration_ms": 100,
        "status": "success",
        "tool_name": "test_tool",
    }
    await client.post(
        "/v1/events/batch",
        json={"events": [event]},
        headers=auth_headers,
    )

    resp = await client.get("/v1/stats", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "active_sessions" in data
    assert "total_agents" in data
    assert "events_per_minute" in data


async def test_stats_no_auth(client):
    resp = await client.get("/v1/stats")
    assert resp.status_code == 422
