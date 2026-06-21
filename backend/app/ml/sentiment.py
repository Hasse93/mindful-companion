"""Sentiment analysis (DistilBERT SST-2).

Serving priority mirrors emotion.py: FAKE_AI stub → ONNX Runtime (torch-free,
production) → Transformers pipeline (PyTorch) fallback. Models load lazily on
first use so the API boots instantly.
"""
from __future__ import annotations

from functools import lru_cache

from app.config import get_settings

_LABEL_MAP = {"POSITIVE": "POSITIVE", "NEGATIVE": "NEGATIVE"}


@lru_cache(maxsize=1)
def _pipeline():
    from transformers import pipeline

    return pipeline("sentiment-analysis", model=get_settings().sentiment_model)


def _fake(text: str) -> dict[str, object]:
    neg_words = ("sad", "bad", "hate", "awful", "terrible", "anxious", "hopeless")
    is_neg = any(w in text.lower() for w in neg_words)
    return {"label": "NEGATIVE" if is_neg else "POSITIVE", "score": 0.99}


def analyze(text: str) -> dict[str, object]:
    """Return {"label": str, "score": float} for the given text."""
    settings = get_settings()
    if settings.fake_ai:
        return _fake(text)

    from app.ml.onnx_infer import get_classifier, is_onnx_dir

    if is_onnx_dir(settings.sentiment_model):
        result = get_classifier(settings.sentiment_model).classify(text)
        return {"label": _LABEL_MAP.get(str(result["label"]), result["label"]), "score": result["score"]}

    result = _pipeline()(text[:512])[0]
    return {
        "label": _LABEL_MAP.get(result["label"], result["label"]),
        "score": float(result["score"]),
    }
