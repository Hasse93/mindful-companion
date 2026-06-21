"""Torch-free text classification via ONNX Runtime.

Used for production serving: loads `model.onnx` + the tokenizer + the id->label
map from a model directory and classifies text using only `onnxruntime` and the
`transformers` tokenizer — no torch. This keeps the deployed image small.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache

import numpy as np


class OnnxClassifier:
    def __init__(self, model_dir: str) -> None:
        import onnxruntime as ort
        from transformers import AutoTokenizer

        self.session = ort.InferenceSession(
            os.path.join(model_dir, "model.onnx"),
            providers=["CPUExecutionProvider"],
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        with open(os.path.join(model_dir, "config.json"), encoding="utf-8") as f:
            cfg = json.load(f)
        self.id2label = {int(k): v for k, v in cfg["id2label"].items()}
        self.input_names = {i.name for i in self.session.get_inputs()}

    def classify(self, text: str) -> dict[str, object]:
        enc = self.tokenizer(
            text[:512], return_tensors="np", truncation=True, max_length=512
        )
        feeds = {
            k: v.astype(np.int64) for k, v in enc.items() if k in self.input_names
        }
        logits = self.session.run(None, feeds)[0][0]
        # numerically stable softmax
        exp = np.exp(logits - logits.max())
        probs = exp / exp.sum()
        idx = int(probs.argmax())
        return {"label": self.id2label[idx], "score": float(probs[idx])}


def is_onnx_dir(path: str) -> bool:
    return os.path.isdir(path) and os.path.exists(os.path.join(path, "model.onnx"))


@lru_cache(maxsize=4)
def get_classifier(model_dir: str) -> OnnxClassifier:
    return OnnxClassifier(model_dir)
