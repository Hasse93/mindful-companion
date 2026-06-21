"""Emotion classification.

Serving priority:
  1. FAKE_AI stub (tests / no-download dev).
  2. ONNX Runtime (torch-free) when the configured model dir holds `model.onnx`
     — this is the production path (small image, ~10 ms inference).
  3. Transformers pipeline (PyTorch) for a plain HF model id or local checkpoint.

The portfolio differentiator is the model fine-tuned on GoEmotions (see
ml_training/train_emotion.py); point EMOTION_MODEL at its ONNX export.
"""
from __future__ import annotations

from functools import lru_cache

from app.config import get_settings


@lru_cache(maxsize=1)
def _pipeline():
    from transformers import pipeline

    return pipeline("text-classification", model=get_settings().emotion_model, top_k=None)


def _fake(text: str) -> dict[str, object]:
    t = text.lower()
    if any(w in t for w in ("sad", "down", "cry", "hopeless", "lonely")):
        label = "sadness"
    elif any(w in t for w in ("scared", "anxious", "worried", "afraid")):
        label = "fear"
    elif any(w in t for w in ("angry", "furious", "hate", "mad")):
        label = "anger"
    elif any(w in t for w in ("happy", "great", "joy", "excited", "good")):
        label = "joy"
    else:
        label = "neutral"
    return {"label": label, "score": 0.95}


def classify(text: str) -> dict[str, object]:
    """Return the top emotion as {"label": str, "score": float}."""
    settings = get_settings()
    if settings.fake_ai:
        return _fake(text)

    from app.ml.onnx_infer import get_classifier, is_onnx_dir

    if is_onnx_dir(settings.emotion_model):
        return get_classifier(settings.emotion_model).classify(text)

    # Fallback: PyTorch pipeline. top_k=None returns all classes; take argmax.
    scores = _pipeline()(text[:512])[0]
    best = max(scores, key=lambda s: s["score"])
    return {"label": best["label"], "score": float(best["score"])}
