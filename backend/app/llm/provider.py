"""LLM provider dispatch.

Owns the fake/no-key decision centrally, then routes to the configured backend
(Gemini or Claude). Routers call `provider.stream_reply` / `provider.complete`
and never touch a specific vendor SDK.
"""
from __future__ import annotations

from collections.abc import Iterator

from app.config import get_settings


def _provider() -> str:
    return get_settings().llm_provider.lower()


def _use_fake() -> bool:
    s = get_settings()
    if s.fake_ai:
        return True
    return not (s.gemini_api_key if _provider() == "gemini" else s.anthropic_api_key)


def stream_reply(history: list[dict[str, str]], *, is_crisis: bool = False) -> Iterator[str]:
    if _use_fake():
        yield from _fake_stream(is_crisis)
        return
    if _provider() == "gemini":
        from app.llm import gemini_client

        yield from gemini_client.stream_reply(history, is_crisis=is_crisis)
    else:
        from app.llm import claude_client

        yield from claude_client.stream_reply(history, is_crisis=is_crisis)


def complete(prompt: str) -> str:
    if _use_fake():
        return _fake_complete()
    if _provider() == "gemini":
        from app.llm import gemini_client

        return gemini_client.complete(prompt)
    from app.llm import claude_client

    return claude_client.complete(prompt)


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


def _fake_complete() -> str:
    return (
        "This week shows a mix of ups and downs, which is completely human. "
        "Your check-ins suggest some heavier moments alongside lighter ones. "
        "A gentle invitation for the week ahead: try a few minutes of grounding "
        "when things feel heavy, and reach out to someone you trust. This "
        "reflection is a supportive note, not professional care."
    )
