"""Tests for waitlist / early access signup."""


async def test_join_waitlist(client):
    resp = await client.post(
        "/v1/waitlist",
        json={"email": "test@example.com", "name": "Test User", "company": "TestCo"},
    )
    assert resp.status_code == 201
    assert "message" in resp.json()


async def test_join_waitlist_email_only(client):
    resp = await client.post(
        "/v1/waitlist",
        json={"email": "minimal@example.com"},
    )
    assert resp.status_code == 201


async def test_join_waitlist_duplicate_email(client):
    await client.post("/v1/waitlist", json={"email": "dupe@example.com"})
    resp = await client.post("/v1/waitlist", json={"email": "dupe@example.com"})
    # Should succeed silently (idempotent)
    assert resp.status_code in (200, 201)
    assert "message" in resp.json()


async def test_join_waitlist_invalid_email(client):
    resp = await client.post(
        "/v1/waitlist",
        json={"email": "not-an-email"},
    )
    assert resp.status_code == 422


async def test_join_waitlist_no_auth_required(client):
    """Waitlist signup is a public endpoint."""
    resp = await client.post(
        "/v1/waitlist",
        json={"email": "public@example.com"},
    )
    assert resp.status_code == 201


async def test_list_waitlist(client, auth_headers):
    # Add some entries
    await client.post("/v1/waitlist", json={"email": "a@example.com", "name": "Alice"})
    await client.post("/v1/waitlist", json={"email": "b@example.com", "company": "BigCo"})

    resp = await client.get("/v1/waitlist", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["entries"]) == 2
    emails = [e["email"] for e in data["entries"]]
    assert "a@example.com" in emails
    assert "b@example.com" in emails


async def test_list_waitlist_requires_auth(client):
    resp = await client.get("/v1/waitlist")
    assert resp.status_code == 422
