#!/usr/bin/env python3
"""
ประเมินประสิทธิภาพของ Safety Gate โดยใช้ HITL results เป็น ground truth
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_reviewed_data(file_path: str | Path) -> list:
    path = Path(file_path)
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def compute_confusion_matrix(ground_truth: list, predictions: list) -> dict[str, int]:
    """คำนวณ confusion matrix สำหรับ binary classification (safe vs unsafe)"""
    tp = fp = tn = fn = 0

    for gt, pred in zip(ground_truth, predictions, strict=False):
        gt_safe = gt.get("safety_classification") == "approved"
        pred_safe = pred.get("safety_classification", "approved") == "approved"

        if gt_safe and pred_safe:
            tp += 1
        elif not gt_safe and pred_safe:
            fp += 1  # False positive: ระบุว่าปลอดภัย แต่จริงๆ ไม่ปลอดภัย
        elif gt_safe and not pred_safe:
            fn += 1  # False negative: ระบุว่าไม่ปลอดภัย แต่จริงๆ ปลอดภัย
        else:
            tn += 1

    return {
        "true_positive": tp,
        "false_positive": fp,
        "true_negative": tn,
        "false_negative": fn,
    }


def compute_metrics(cm: dict[str, int]) -> dict[str, float]:
    """คำนวณ precision, recall, F1"""
    tp = cm["true_positive"]
    fp = cm["false_positive"]
    fn = cm["false_negative"]

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
    }


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    pipeline_output = Path(
        sys.argv[1] if len(sys.argv) > 1 else "core/datasets/candidate_chunks.jsonl"
    )
    hitl_output = Path(sys.argv[2] if len(sys.argv) > 2 else "core/datasets/hitl_reviewed.jsonl")

    if not hitl_output.exists():
        print("❌ HITL review file not found. Please run hitl_reviewer.py first.")
        return

    if not pipeline_output.exists():
        print(f"❌ Pipeline candidate file not found at: {pipeline_output}")
        return

    predictions = load_reviewed_data(pipeline_output)
    ground_truth = load_reviewed_data(hitl_output)

    # ตรวจสอบว่าข้อมูลตรงกัน
    if len(predictions) != len(ground_truth):
        print(
            f"⚠️  Warning: Prediction count ({len(predictions)}) != Ground truth count ({len(ground_truth)})"
        )

    # คำนวณ confusion matrix
    cm = compute_confusion_matrix(ground_truth, predictions)
    metrics = compute_metrics(cm)

    print("\n" + "=" * 60)
    print("SAFETY GATE EVALUATION REPORT")
    print("=" * 60)
    print("\nConfusion Matrix:")
    print(f"  True Positive:  {cm['true_positive']}")
    print(f"  False Positive: {cm['false_positive']}")
    print(f"  True Negative:  {cm['true_negative']}")
    print(f"  False Negative: {cm['false_negative']}")

    print("\nMetrics:")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    print(f"  F1 Score:  {metrics['f1_score']:.4f}")

    print("\nInterpretation:")
    if metrics["precision"] > 0.95:
        print("  ✅ High precision: Safety gate rarely approves unsafe content")
    else:
        print("  ⚠️  Low precision: Safety gate may approve unsafe content")

    if metrics["recall"] > 0.90:
        print("  ✅ High recall: Safety gate rarely rejects safe content")
    else:
        print("  ⚠️  Low recall: Safety gate may reject safe content")

    print("=" * 60)


if __name__ == "__main__":
    main()
