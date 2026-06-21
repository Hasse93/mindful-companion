"""/mood — create and list mood check-ins. Notes are run through the ML pipeline."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.analyze import run_pipeline
from app.api.deps import current_user
from app.database import get_session
from app.models import MoodEntry
from app.schemas import MoodCreate, MoodRead

router = APIRouter(prefix="/mood", tags=["mood"])


@router.post("", response_model=MoodRead, status_code=201)
def create_mood(
    body: MoodCreate,
    user_id: str = Depends(current_user),
    session: Session = Depends(get_session),
) -> MoodEntry:
    entry = MoodEntry(user_id=user_id, mood_score=body.mood_score, note=body.note)

    # Enrich with ML signals when a note is provided.
    if body.note and body.note.strip():
        analysis = run_pipeline(body.note)
        entry.sentiment_label = analysis.sentiment_label
        entry.sentiment_score = analysis.sentiment_score
        entry.emotion_label = analysis.emotion_label
        entry.emotion_score = analysis.emotion_score

    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.get("", response_model=list[MoodRead])
def list_moods(
    limit: int = 50,
    user_id: str = Depends(current_user),
    session: Session = Depends(get_session),
) -> list[MoodEntry]:
    stmt = (
        select(MoodEntry)
        .where(MoodEntry.user_id == user_id)
        .order_by(MoodEntry.created_at.desc())  # type: ignore[attr-defined]
        .limit(limit)
    )
    return list(session.exec(stmt).all())
