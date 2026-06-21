"""/journal — create and list journal & gratitude entries (ML-enriched)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.api.analyze import run_pipeline
from app.api.deps import current_user
from app.database import get_session
from app.models import JournalEntry
from app.schemas import JournalCreate, JournalRead

router = APIRouter(prefix="/journal", tags=["journal"])


@router.post("", response_model=JournalRead, status_code=201)
def create_entry(
    body: JournalCreate,
    user_id: str = Depends(current_user),
    session: Session = Depends(get_session),
) -> JournalEntry:
    entry = JournalEntry(
        user_id=user_id, kind=body.kind, prompt=body.prompt, content=body.content
    )
    analysis = run_pipeline(body.content)
    entry.emotion_label = analysis.emotion_label
    entry.sentiment_label = analysis.sentiment_label

    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.get("", response_model=list[JournalRead])
def list_entries(
    kind: str | None = Query(default=None),
    limit: int = 50,
    user_id: str = Depends(current_user),
    session: Session = Depends(get_session),
) -> list[JournalEntry]:
    stmt = select(JournalEntry).where(JournalEntry.user_id == user_id)
    if kind:
        stmt = stmt.where(JournalEntry.kind == kind)
    stmt = stmt.order_by(JournalEntry.created_at.desc()).limit(limit)  # type: ignore[attr-defined]
    return list(session.exec(stmt).all())
