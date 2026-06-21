"""Sentiment analysis (pretrained DistilBERT SST-2).

The model is loaded lazily on first use so importing the module is cheap and the
API boots instantly. When `FAKE_AI=true` (tests / no-download dev) a
deterministic stub is returned instead of running a real model.
"""
from __future__ import annotations

from functools import lru_cache

from app.config import get_settings

# Map raw SST-2 labels to our domain vocabulary.
_LABEL_MAP = {"POSITIVE": "POSITIVE", "NEGATIVE": "NEGATIVE"}


@lru_cache(maxsize=1)
def _pipeline():
    # Imported here, not at module top, so transformers/torch are only required
    # when real inference actually runs.
    from transformers import pipeline

    settings = get_settings()
    return pipeline("sentiment-analysis", model=settings.sentiment_model)


def _fake(text: str) -> dict[str, object]:
    neg_words = ("sad", "bad", "hate", "awful", "terrible", "anxious", "hopeless")
    is_neg = any(w in text.lower() for w in neg_words)
    return {
        "label": "NEGATIVE" if is_neg else "POSITIVE",
        "score": 0.99,
    }


def analyze(text: str) -> dict[str, object]:
    """Return {"label": str, "score": float} for the given text."""
    if get_settings().fake_ai:
        return _fake(text)

    result = _pipeline()(text[:512])[0]  # truncate to model max length
    return {
        "label": _LABEL_MAP.get(result["label"], result["label"]),
        "score": float(result["score"]),
    }
