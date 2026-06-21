"""Google Gemini backend for the companion (streaming chat + report).

Uses the current `google-genai` SDK. Safety thresholds are set to BLOCK_NONE on
purpose: this is a wellness companion, so the model must be able to respond with
care when someone expresses distress or self-harm thoughts rather than refusing.
Compassionate, non-clinical behaviour is steered by the system prompt, and the
separate crisis-triage layer independently surfaces professional resources.
"""
from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache

from app.config import get_settings
from app.llm.prompts import COMPANION_SYSTEM_PROMPT, CRISIS_STEER


@lru_cache(maxsize=1)
def _client():
    from google import genai

    return genai.Client(api_key=get_settings().gemini_api_key)


def _config(system: str):
    from google.genai import types

    none = types.HarmBlockThreshold.BLOCK_NONE
    return types.GenerateContentConfig(
        system_instruction=system,
        max_output_tokens=600,
        safety_settings=[
            types.SafetySetting(category=c, threshold=none)
            for c in (
                types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            )
        ],
    )


def _contents(history: list[dict[str, str]]):
    # Gemini uses roles "user" / "model".
    return [
        {"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
        for m in history
    ]


def stream_reply(history: list[dict[str, str]], *, is_crisis: bool = False) -> Iterator[str]:
    system = COMPANION_SYSTEM_PROMPT + (("\n\n" + CRISIS_STEER) if is_crisis else "")
    settings = get_settings()
    stream = _client().models.generate_content_stream(
        model=settings.gemini_model,
        contents=_contents(history),
        config=_config(system),
    )
    for chunk in stream:
        if chunk.text:
            yield chunk.text


def complete(prompt: str) -> str:
    settings = get_settings()
    resp = _client().models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=_config(COMPANION_SYSTEM_PROMPT),
    )
    return resp.text or ""
