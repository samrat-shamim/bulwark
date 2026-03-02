"""Tests for the health endpoint."""


async def test_health_returns_ok(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


async def test_health_no_auth_required(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
