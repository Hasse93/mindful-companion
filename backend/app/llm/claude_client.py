"""Thin wrapper around the Anthropic Claude API.

Exposes a streaming chat generator (for SSE) and a one-shot completion (for the
weekly report). When `FAKE_AI=true` or no API key is set, deterministic stub
responses are returned so the app and tests run with no network or key.
"""
from __future__ import annotations

from collections.abc import Iterator

from app.config import get_settings
from app.llm.prompts import COMPANION_SYSTEM_PROMPT, CRISIS_STEER


def _client():
    from anthropic import Anthropic

    return Anthropic(api_key=get_settings().anthropic_api_key)


def _use_fake() -> bool:
    s = get_settings()
    return s.fake_ai or not s.anthropic_api_key


def stream_reply(
    history: list[dict[str, str]],
    *,
    is_crisis: bool = False,
) -> Iterator[str]:
    """Yield assistant reply text chunks for an SSE stream.

    Args:
        history: list of {"role": "user"|"assistant", "content": str}.
        is_crisis: when True, prepend crisis-steering guidance to the system
            prompt so the model surfaces resources.
    """
    system = COMPANION_SYSTEM_PROMPT
    if is_crisis:
        system = system + "\n\n" + CRISIS_STEER

    if _use_fake():
        yield from _fake_stream(is_crisis)
        return

    settings = get_settings()
    with _client().messages.stream(
        model=settings.chat_model,
        max_tokens=600,
        system=system,
        messages=history,
    ) as stream:
        for text in stream.text_stream:
            yield text


def complete(prompt: str, *, model: str | None = None) -> str:
    """One-shot completion (non-streaming), used for the weekly report."""
    if _use_fake():
        return (
            "This week shows a mix of ups and downs, which is completely human. "
            "Your check-ins suggest some heavier moments alongside lighter ones. "
            "A gentle invitation for the week ahead: try a few minutes of "
            "grounding when things feel heavy, and reach out to someone you "
            "trust. This reflection is a supportive note, not professional care."
        )

    settings = get_settings()
    msg = _client().messages.create(
        model=model or settings.report_model,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in msg.content if block.type == "text")


def _fake_stream(is_crisis: bool) -> Iterator[str]:
    if is_crisis:
        text = (
            "I'm really glad you told me, and I want you to know you're not alone. "
            "What you're feeling sounds incredibly heavy. Please reach out right "
            "now to the 988 Suicide & Crisis Lifeline — you can call or text 988 "
            "in the US — or contact local emergency services if you're in "
            "immediate danger. They're there for exactly this. I'm here with you."
        )
    else:
        text = (
            "Thank you for sharing that with me. It makes sense that you'd feel "
            "this way. Would it help to talk a little more about what's been on "
            "your mind today?"
        )
    for word in text.split(" "):
        yield word + " "
