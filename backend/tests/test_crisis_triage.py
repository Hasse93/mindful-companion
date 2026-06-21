"""Tests for the safety-critical crisis triage.

These are the most important tests in the suite: a regression here could mean a
person in distress is not shown crisis resources. We bias toward over-detection.
"""
from __future__ import annotations

import pytest

from app.ml.crisis_triage import TriageLevel, assess


@pytest.mark.parametrize(
    "text",
    [
        "I want to kill myself",
        "I just want to end it all",
        "sometimes I think the world is better off without me",
        "I've been thinking about suicide",
        "I can't go on anymore",
        "I keep cutting myself",
        "There's no reason to live",
    ],
)
def test_explicit_self_harm_is_crisis(text):
    result = assess(text)
    assert result.level is TriageLevel.CRISIS
    assert result.resources, "crisis must always return resources"
    assert result.matched_signals


@pytest.mark.parametrize(
    "text",
    [
        "I feel so hopeless lately",
        "I think I'm worthless",
        "I just want to give up",
        "I feel so alone",
    ],
)
def test_soft_distress_is_elevated(text):
    result = assess(text)
    assert result.level is TriageLevel.ELEVATED


@pytest.mark.parametrize(
    "text",
    [
        "I had a great day at the park today!",
        "Feeling pretty good after my run.",
        "Just checking in, nothing much going on.",
    ],
)
def test_neutral_text_is_none(text):
    assert assess(text).level is TriageLevel.NONE


def test_strong_negative_emotion_raises_to_elevated():
    result = assess(
        "today was rough",
        emotion_label="sadness",
        emotion_score=0.95,
    )
    assert result.level is TriageLevel.ELEVATED


def test_low_confidence_emotion_does_not_escalate():
    result = assess("today was rough", emotion_label="sadness", emotion_score=0.4)
    assert result.level is TriageLevel.NONE


def test_empty_text_is_none():
    assert assess("").level is TriageLevel.NONE
    assert assess("   ").level is TriageLevel.NONE
