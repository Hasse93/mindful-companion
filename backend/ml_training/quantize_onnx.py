"""INT8 dynamic quantization of an exported ONNX model.

Shrinks a DistilBERT ONNX model ~4x (≈255 MB → ≈65 MB) with minimal accuracy
loss, so it fits under GitHub's 100 MB file limit and a free-tier's RAM budget.
Replaces `model.onnx` in place (re-export with export_onnx.py to restore FP32).

Usage:
    python ml_training/quantize_onnx.py --dir ./models/emotion-onnx
"""
from __future__ import annotations

import argparse
import os


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="Model dir containing model.onnx")
    args = ap.parse_args()

    from onnxruntime.quantization import QuantType, quantize_dynamic

    src = os.path.join(args.dir, "model.onnx")
    tmp = os.path.join(args.dir, "model.quant.onnx")
    before = os.path.getsize(src) / 1e6

    quantize_dynamic(src, tmp, weight_type=QuantType.QInt8)

    after = os.path.getsize(tmp) / 1e6
    os.replace(tmp, src)  # overwrite model.onnx with the quantized version
    print(f"{args.dir}: {before:.0f} MB -> {after:.0f} MB")


if __name__ == "__main__":
    main()
