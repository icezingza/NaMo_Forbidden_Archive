"""Offline sanitizer for promoting web narrative HTML into reviewable JSONL."""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import tempfile
import unicodedata
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path

from core.narrative_safety import NarrativeBeat, NarrativeSafetyGate
from core.rag_chunker import MicroChunker

SANITIZER_VERSION = "1.0.0"


class _VisibleTextParser(HTMLParser):
    _IGNORED = {"script", "style", "noscript", "svg", "nav", "footer", "header", "aside"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() in self._IGNORED:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() in self._IGNORED and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth and data.strip():
            self.parts.append(data)


@dataclass(frozen=True, slots=True)
class ProvenanceRecord:
    source_path: str
    source_hash: str
    decision: str
    reason_codes: list[str]
    sanitizer_version: str
    chunk_count: int
    processed_at: str


class NarrativeDataSanitizer:
    _BOILERPLATE = re.compile(
        r"(สมัครสมาชิก|เข้าสู่ระบบ|privacy policy|cookie policy|advertisement|โฆษณา)", re.I
    )

    def __init__(self, *, min_chars: int = 120) -> None:
        self.min_chars = min_chars
        self.safety_gate = NarrativeSafetyGate()
        self.chunker = MicroChunker(max_tokens=150, overlap_tokens=20)

    @staticmethod
    def clean_html(raw: bytes) -> str:
        decoded = raw.decode("utf-8", errors="replace")
        parser = _VisibleTextParser()
        parser.feed(decoded)
        text = html.unescape("\n".join(parser.parts))
        text = unicodedata.normalize("NFC", text)
        lines = [" ".join(line.split()) for line in text.splitlines()]
        return "\n".join(line for line in lines if line)

    @staticmethod
    def _beat_for_chunk(text: str) -> str:
        lowered = text.casefold()
        if any(term in lowered for term in ("ปลอบ", "พัก", "ดูแล", "สงบ")):
            return NarrativeBeat.RECOVERY.value
        if any(term in lowered for term in ("จบ", "คลี่คลาย", "ผ่อนลง")):
            return NarrativeBeat.RESOLUTION.value
        if any(term in lowered for term in ("ลังเล", "ช้าก่อน", "ต่อรอง", "รอ")):
            return NarrativeBeat.RESISTANCE.value
        if any(term in lowered for term in ("ใกล้ขึ้น", "เข้มขึ้น", "เร่ง")):
            return NarrativeBeat.ESCALATION.value
        return NarrativeBeat.TEASE.value

    def process_file(self, source: Path, *, root: Path) -> tuple[list[dict], ProvenanceRecord]:
        raw = source.read_bytes()
        source_hash = hashlib.sha256(raw).hexdigest()
        relative_path = source.relative_to(root).as_posix()
        clean_text = self.clean_html(raw)
        classification_text = f"{source.name}\n{clean_text}"
        blocked_reason = self.safety_gate.classify_corpus(classification_text)
        reason_codes: list[str] = []

        if self._BOILERPLATE.search(clean_text):
            clean_text = "\n".join(
                line for line in clean_text.splitlines() if not self._BOILERPLATE.search(line)
            )
        if len(clean_text) < self.min_chars:
            reason_codes.append("EMPTY_OR_TOO_SHORT")
        if blocked_reason:
            reason_codes.append(blocked_reason)

        records: list[dict] = []
        if not reason_codes:
            document_id = f"sha256:{source_hash}"
            for index, chunk in enumerate(self.chunker.chunk_text(clean_text)):
                chunk_hash = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
                records.append(
                    {
                        "chunk_id": f"{source_hash[:16]}-{index:05d}",
                        "document_id": document_id,
                        "text": chunk,
                        "beat": self._beat_for_chunk(chunk),
                        "safety_labels": [],
                        "source_hash": source_hash,
                        "content_hash": chunk_hash,
                        "sanitizer_version": SANITIZER_VERSION,
                        "review_status": "PENDING_HITL",
                    }
                )

        provenance = ProvenanceRecord(
            source_path=relative_path,
            source_hash=source_hash,
            decision="REVIEW" if records else "REJECT",
            reason_codes=reason_codes,
            sanitizer_version=SANITIZER_VERSION,
            chunk_count=len(records),
            processed_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        )
        return records, provenance

    def process_directory(self, source_dir: Path) -> tuple[list[dict], list[ProvenanceRecord]]:
        records: list[dict] = []
        provenance: list[ProvenanceRecord] = []
        seen_content: set[str] = set()
        for source in sorted((*source_dir.rglob("*.htm"), *source_dir.rglob("*.html"))):
            file_records, audit = self.process_file(source, root=source_dir)
            unique_records = []
            for record in file_records:
                if record["content_hash"] not in seen_content:
                    seen_content.add(record["content_hash"])
                    unique_records.append(record)
            if len(unique_records) != len(file_records):
                audit = ProvenanceRecord(
                    **{
                        **asdict(audit),
                        "reason_codes": [*audit.reason_codes, "DUPLICATE_CHUNK_REMOVED"],
                        "chunk_count": len(unique_records),
                    }
                )
            records.extend(unique_records)
            provenance.append(audit)
        return records, provenance


def write_jsonl_atomic(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            for row in rows:
                output.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary_name, path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def build_dpo_pairs(records: Iterable[dict]) -> list[dict]:
    """Emit only reviewed pairs; rejected text is a safe pacing anti-pattern, never toxic source."""
    pairs = []
    for record in records:
        if record.get("review_status") != "APPROVED":
            continue
        beat = record["beat"]
        pairs.append(
            {
                "prompt": f"เขียนฉากตาม narrative beat={beat} โดยเคารพขอบเขตที่ระบุ",
                "chosen": record["text"],
                "rejected": "ข้ามจังหวะอารมณ์และดำเนินฉากต่อทันทีโดยไม่ตรวจสอบขอบเขต",
                "policy_labels": ["BOUNDARY_RESPECT", "CONTROLLED_PACING"],
                "beat": beat,
                "review_status": "APPROVED",
            }
        )
    return pairs
