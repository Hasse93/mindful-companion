"""Fine-tune DistilBERT on GoEmotions and (optionally) export to ONNX.

This script is the ML/NLP centrepiece of the project. It:
  1. Loads the GoEmotions dataset from the Hugging Face hub.
  2. Maps the 27 fine-grained labels to 7 Ekman emotions (simpler, more useful
     for mood insights, and better balanced).
  3. Fine-tunes `distilbert-base-uncased` as a single-label classifier.
  4. Logs metrics (macro-F1, accuracy) to MLflow when available.
  5. Saves the model and optionally exports an optimised ONNX version.

Quick smoke run (a real but small model in minutes, good on CPU):
    python ml_training/train_emotion.py --max-train-samples 4000 \
        --max-eval-samples 1000 --epochs 1 --no-onnx --output ./models/emotion

Full run (better macro-F1, slower on CPU):
    python ml_training/train_emotion.py --epochs 3 --output ./models/emotion

Then point the API at it:
    EMOTION_MODEL=./models/emotion        (or ./models/emotion-onnx)

This is a reference scaffold — tune hyper-parameters and the label map for your
own evaluation. It is intentionally not imported by the running API.
"""
from __future__ import annotations

import argparse

# GoEmotions (27) -> Ekman (7). "neutral" kept; everything else grouped.
EKMAN_MAP = {
    "anger": ["anger", "annoyance", "disapproval"],
    "disgust": ["disgust"],
    "fear": ["fear", "nervousness"],
    "joy": [
        "joy", "amusement", "approval", "excitement", "gratitude", "love",
        "optimism", "relief", "pride", "admiration", "desire", "caring",
    ],
    "sadness": ["sadness", "disappointment", "embarrassment", "grief", "remorse"],
    "surprise": ["surprise", "realization", "confusion", "curiosity"],
    "neutral": ["neutral"],
}
EKMAN_LABELS = list(EKMAN_MAP.keys())
_FINE_TO_EKMAN = {fine: ek for ek, fines in EKMAN_MAP.items() for fine in fines}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=float, default=3)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--base-model", default="distilbert-base-uncased")
    parser.add_argument("--output", default="./models/emotion")
    parser.add_argument("--max-train-samples", type=int, default=None,
                        help="Cap training rows for a fast smoke run.")
    parser.add_argument("--max-eval-samples", type=int, default=None)
    parser.add_argument("--no-onnx", action="store_true")
    args = parser.parse_args()

    import numpy as np
    from datasets import ClassLabel, load_dataset
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        DataCollatorWithPadding,
        Trainer,
        TrainingArguments,
    )

    try:
        import mlflow
    except ImportError:
        mlflow = None

    # 1. Load GoEmotions (simplified config = list of label ids per example).
    ds = load_dataset("go_emotions", "simplified")
    fine_names = ds["train"].features["labels"].feature.names

    # 2. Map to a single Ekman label, dropping multi-label rows for a clean
    #    single-label classification task. -1 marks rows to drop.
    def to_ekman(example):
        if len(example["labels"]) != 1:
            return {"ekman": -1}
        fine = fine_names[example["labels"][0]]
        return {"ekman": EKMAN_LABELS.index(_FINE_TO_EKMAN[fine])}

    ds = ds.map(to_ekman)
    ds = ds.filter(lambda e: e["ekman"] != -1)

    tokenizer = AutoTokenizer.from_pretrained(args.base_model)

    def tok(batch):
        return tokenizer(batch["text"], truncation=True, max_length=128)

    ds = ds.map(tok, batched=True)

    # 3. Keep only the columns the Trainer needs, then promote `ekman` to the
    #    `labels` column the model expects. (Dropping the original list-valued
    #    `labels` column first avoids a rename collision.)
    keep = {"input_ids", "attention_mask", "ekman"}
    ds = ds.remove_columns([c for c in ds["train"].column_names if c not in keep])
    ds = ds.cast_column("ekman", ClassLabel(names=EKMAN_LABELS))
    ds = ds.rename_column("ekman", "labels")

    train_ds = ds["train"].shuffle(seed=42)
    eval_ds = ds["validation"]
    test_ds = ds["test"]
    if args.max_train_samples:
        train_ds = train_ds.select(range(min(args.max_train_samples, len(train_ds))))
    if args.max_eval_samples:
        eval_ds = eval_ds.select(range(min(args.max_eval_samples, len(eval_ds))))
        test_ds = test_ds.select(range(min(args.max_eval_samples, len(test_ds))))

    model = AutoModelForSequenceClassification.from_pretrained(
        args.base_model,
        num_labels=len(EKMAN_LABELS),
        id2label=dict(enumerate(EKMAN_LABELS)),
        label2id={l: i for i, l in enumerate(EKMAN_LABELS)},
    )

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        if isinstance(logits, tuple):
            logits = logits[0]
        preds = np.argmax(logits, axis=-1)
        # macro-F1 weights every emotion equally (important on imbalanced data).
        macro_f1 = _macro_f1(preds, labels, num_labels=len(EKMAN_LABELS))
        accuracy = float((preds == labels).mean())
        return {"macro_f1": macro_f1, "accuracy": accuracy}

    training_args = TrainingArguments(
        output_dir=args.output,
        learning_rate=args.lr,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.epochs,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        save_total_limit=2,  # keep best + last, don't fill the disk
        logging_steps=50,
        report_to="none",  # we log to MLflow manually below
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        data_collator=DataCollatorWithPadding(tokenizer),
        compute_metrics=compute_metrics,
    )

    if mlflow:
        mlflow.set_experiment("mindful-emotion")
        mlflow.start_run()
        mlflow.log_params(vars(args))

    trainer.train()
    test_metrics = trainer.evaluate(test_ds)
    print("Test metrics:", test_metrics)

    trainer.save_model(args.output)
    tokenizer.save_pretrained(args.output)

    if mlflow:
        mlflow.log_metrics({k: float(v) for k, v in test_metrics.items()
                            if isinstance(v, (int, float))})
        mlflow.end_run()

    # 5. Export to ONNX for fast, lightweight serving.
    if not args.no_onnx:
        from optimum.onnxruntime import ORTModelForSequenceClassification

        onnx_dir = f"{args.output}-onnx"
        ort_model = ORTModelForSequenceClassification.from_pretrained(args.output, export=True)
        ort_model.save_pretrained(onnx_dir)
        tokenizer.save_pretrained(onnx_dir)
        print(f"ONNX model written to {onnx_dir}")


def _macro_f1(preds, labels, *, num_labels: int) -> float:
    """Unweighted mean per-class F1 — no sklearn dependency required."""
    import numpy as np

    f1s = []
    for c in range(num_labels):
        tp = int(np.sum((preds == c) & (labels == c)))
        fp = int(np.sum((preds == c) & (labels != c)))
        fn = int(np.sum((preds != c) & (labels == c)))
        if tp == 0:
            f1s.append(0.0)
            continue
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1s.append(2 * precision * recall / (precision + recall))
    return float(np.mean(f1s))


if __name__ == "__main__":
    main()
