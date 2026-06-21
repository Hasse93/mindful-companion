"""Emotion classification.

Default model is a public DistilRoBERTa fine-tuned for 7 Ekman emotions, so the
project runs end-to-end out of the box. The portfolio differentiator is to swap
this for YOUR model fine-tuned on GoEmotions (see ml_training/train_emotion.py)
by setting EMOTION_MODEL to the local path or HF repo id — no code change here.
"""
from __future__ import annotations

import os
from functools import lru_cache

from app.config import get_settings


@lru_cache(maxsize=1)
def _pipeline():
    from transformers import pipeline

    model_path = get_settings().emotion_model

    # If the model dir holds an exported ONNX graph, serve it via ONNX Runtime
    # (faster + lighter than PyTorch). Otherwise load the regular Transformers
    # model — works for both a local fine-tune and an HF hub id.
    onnx_file = os.path.join(model_path, "model.onnx")
    if os.path.isdir(model_path) and os.path.exists(onnx_file):
        from optimum.onnxruntime import ORTModelForSequenceClassification
        from transformers import AutoTokenizer

        model = ORTModelForSequenceClassification.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        return pipeline(
            "text-classification", model=model, tokenizer=tokenizer, top_k=None
        )

    return pipeline("text-classification", model=model_path, top_k=None)


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
    if get_settings().fake_ai:
        return _fake(text)

    # top_k=None returns all classes; take the argmax.
    scores = _pipeline()(text[:512])[0]
    best = max(scores, key=lambda s: s["score"])
    return {"label": best["label"], "score": float(best["score"])}
