#!/usr/bin/env python3
"""
Promote reviewed records เป็น Golden Dataset สำหรับ Fine-tuning/DPO
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def promote_to_golden(hitl_file: str, golden_file: str, min_confidence: float = 0.8):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    """กรองและ promote records ที่ผ่านเกณฑ์"""
    hitl_path = Path(hitl_file)
    if not hitl_path.exists():
        print(f"❌ HITL reviewed file not found: {hitl_file}")
        return

    with open(hitl_path, encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]

    golden_records = []

    for record in records:
        # เกณฑ์การ promote
        if (
            record.get("safety_classification") == "approved"
            and record.get("quality_classification") in ["high_quality", "medium_quality"]
            and float(record.get("confidence_score", 0.0)) >= min_confidence
            and not record.get("requires_second_review", False)
        ):
            golden_records.append(record)

    # บันทึก Golden Dataset
    golden_path = Path(golden_file)
    golden_path.parent.mkdir(parents=True, exist_ok=True)
    with open(golden_path, "w", encoding="utf-8") as f:
        for record in golden_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"✅ Promoted {len(golden_records)}/{len(records)} records to Golden Dataset")
    print(f"💾 Saved to: {golden_file}")

    # แยกเป็น ChatML format สำหรับ Fine-tuning
    chatml_file = golden_file.replace(".jsonl", "_chatml.jsonl")
    with open(chatml_file, "w", encoding="utf-8") as f:
        for record in golden_records:
            chatml_entry = {
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "คุณคือผู้เชี่ยวชาญด้านการเขียน Erotic Literary Realism "
                            "เน้น 90% Tension / 10% Action"
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"จงเขียนฉากในจังหวะ '{record.get('beat_classification', 'escalation')}' "
                            "โดยเน้นประสาทสัมผัสและอารมณ์:"
                        ),
                    },
                    {"role": "assistant", "content": record.get("content", "")},
                ],
                "metadata": {
                    "beat": record.get("beat_classification", "escalation"),
                    "quality": record.get("quality_classification", "medium_quality"),
                    "source": record.get("source_file", "unknown"),
                },
            }
            f.write(json.dumps(chatml_entry, ensure_ascii=False) + "\n")

    print(f"✅ Generated ChatML format: {chatml_file}")

    # Build DPO pairs
    dpo_file = golden_file.replace(".jsonl", "_dpo.jsonl")
    chosen_records = [
        r
        for r in golden_records
        if r.get("dpo_preference") == "chosen" or r.get("safety_classification") == "approved"
    ]
    rejected_records = [r for r in golden_records if r.get("dpo_preference") == "rejected"]

    REJECTED_TEMPLATES = {
        "tease": "เอาเลย เร็วๆ ยัดเข้าไปเลย ไม่ต้องพูดมาก",
        "resistance": "ไม่ต้องมาเล่นตัว ยอมๆ ไปเถอะ รีบๆ ทำ",
        "escalation": "กระแทกเข้าไปแรงๆ เร็วๆ ให้เสร็จๆ ไปเลย",
        "resolution": "เสร็จแล้ว ปล่อยออกมาเลย สั้นๆ จบๆ",
        "recovery": "เสร็จแล้วก็ลุกไป ไม่ต้องมากอด ลุกขึ้นเดี๋ยวนี้",
    }

    dpo_pairs = []
    with open(dpo_file, "w", encoding="utf-8") as f:
        for chosen in chosen_records:
            beat = chosen.get("beat_classification", "escalation")
            # If explicit rejected record exists with same beat
            matching_rejected = [
                r for r in rejected_records if r.get("beat_classification") == beat
            ]
            rejected_text = (
                matching_rejected[0].get("content")
                if matching_rejected
                else REJECTED_TEMPLATES.get(beat, "เอาเลย เร็วๆ ทำๆ ไป")
            )

            pair = {
                "prompt": f"จงเขียนฉากในจังหวะ '{beat}' โดยเน้นอารมณ์และวรรณศิลป์:",
                "chosen": chosen.get("content", ""),
                "rejected": rejected_text,
                "metadata": {"beat": beat},
            }
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
            dpo_pairs.append(pair)

    print(f"✅ Generated DPO pairs ({len(dpo_pairs)} pairs): {dpo_file}")


if __name__ == "__main__":
    hitl_input = sys.argv[1] if len(sys.argv) > 1 else "core/datasets/hitl_reviewed.jsonl"
    golden_output = sys.argv[2] if len(sys.argv) > 2 else "core/datasets/namo_golden_dataset.jsonl"

    promote_to_golden(hitl_input, golden_output, min_confidence=0.8)
