"""End-to-end API tests (FAKE_AI stubs, in-memory DB)."""
from __future__ import annotations


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_analyze_returns_full_pipeline(client):
    r = client.post("/analyze", json={"text": "I feel sad and lonely today"})
    assert r.status_code == 200
    body = r.json()
    assert body["sentiment_label"] in {"POSITIVE", "NEGATIVE", "NEUTRAL"}
    assert body["emotion_label"]
    assert body["triage_level"] in {"none", "elevated", "crisis"}


def test_crisis_check_surfaces_resources(client):
    r = client.post("/crisis/check", json={"text": "I want to kill myself"})
    assert r.status_code == 200
    body = r.json()
    assert body["level"] == "crisis"
    assert len(body["resources"]) >= 1


def test_mood_create_and_list(client):
    created = client.post("/mood", json={"mood_score": 4, "note": "good day"})
    assert created.status_code == 201
    assert created.json()["emotion_label"]  # note was analysed

    listed = client.get("/mood")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_mood_score_validation(client):
    assert client.post("/mood", json={"mood_score": 9}).status_code == 422


def test_chat_streams_sse(client):
    r = client.post("/chat", json={"message": "hello"})
    assert r.status_code == 200
    assert "text/event-stream" in r.headers["content-type"]
    assert "event: done" in r.text


def test_chat_crisis_emits_resources(client):
    r = client.post("/chat", json={"message": "I want to end my life"})
    assert "event: triage" in r.text
    assert "988" in r.text  # crisis resources surfaced in the stream


def test_journal_create_and_list(client):
    created = client.post(
        "/journal",
        json={"kind": "gratitude", "prompt": "What went well?", "content": "A good walk"},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["kind"] == "gratitude"
    assert body["emotion_label"]  # ML-enriched

    listed = client.get("/journal", params={"kind": "gratitude"})
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_journal_kind_validation(client):
    assert client.post("/journal", json={"kind": "invalid", "content": "x"}).status_code == 422


def test_weekly_report(client):
    client.post("/mood", json={"mood_score": 2, "note": "rough week, feeling down"})
    r = client.get("/report/weekly")
    assert r.status_code == 200
    assert r.json()["entry_count"] == 1
    assert r.json()["summary"]
