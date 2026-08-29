from dataclasses import asdict

from core.narrative_data_pipeline import (
    NarrativeDataSanitizer,
    build_dpo_pairs,
    write_jsonl_atomic,
)

SAFE_TEXT = " ".join(
    [
        "ตัวละครผู้ใหญ่สองคนค่อยๆ สนทนาและรับฟังขอบเขตของกันและกัน",
        "บรรยากาศดำเนินอย่างช้าๆ ผ่านสายตาและความไว้วางใจ",
        "ทั้งคู่หยุดทบทวนความรู้สึกก่อนตัดสินใจดำเนินเรื่องต่อ",
    ]
    * 3
)


def test_pipeline_rejects_toxic_filename_without_logging_text(tmp_path) -> None:
    source_dir = tmp_path / "raw"
    source_dir.mkdir()
    source = source_dir / "ฉากข่มขืน.htm"
    source.write_text(f"<html><body><p>{SAFE_TEXT}</p></body></html>", encoding="utf-8")

    records, provenance = NarrativeDataSanitizer().process_directory(source_dir)

    assert records == []
    assert provenance[0].decision == "REJECT"
    assert "NON_CONSENSUAL_OR_COERCION" in provenance[0].reason_codes
    assert "text" not in asdict(provenance[0])


def test_pipeline_cleans_html_and_deduplicates_chunks(tmp_path) -> None:
    source_dir = tmp_path / "raw"
    source_dir.mkdir()
    html = f"<html><script>secret ad</script><body><p>{SAFE_TEXT}</p></body></html>"
    (source_dir / "safe-a.htm").write_text(html, encoding="utf-8")
    (source_dir / "safe-b.htm").write_text(html, encoding="utf-8")

    records, provenance = NarrativeDataSanitizer().process_directory(source_dir)

    assert records
    assert all("secret ad" not in record["text"] for record in records)
    assert len({record["content_hash"] for record in records}) == len(records)
    assert any("DUPLICATE_CHUNK_REMOVED" in item.reason_codes for item in provenance)
    assert all(record["review_status"] == "PENDING_HITL" for record in records)


def test_dpo_requires_human_approval() -> None:
    pending = {"text": SAFE_TEXT, "beat": "resistance", "review_status": "PENDING_HITL"}
    approved = {**pending, "review_status": "APPROVED"}

    assert build_dpo_pairs([pending]) == []
    assert build_dpo_pairs([approved])[0]["chosen"] == SAFE_TEXT


def test_atomic_jsonl_writer(tmp_path) -> None:
    output = tmp_path / "nested" / "records.jsonl"
    write_jsonl_atomic(output, [{"ภาษา": "ไทย"}])

    assert output.read_text(encoding="utf-8") == '{"ภาษา": "ไทย"}\n'
