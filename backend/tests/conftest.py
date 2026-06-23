"""Test fixtures: in-memory SQLite DB + FAKE_AI so no models/keys are needed."""
from __future__ import annotations

import os

os.environ["FAKE_AI"] = "true"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["RATE_LIMIT_ENABLED"] = "false"  # don't throttle the test suite

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel
from sqlmodel.pool import StaticPool

import app.database as database
from sqlmodel import create_engine


@pytest.fixture(autouse=True)
def _fresh_db(monkeypatch):
    # One shared in-memory engine for the whole test (StaticPool keeps it alive).
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr(database, "engine", engine)
    from app import models  # noqa: F401

    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client():
    """An authenticated client: registers + logs in a test user and sets the
    Bearer token as a default header so endpoint tests need no extra setup."""
    from app.main import app

    with TestClient(app) as c:
        c.post("/auth/register", json={"email": "test@example.com", "password": "secret123"})
        token = c.post(
            "/auth/login", json={"email": "test@example.com", "password": "secret123"}
        ).json()["access_token"]
        c.headers.update({"Authorization": f"Bearer {token}"})
        yield c


@pytest.fixture
def anon_client():
    """An unauthenticated client (no token) for testing auth enforcement."""
    from app.main import app

    with TestClient(app) as c:
        yield c
