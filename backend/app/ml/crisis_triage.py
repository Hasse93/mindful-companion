"""Crisis safety triage.

This is the most safety-critical module in the project. It is deliberately
*not* a clinical risk classifier. It is a high-recall rule layer that detects
language suggesting self-harm or suicidal ideation and routes the user to
professional crisis resources. It never diagnoses, never scores "risk", and
never contacts anyone automatically.

Design principles:
  * High recall over precision — a false positive shows a help banner, a false
    negative could miss someone in distress. We accept extra banners.
  * Transparent — every decision lists which signals matched, so behaviour is
    auditable and testable.
  * Conservative escalation — an explicit self-harm phrase is always CRISIS,
    regardless of the ML emotion signal.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class TriageLevel(str, Enum):
    NONE = "none"
    ELEVATED = "elevated"   # strong negative affect; offer gentle support
    CRISIS = "crisis"       # possible self-harm; surface crisis resources now


# Explicit, high-confidence self-harm / suicidal-ideation phrases.
# Word boundaries keep these from matching inside unrelated words.
_CRISIS_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\bkill (myself|me)\b",
        r"\bend (my|it all|my life)\b",
        r"\b(want|wanna|going) to die\b",
        r"\bdon'?t want to (be alive|live|exist)\b",
        r"\bno reason to live\b",
        r"\b(take|taking|end) my (own )?life\b",
        r"\bsuicid(e|al)\b",
        r"\bharm(ing)? myself\b",
        r"\bself[- ]?harm\b",
        r"\bcut(ting)? myself\b",
        r"\bbetter off (dead|without me)\b",
        r"\bcan'?t go on\b",
        r"\bnothing to live for\b",
    )
]

# Softer distress phrases that, on their own, mean ELEVATED rather than CRISIS.
_ELEVATED_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\bhopeless\b",
        r"\bworthless\b",
        r"\bcan'?t cope\b",
        r"\bgive up\b",
        r"\bso alone\b",
        r"\bunbearable\b",
        r"\bhate myself\b",
    )
]

# Emotion labels (from the ML classifier) that nudge toward ELEVATED when paired
# with high confidence.
_NEGATIVE_EMOTIONS = {"sadness", "fear", "grief", "anger", "disgust"}


# US-centric defaults; localise per deployment region. Kept in code (not the DB)
# so they can never be empty when a crisis is detected.
CRISIS_RESOURCES: list[dict[str, str]] = [
    {
        "name": "988 Suicide & Crisis Lifeline (US)",
        "contact": "Call or text 988",
        "url": "https://988lifeline.org",
    },
    {
        "name": "Crisis Text Line",
        "contact": "Text HOME to 741741",
        "url": "https://www.crisistextline.org",
    },
    {
        "name": "International Association for Suicide Prevention",
        "contact": "Find a crisis centre near you",
        "url": "https://www.iasp.info/resources/Crisis_Centres/",
    },
]


@dataclass
class TriageResult:
    level: TriageLevel
    matched_signals: list[str] = field(default_factory=list)
    resources: list[dict[str, str]] = field(default_factory=list)

    @property
    def is_crisis(self) -> bool:
        return self.level is TriageLevel.CRISIS


def assess(
    text: str,
    *,
    emotion_label: str | None = None,
    emotion_score: float | None = None,
) -> TriageResult:
    """Assess a piece of user text for crisis signals.

    Args:
        text: the user's message or journal note.
        emotion_label: optional ML emotion label to incorporate.
        emotion_score: confidence (0..1) of that emotion.

    Returns:
        TriageResult with the escalation level, the signals that matched, and
        crisis resources (only populated at CRISIS level).
    """
    if not text or not text.strip():
        return TriageResult(level=TriageLevel.NONE)

    matched: list[str] = []

    # 1. Explicit self-harm language -> always CRISIS.
    for pat in _CRISIS_PATTERNS:
        m = pat.search(text)
        if m:
            matched.append(m.group(0).lower())
    if matched:
        return TriageResult(
            level=TriageLevel.CRISIS,
            matched_signals=sorted(set(matched)),
            resources=CRISIS_RESOURCES,
        )

    # 2. Softer distress language -> ELEVATED.
    for pat in _ELEVATED_PATTERNS:
        m = pat.search(text)
        if m:
            matched.append(m.group(0).lower())

    # 3. Strong negative emotion from the ML model also raises to ELEVATED.
    if (
        emotion_label
        and emotion_label.lower() in _NEGATIVE_EMOTIONS
        and (emotion_score or 0) >= 0.85
    ):
        matched.append(f"emotion:{emotion_label.lower()}")

    if matched:
        return TriageResult(
            level=TriageLevel.ELEVATED,
            matched_signals=sorted(set(matched)),
            # Elevated does not push hotlines, but does offer them as support.
            resources=CRISIS_RESOURCES,
        )

    return TriageResult(level=TriageLevel.NONE)
