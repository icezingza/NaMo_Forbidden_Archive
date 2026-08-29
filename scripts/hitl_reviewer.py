#!/usr/bin/env python3
"""
HITL Reviewer Interface สำหรับตรวจสอบ candidate chunks จาก narrative_data_pipeline
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path


class HITLReviewer:
    def __init__(self, candidate_file: str, output_file: str):
        self.candidate_file = Path(candidate_file)
        self.output_file = Path(output_file)
        self.reviewed_records = []

        # โหลดไฟล์ที่ review แล้ว (ถ้ามี) เพื่อ resume
        if self.output_file.exists():
            with open(self.output_file, encoding="utf-8") as f:
                self.reviewed_records = [json.loads(line) for line in f if line.strip()]

    def display_chunk(self, chunk: dict, index: int, total: int):
        """แสดง chunk พร้อม metadata"""
        print(f"\n{'='*80}")
        print(f"CHUNK {index+1}/{total}")
        print(f"{'='*80}")
        print(f"Source: {chunk.get('source_file', 'N/A')}")
        print(f"Provenance: {chunk.get('provenance', 'N/A')}")
        print("\n--- CONTENT ---")
        print(chunk.get("content", ""))
        print(f"{'='*80}\n")

    def get_review_input(self) -> dict:
        """รับ input จาก reviewer"""
        review = {}

        # Safety classification
        print("1. SAFETY CLASSIFICATION:")
        print("   [a] approved - ปลอดภัย")
        print("   [r] rejected_unsafe - ไม่ปลอดภัย")
        print("   [m] ambiguous - ต้องตรวจสอบเพิ่ม")
        safety = input("   Choice: ").strip().lower()
        review["safety_classification"] = {
            "a": "approved",
            "r": "rejected_unsafe",
            "m": "ambiguous",
        }.get(safety, "ambiguous")

        # Quality classification
        print("\n2. QUALITY CLASSIFICATION:")
        print("   [h] high_quality - วรรณศิลป์ดี")
        print("   [m] medium_quality - พอใช้")
        print("   [l] low_quality - เขียนหยาบ")
        quality = input("   Choice: ").strip().lower()
        review["quality_classification"] = {
            "h": "high_quality",
            "m": "medium_quality",
            "l": "low_quality",
        }.get(quality, "medium_quality")

        # Beat classification
        print("\n3. BEAT CLASSIFICATION:")
        print("   [t] tease - ยั่วยุ ชะลอ")
        print("   [r] resistance - เล่นตัว ต่อรอง")
        print("   [e] escalation - ยกระดับ")
        print("   [s] resolution - คลี่คลาย")
        print("   [c] recovery - aftercare")
        beat = input("   Choice: ").strip().lower()
        review["beat_classification"] = {
            "t": "tease",
            "r": "resistance",
            "e": "escalation",
            "s": "resolution",
            "c": "recovery",
        }.get(beat, "escalation")

        # DPO preference
        print("\n4. DPO PREFERENCE:")
        print("   [c] chosen - ตัวอย่างที่ดี")
        print("   [r] rejected - ตัวอย่างที่ไม่ดี")
        print("   [n] neutral - ใช้สำหรับ RAG เท่านั้น")
        dpo = input("   Choice: ").strip().lower()
        review["dpo_preference"] = {
            "c": "chosen",
            "r": "rejected",
            "n": "neutral",
        }.get(dpo, "neutral")

        # Confidence score
        print("\n5. CONFIDENCE SCORE (0.0-1.0):")
        try:
            confidence = float(input("   Score: ").strip())
        except ValueError:
            confidence = 0.5
        review["confidence_score"] = max(0.0, min(1.0, confidence))

        # Notes
        print("\n6. NOTES (optional, press Enter to skip):")
        notes = input("   Notes: ").strip()
        if notes:
            review["notes"] = notes

        # Metadata
        reviewer_id = input("\n7. REVIEWER ID: ").strip()
        review["reviewer_id"] = reviewer_id if reviewer_id else "reviewer_1"
        review["review_timestamp"] = datetime.utcnow().isoformat() + "Z"
        review["requires_second_review"] = review["confidence_score"] < 0.7

        return review

    def run(self):
        """รัน workflow"""
        with open(self.candidate_file, encoding="utf-8") as f:
            candidates = [json.loads(line) for line in f if line.strip()]

        total = len(candidates)
        print(f"📋 Starting HITL Review: {total} chunks to review")
        print(f"💾 Output will be saved to: {self.output_file}")
        print(f"🔄 Already reviewed: {len(self.reviewed_records)} chunks")

        for i, chunk in enumerate(candidates[len(self.reviewed_records) :]):
            self.display_chunk(chunk, len(self.reviewed_records) + i, total)

            review = self.get_review_input()
            record = {**chunk, **review}
            self.reviewed_records.append(record)

            # บันทึกทันทีหลังแต่ละ review
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

            print(f"\n✅ Saved review {len(self.reviewed_records)}/{total}")

            if input("\nContinue? [y/n]: ").strip().lower() != "y":
                break

        print(f"\n🎉 Review complete! {len(self.reviewed_records)} records reviewed.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python hitl_reviewer.py <candidate_file.jsonl> <output_file.jsonl>")
        sys.exit(1)

    reviewer = HITLReviewer(sys.argv[1], sys.argv[2])
    reviewer.run()
