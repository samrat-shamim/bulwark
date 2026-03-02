"""Tests for alert rule CRUD."""

import pytest


def _make_rule(**overrides):
    rule = {
        "name": "Test Rule",
        "description": "A test alert rule",
        "condition": {
            "metric": "events_per_minute",
            "operator": ">",
            "threshold": 100,
            "window_seconds": 60,
        },
        "actions": [{"type": "dashboard_notification"}],
        "scope": {},
        "cooldown_seconds": 300,
        "enabled": True,
    }
    rule.update(overrides)
    return rule


# --- Create Rule ---


async def test_create_rule(client, auth_headers):
    resp = await client.post(
        "/v1/rules", json=_make_rule(), headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Rule"
    assert "id" in data


async def test_create_rule_no_auth(client):
    resp = await client.post("/v1/rules", json=_make_rule())
    assert resp.status_code == 422


# --- List Rules ---


async def test_list_rules(client, auth_headers):
    await client.post("/v1/rules", json=_make_rule(name="Rule A"), headers=auth_headers)
    await client.post("/v1/rules", json=_make_rule(name="Rule B"), headers=auth_headers)

    resp = await client.get("/v1/rules", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    names = [r["name"] for r in data["rules"]]
    assert "Rule A" in names
    assert "Rule B" in names


# --- Get Single Rule ---


async def test_get_rule(client, auth_headers):
    create_resp = await client.post(
        "/v1/rules", json=_make_rule(name="Get Me"), headers=auth_headers
    )
    rule_id = create_resp.json()["id"]

    resp = await client.get(f"/v1/rules/{rule_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Get Me"


async def test_get_rule_not_found(client, auth_headers):
    resp = await client.get("/v1/rules/nonexistent-id", headers=auth_headers)
    assert resp.status_code == 404


# --- Update Rule ---


async def test_update_rule(client, auth_headers):
    create_resp = await client.post(
        "/v1/rules", json=_make_rule(name="Old Name"), headers=auth_headers
    )
    rule_id = create_resp.json()["id"]

    resp = await client.put(
        f"/v1/rules/{rule_id}",
        json={"name": "New Name", "cooldown_seconds": 600},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


async def test_update_rule_not_found(client, auth_headers):
    resp = await client.put(
        "/v1/rules/nonexistent",
        json={"name": "Whatever"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


# --- Delete Rule ---


async def test_delete_rule(client, auth_headers):
    create_resp = await client.post(
        "/v1/rules", json=_make_rule(name="Delete Me"), headers=auth_headers
    )
    rule_id = create_resp.json()["id"]

    resp = await client.delete(f"/v1/rules/{rule_id}", headers=auth_headers)
    assert resp.status_code == 200

    # Verify gone
    get_resp = await client.get(f"/v1/rules/{rule_id}", headers=auth_headers)
    assert get_resp.status_code == 404


# --- Toggle Rule ---


async def test_toggle_rule(client, auth_headers):
    create_resp = await client.post(
        "/v1/rules", json=_make_rule(enabled=True), headers=auth_headers
    )
    rule_id = create_resp.json()["id"]

    # Toggle off
    resp = await client.post(f"/v1/rules/{rule_id}/toggle", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["enabled"] is False

    # Toggle back on
    resp = await client.post(f"/v1/rules/{rule_id}/toggle", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["enabled"] is True
