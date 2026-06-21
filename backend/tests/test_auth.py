"""Auth tests: registration, login, and access enforcement."""
from __future__ import annotations


def test_register_and_login(anon_client):
    r = anon_client.post(
        "/auth/register", json={"email": "a@example.com", "password": "hunter2pass"}
    )
    assert r.status_code == 201
    assert r.json()["email"] == "a@example.com"

    r = anon_client.post(
        "/auth/login", json={"email": "a@example.com", "password": "hunter2pass"}
    )
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_duplicate_email_rejected(anon_client):
    body = {"email": "dup@example.com", "password": "hunter2pass"}
    assert anon_client.post("/auth/register", json=body).status_code == 201
    assert anon_client.post("/auth/register", json=body).status_code == 409


def test_wrong_password_rejected(anon_client):
    anon_client.post(
        "/auth/register", json={"email": "b@example.com", "password": "correctpass"}
    )
    r = anon_client.post(
        "/auth/login", json={"email": "b@example.com", "password": "wrongpass"}
    )
    assert r.status_code == 401


def test_weak_password_rejected(anon_client):
    r = anon_client.post("/auth/register", json={"email": "c@example.com", "password": "short"})
    assert r.status_code == 422


def test_protected_route_requires_token(anon_client):
    assert anon_client.get("/mood").status_code == 403  # no Bearer credentials


def test_invalid_token_rejected(anon_client):
    r = anon_client.get("/mood", headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401


def test_authenticated_user_sees_only_their_data(client, anon_client):
    # `client` (test@example.com) creates a mood entry.
    client.post("/mood", json={"mood_score": 4})

    # A different user should not see it.
    anon_client.post("/auth/register", json={"email": "other@example.com", "password": "secret123"})
    token = anon_client.post(
        "/auth/login", json={"email": "other@example.com", "password": "secret123"}
    ).json()["access_token"]
    other = anon_client.get("/mood", headers={"Authorization": f"Bearer {token}"})
    assert other.status_code == 200
    assert other.json() == []
