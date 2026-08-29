#!/usr/bin/env python3
"""
Dry-Run Verification Script for Golden Dataset SFT & DPO Training Compliance.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def verify_dataset(filepath: Path, expected_keys: list[str]) -> tuple[bool, int, list[str]]:
    if not filepath.exists():
        return False, 0, [f"File not found: {filepath}"]

    errors = []
    record_count = 0

    with open(filepath, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            record_count += 1
            try:
                data = json.loads(line)
                for key in expected_keys:
                    if key not in data:
                        errors.append(f"Line {line_num}: Missing key '{key}'")
            except json.JSONDecodeError as exc:
                errors.append(f"Line {line_num}: Invalid JSON ({exc})")

    return len(errors) == 0, record_count, errors


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("\n" + "=" * 70)
    print("🧪 DRY-RUN VERIFICATION: FINE-TUNING DATASETS")
    print("=" * 70)

    datasets = [
        (Path("core/datasets/namo_golden_dataset.jsonl"), ["content", "safety_classification"]),
        (Path("core/datasets/namo_golden_dataset_chatml.jsonl"), ["messages"]),
        (Path("core/datasets/namo_golden_dataset_dpo.jsonl"), ["prompt", "chosen", "rejected"]),
    ]

    all_valid = True
    for path, keys in datasets:
        valid, count, errs = verify_dataset(path, keys)
        status = "✅ PASS" if valid else "❌ FAIL"
        print(f"\n📁 Dataset: {path}")
        print(f"   Status: {status} | Total Records: {count}")
        if not valid:
            all_valid = False
            for err in errs[:5]:
                print(f"   ⚠️ {err}")

    print("\n" + "=" * 70)
    if all_valid:
        print(
            "🎉 DRY-RUN PASSED: All training datasets are 100% compliant and ready for Unsloth/Axolotl Fine-Tuning!"
        )
    else:
        print("🚨 DRY-RUN FAILED: Fix dataset errors before initiating GPU fine-tuning.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
