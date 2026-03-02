"""Tests for alert listing and acknowledgement."""

import pytest
import uuid
from datetime import datetime, timezone

from app.db import Alert, AlertRule, SessionRecord
import app.db as db_module


async def _seed_alert(setup_db):
    """Seed a session, alert rule, and fired alert directly in the DB."""
    async with setup_db() as session:
        # Need a session record for the FK
        sess = SessionRecord(
            id="sess_alert_1",
            agent_id="test_agent_id",
            environment="test",
        )
        session.add(sess)
        await session.flush()

        rule = AlertRule(
            id="rule_test_1",
            agent_id="test_agent_id",
            name="Test Rule",
            description="Test rule",
            enabled=True,
            condition={"metric": "events_per_minute", "operator": ">", "threshold": 10, "window_seconds": 60},
            actions=[{"type": "alert"}],
            scope={},
            cooldown_seconds=300,
        )
        session.add(rule)
        await session.flush()

        alert = Alert(
            id="alert_test_1",
            rule_id="rule_test_1",
            session_id="sess_alert_1",
            agent_name="test-agent",
            metric_value=25.0,
            threshold=10.0,
            actions_taken=["alert"],
            acknowledged=False,
        )
        session.add(alert)
        await session.commit()


# --- List Alerts ---


async def test_list_alerts(client, auth_headers, setup_db):
    await _seed_alert(setup_db)

    resp = await client.get("/v1/alerts", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["alerts"]) >= 1
    assert data["alerts"][0]["id"] == "alert_test_1"


async def test_list_alerts_no_auth(client):
    resp = await client.get("/v1/alerts")
    assert resp.status_code == 422


# --- Unread Count ---


async def test_unread_alerts_count(client, auth_headers, setup_db):
    await _seed_alert(setup_db)

    resp = await client.get("/v1/alerts/unread", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["unread"] >= 1


# --- Acknowledge Alert ---


async def test_acknowledge_alert(client, auth_headers, setup_db):
    await _seed_alert(setup_db)

    resp = await client.post("/v1/alerts/alert_test_1/ack", headers=auth_headers)
    assert resp.status_code == 200

    # Verify unread count decreased
    unread_resp = await client.get("/v1/alerts/unread", headers=auth_headers)
    assert unread_resp.json()["unread"] == 0


async def test_acknowledge_alert_not_found(client, auth_headers):
    resp = await client.post("/v1/alerts/nonexistent/ack", headers=auth_headers)
    assert resp.status_code == 404
