"""/chat — streaming companion chat with an inline safety triage gate.

Flow per user message:
  1. Persist the user turn (with its triage level).
  2. Run crisis triage on the message.
  3. Stream Claude's reply via SSE; if triage == CRISIS, steer the model to
     surface crisis resources and emit a structured `resources` SSE event.
  4. Persist the assistant turn after the stream completes.
"""
from __future__ import annotations

import json
from collections.abc import Iterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from app.api.deps import current_user
from app.database import get_session
from app.llm import claude_client
from app.ml import crisis_triage, emotion
from app.models import ChatMessage
from app.schemas import ChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])


def _sse(event: str, data: dict | str) -> str:
    payload = data if isinstance(data, str) else json.dumps(data)
    return f"event: {event}\ndata: {payload}\n\n"


@router.post("")
def chat(
    body: ChatRequest,
    user_id: str = Depends(current_user),
    session: Session = Depends(get_session),
) -> StreamingResponse:
    # 1. Triage the incoming message (emotion signal feeds the triage).
    emo = emotion.classify(body.message)
    triage = crisis_triage.assess(
        body.message,
        emotion_label=str(emo["label"]),
        emotion_score=float(emo["score"]),
    )

    # 2. Persist the user turn.
    user_turn = ChatMessage(
        user_id=user_id,
        role="user",
        content=body.message,
        triage_level=triage.level.value,
    )
    session.add(user_turn)
    session.commit()

    # 3. Build short history for context (last 10 turns).
    history_rows = session.exec(
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at.desc())  # type: ignore[attr-defined]
        .limit(10)
    ).all()
    history = [
        {"role": r.role, "content": r.content} for r in reversed(history_rows)
    ]

    def event_stream() -> Iterator[str]:
        # Emit triage metadata first so the UI can render a help banner immediately.
        yield _sse("triage", {
            "level": triage.level.value,
            "resources": triage.resources,
        })

        chunks: list[str] = []
        for chunk in claude_client.stream_reply(history, is_crisis=triage.is_crisis):
            chunks.append(chunk)
            yield _sse("message", {"text": chunk})

        # 4. Persist the assistant turn. We need a fresh session because the
        # request-scoped one closes when the generator is still running.
        from app.database import engine
        with Session(engine) as s:
            s.add(ChatMessage(user_id=user_id, role="assistant", content="".join(chunks)))
            s.commit()

        yield _sse("done", {"ok": True})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
