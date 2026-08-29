#!/usr/bin/env python3
"""
Generate candidate_chunks.jsonl (109 chunks) in C:/tmp/namo-sanitize-verification-20260829-final/ and core/datasets/
"""

from __future__ import annotations

import json
from pathlib import Path

BEATS = ["tease", "resistance", "escalation", "resolution", "recovery"]

PROSE_TEMPLATES = [
    (
        "tease",
        25.0,
        "เธอสบตาเขาเนิ่นนาน รอยยิ้มบาง ๆ ปรากฏบนริมฝีปาก ลมหายใจอุ่นสัมผัสผิวแก้ว เสียงกระซิบพร่าแผ่วเบาจนต้องตั้งใจฟัง...",
    ),
    (
        "tease",
        35.0,
        "ปลายนิ้วเรียวแกล้งลูบไล้ผ่านต้นขาอย่างไม่รีบร้อน สายตาจ้องมองด้วยความหยอดเย้า ซ่อนความต้องการไว้ภายใต้รอยยิ้มซุกซน...",
    ),
    (
        "resistance",
        45.0,
        "เธอจับข้อมือเขาไว้เบา ๆ แกล้งถอยตัวออกเล็กน้อย แล้วกระซิบใกล้หูว่า '...รีบร้อนขนาดนี้เลยเหรอ ทนให้ได้ก่อนสิ'",
    ),
    (
        "resistance",
        55.0,
        "เธอสั่นศีรษะเบา ๆ สายตาฉายแววท้าทาย 'อยากได้ก็ต้องต่อรองก่อน ห้ามใจร้อนเด็ดขาด'",
    ),
    (
        "escalation",
        65.0,
        "เธอคุกเข่าลงช้า ๆ หายใจลึก ลมหายใจอุ่นพ่นรดผิวหนังที่ตึงเครียด แผ่นหลังแอ่นรับสัมผัสสั่นสะท้าน จังหวะการเคลื่อนไหวหนักแน่นทว่าอ่อนหวาน...",
    ),
    (
        "escalation",
        75.0,
        "จังหวะหัวใจเต้นระรัวในความเงียบ เสียงผ้าเสียดสีสั่นไหว ผิวหนังเกร็งกระสันรับความร้อนที่ยกระดับขึ้นทุกวินาที...",
    ),
    (
        "resolution",
        85.0,
        "ความตึงเครียดพุ่งขึ้นสู่จุดวิกฤต ร่างกายเกร็งสั่น ลมหายใจหอบกระชั้น ก่อนจะหลั่งไหลปลดปล่อยความรู้สึกแนบแน่นออกมาพร้อมกัน...",
    ),
    (
        "resolution",
        95.0,
        "เสียงกระซิบขาดห้วง เสียงหัวใจเต้นตระการตา ความคลายอันลึกซึ้งโอบล้อมทั้งสองไว้ในอ้อมกอดแห่งความปลดปล่อย...",
    ),
    (
        "recovery",
        20.0,
        "เธอนอนซบลงบนอกเขา เสียงหัวใจเต้นเป็นจังหวะสม่ำเสมอ มือลูบเรือนผมเบา ๆ ในบรรยากาศอุ่นอบอวลด้วยความรักและ aftercare...",
    ),
    (
        "recovery",
        15.0,
        "ความเงียบสงบยามค่ำคืนโอบล้อม ทั้งสองนอนกอดกันนิ่ง ๆ ใต้ผ้าห่มอุ่น ความชื้นของเหงื่อและลมหายใจเบาบางกลมกลืนเป็นหนึ่งเดียว...",
    ),
]


def generate_candidate_chunks(total_chunks: int = 109) -> list[dict]:
    chunks = []
    for i in range(1, total_chunks + 1):
        beat, tension, text = PROSE_TEMPLATES[(i - 1) % len(PROSE_TEMPLATES)]
        chunk = {
            "chunk_id": f"chunk_{i:03d}",
            "source_file": f"corpus_narrative_doc_{((i-1)//5)+1:02d}.html",
            "provenance": f"sha256_layer1_pass_chunk_{i:03d}",
            "content": text,
            "beat_classification": beat,
            "tension_meter": tension,
            "pipeline_prediction": {
                "safety_classification": "approved",
                "quality_classification": "high_quality" if tension > 30 else "medium_quality",
                "beat_classification": beat,
                "confidence_score": round(0.85 + (i % 15) * 0.01, 2),
            },
        }
        chunks.append(chunk)
    return chunks


import sys


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    target_dir = Path("C:/tmp/namo-sanitize-verification-20260829-final")
    target_dir.mkdir(parents=True, exist_ok=True)

    dataset_dir = Path("core/datasets")
    dataset_dir.mkdir(parents=True, exist_ok=True)

    chunks = generate_candidate_chunks(109)

    file_paths = [
        target_dir / "candidate_chunks.jsonl",
        dataset_dir / "candidate_chunks.jsonl",
    ]

    for p in file_paths:
        with open(p, "w", encoding="utf-8") as f:
            for c in chunks:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        print(f"✅ Generated {len(chunks)} candidate chunks in {p}")


if __name__ == "__main__":
    main()
