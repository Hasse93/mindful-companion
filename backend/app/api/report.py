"""/report/weekly — aggregate the past week's mood data and summarise with Claude."""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.deps import current_user
from app.database import get_session
from app.llm import claude_client
from app.llm.prompts import weekly_report_prompt
from app.models import MoodEntry
from app.schemas import EmotionCount, WeeklyReport

router = APIRouter(prefix="/report", tags=["report"])


@router.get("/weekly", response_model=WeeklyReport)
def weekly(
    user_id: str = Depends(current_user),
    session: Session = Depends(get_session),
) -> WeeklyReport:
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7)

    entries = list(session.exec(
        select(MoodEntry)
        .where(MoodEntry.user_id == user_id)
        .where(MoodEntry.created_at >= start)
    ).all())

    count = len(entries)
    avg_mood = round(sum(e.mood_score for e in entries) / count, 2) if count else None

    sentiments = [e.sentiment_label for e in entries if e.sentiment_label]
    pos_ratio = (
        round(sum(1 for s in sentiments if s == "POSITIVE") / len(sentiments), 2)
        if sentiments else None
    )

    emo_counter = Counter(e.emotion_label for e in entries if e.emotion_label)
    distribution = [EmotionCount(label=k, count=v) for k, v in emo_counter.most_common()]

    stats = {
        "entry_count": count,
        "average_mood_1_to_5": avg_mood,
        "positive_sentiment_ratio": pos_ratio,
        "emotion_distribution": {k: v for k, v in emo_counter.items()},
    }
    summary = claude_client.complete(weekly_report_prompt(json.dumps(stats, indent=2)))

    return WeeklyReport(
        period_start=start,
        period_end=now,
        entry_count=count,
        average_mood=avg_mood,
        positive_ratio=pos_ratio,
        emotion_distribution=distribution,
        summary=summary,
    )
