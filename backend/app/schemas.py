"""Pydantic request/response schemas (the typed API boundary).

These are the source of truth for the OpenAPI spec, from which the frontend's
TypeScript client is generated — so the two ends never drift.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# --- Auth ---
class RegisterRequest(BaseModel):
    # Basic email shape check — avoids the email-validator dependency.
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=255)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(max_length=128)


class UserRead(BaseModel):
    id: int
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Analysis ---
class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class AnalyzeResponse(BaseModel):
    sentiment_label: str
    sentiment_score: float
    emotion_label: str
    emotion_score: float
    triage_level: str
    matched_signals: list[str] = []
    resources: list[dict[str, str]] = []


# --- Mood ---
class MoodCreate(BaseModel):
    mood_score: int = Field(ge=1, le=5)
    note: str | None = Field(default=None, max_length=4000)


class MoodRead(BaseModel):
    id: int
    mood_score: int
    note: str | None
    sentiment_label: str | None
    sentiment_score: float | None
    emotion_label: str | None
    emotion_score: float | None
    created_at: datetime


# --- Chat ---
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


# --- Journal / gratitude ---
class JournalCreate(BaseModel):
    kind: str = Field(default="journal", pattern="^(journal|gratitude)$")
    prompt: str | None = Field(default=None, max_length=500)
    content: str = Field(min_length=1, max_length=8000)


class JournalRead(BaseModel):
    id: int
    kind: str
    prompt: str | None
    content: str
    emotion_label: str | None
    sentiment_label: str | None
    created_at: datetime


# --- Crisis ---
class CrisisCheckRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class CrisisCheckResponse(BaseModel):
    level: str
    matched_signals: list[str]
    resources: list[dict[str, str]]


# --- Weekly report ---
class EmotionCount(BaseModel):
    label: str
    count: int


class WeeklyReport(BaseModel):
    period_start: datetime
    period_end: datetime
    entry_count: int
    average_mood: float | None
    positive_ratio: float | None
    emotion_distribution: list[EmotionCount]
    summary: str
