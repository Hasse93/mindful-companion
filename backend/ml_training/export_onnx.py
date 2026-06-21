"""Export a fine-tuned emotion model to ONNX for fast, lightweight serving.

Runs independently of training, so you can export an already-saved model without
re-fitting. The backend (`app/ml/emotion.py`) auto-detects `model.onnx` in the
model dir and serves it via ONNX Runtime.

Usage:
    python ml_training/export_onnx.py --model ./models/emotion --output ./models/emotion-onnx

Then point the API at it:
    EMOTION_MODEL=./models/emotion-onnx
"""
from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="./models/emotion", help="Saved model dir")
    parser.add_argument("--output", default="./models/emotion-onnx")
    args = parser.parse_args()

    from optimum.exporters.onnx import main_export

    # Exports model.onnx + copies config/tokenizer into the output dir.
    main_export(
        model_name_or_path=args.model,
        output=args.output,
        task="text-classification",
    )
    print(f"ONNX model written to {args.output}")


if __name__ == "__main__":
    main()
