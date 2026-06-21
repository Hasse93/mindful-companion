"""Persistence models (SQLModel ORM tables).

Auth is intentionally out of scope for the first build: every row carries a
`user_id` string (defaults to "demo") so multi-user/JWT can be layered on later
without a schema change.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    """A registered account. Rows in other tables reference this by `str(id)`."""

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=_utcnow)


class MoodEntry(SQLModel, table=True):
    """A point-in-time mood check-in, optionally with a free-text note that is
    run through the ML pipeline."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(default="demo", index=True)
    # 1 (very low) .. 5 (very good) — the user's self-reported score.
    mood_score: int = Field(ge=1, le=5)
    note: str | None = None
    # Outputs of the ML pipeline (nullable until analysis runs).
    sentiment_label: str | None = None       # POSITIVE / NEGATIVE / NEUTRAL
    sentiment_score: float | None = None      # confidence 0..1
    emotion_label: str | None = None          # joy / sadness / anger / ...
    emotion_score: float | None = None
    created_at: datetime = Field(default_factory=_utcnow, index=True)


class ChatMessage(SQLModel, table=True):
    """A single turn in a conversation with the companion."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(default="demo", index=True)
    role: str  # "user" | "assistant"
    content: str
    # Safety triage level recorded for user turns: none / elevated / crisis.
    triage_level: str | None = None
    created_at: datetime = Field(default_factory=_utcnow, index=True)


class JournalEntry(SQLModel, table=True):
    """A free-form journal entry or a gratitude note."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(default="demo", index=True)
    kind: str = Field(default="journal")  # "journal" | "gratitude"
    prompt: str | None = None             # the prompt the entry responded to
    content: str
    # The journal text is also run through the emotion/sentiment pipeline.
    emotion_label: str | None = None
    sentiment_label: str | None = None
    created_at: datetime = Field(default_factory=_utcnow, index=True)
