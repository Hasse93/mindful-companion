"""/chat — streaming companion chat with an inline safety triage gate.

Flow per user message:
  1. Persist the user turn (with its triage level).
  2. Run crisis triage on the message.
  3. Stream the reply via SSE; if triage == CRISIS, steer the model to surface
     crisis resources and emit a structured `triage` SSE event.
  4. Persist the assistant turn after the stream completes.

The shared read-only demo account is exempt from persistence: its chat works
but nothing is saved, so concurrent visitors can't pollute each other's context.
"""
from __future__ import annotations

import json
from collections.abc import Iterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from app.auth import AuthUser, current_auth
from app.database import get_session
from app.llm import provider as llm
from app.ml import crisis_triage, emotion
from app.models import ChatMessage
from app.ratelimit import rate_limit
from app.schemas import ChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])


def _sse(event: str, data: dict | str) -> str:
    payload = data if isinstance(data, str) else json.dumps(data)
    return f"event: {event}\ndata: {payload}\n\n"


@router.post("", dependencies=[Depends(rate_limit("15/minute"))])
def chat(
    body: ChatRequest,
    auth: AuthUser = Depends(current_auth),
    session: Session = Depends(get_session),
) -> StreamingResponse:
    user_id = auth.id
    persist = not auth.is_demo

    # 1. Triage the incoming message (emotion signal feeds the triage).
    emo = emotion.classify(body.message)
    triage = crisis_triage.assess(
        body.message,
        emotion_label=str(emo["label"]),
        emotion_score=float(emo["score"]),
    )

    if persist:
        # Persist the user turn, then build short context (last 10 turns).
        session.add(ChatMessage(
            user_id=user_id, role="user", content=body.message,
            triage_level=triage.level.value,
        ))
        session.commit()
        history_rows = session.exec(
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.desc())  # type: ignore[attr-defined]
            .limit(10)
        ).all()
        history = [{"role": r.role, "content": r.content} for r in reversed(history_rows)]
    else:
        # Demo: standalone, nothing saved.
        history = [{"role": "user", "content": body.message}]

    def event_stream() -> Iterator[str]:
        yield _sse("triage", {"level": triage.level.value, "resources": triage.resources})

        chunks: list[str] = []
        for chunk in llm.stream_reply(history, is_crisis=triage.is_crisis):
            chunks.append(chunk)
            yield _sse("message", {"text": chunk})

        if persist:
            from app.database import engine
            with Session(engine) as s:
                s.add(ChatMessage(user_id=user_id, role="assistant", content="".join(chunks)))
                s.commit()

        yield _sse("done", {"ok": True})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
