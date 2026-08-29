"""Slow-Burn Lorebook Injector for NRE Core Engine.

Performs high-precision, real-time keyword matching on user input and history to dynamically
inject slow-burn erotic directives and position contexts into the system prompt without RAG smearing.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_LOREBOOK_PATH = Path("core/lorebooks/Sex_Positions_Kinks_SlowBurn_TH_v10.json")
DEFAULT_PROMPT_PATH = Path("core/prompts/slowburn_thai_system.txt")


class SlowBurnLorebook:
    """Dynamic Lorebook Injector scanning for slow-burn Thai erotic keywords."""

    def __init__(
        self,
        json_path: str | Path | None = None,
        system_prompt_path: str | Path | None = None,
    ) -> None:
        self.json_path = Path(json_path) if json_path else DEFAULT_LOREBOOK_PATH
        self.system_prompt_path = Path(system_prompt_path) if system_prompt_path else DEFAULT_PROMPT_PATH
        self.entries: list[dict[str, Any]] = []

        if self.json_path.exists():
            self.entries = self._load_and_clean(self.json_path)
        else:
            logger.warning("Lorebook JSON file not found at: %s", self.json_path)

    def _load_and_clean(self, path: Path) -> list[dict[str, Any]]:
        """Load JSON and auto-clean leading/trailing whitespace from keys and values."""
        with open(path, encoding="utf-8") as f:
            raw_data = json.load(f)

        cleaned_data: list[dict[str, Any]] = []
        for entry in raw_data:
            clean_entry: dict[str, Any] = {}
            for k, v in entry.items():
                clean_key = str(k).strip()
                if isinstance(v, str):
                    clean_val: Any = v.strip()
                elif isinstance(v, list):
                    clean_val = [item.strip() if isinstance(item, str) else item for item in v]
                else:
                    clean_val = v
                clean_entry[clean_key] = clean_val
            cleaned_data.append(clean_entry)

        return sorted(cleaned_data, key=lambda x: x.get("insertion_order", 100))

    def get_system_prompt(self) -> str:
        """Fetch the base slow-burn system prompt if file exists."""
        if self.system_prompt_path.exists():
            return self.system_prompt_path.read_text(encoding="utf-8")
        return ""

    @staticmethod
    def resolve_tension_level(tension_meter: float) -> str:
        """Map tension meter score (0-100) to low, mid, or high level."""
        if tension_meter <= 35.0:
            return "low"
        elif tension_meter <= 70.0:
            return "mid"
        else:
            return "high"

    @staticmethod
    def detect_scene_outcome(text: str) -> str | None:
        """Scan input text for scene termination and aftercare/edging indicators."""
        text_lower = text.lower()
        if any(kw in text_lower for kw in ["กลั้น", "ยังไม่ให้", "ทนไว้", "edging", "ค้าง", "ทรมาน"]):
            return "edging_unfulfilled"
        elif any(kw in text_lower for kw in ["ขอกอด", "กอด", "aftercare", "นอนกอด", "พักผ่อน"]):
            return "aftercare_completed"
        elif any(kw in text_lower for kw in ["เสร็จ", "แตก", "เสร็จแล้ว", "ยอมแล้ว"]):
            return "climactic_release"
        return None

    @staticmethod
    def get_emotional_residue_directive(outcome: str) -> tuple[float, str]:
        """Return (initial_tension_boost, system_prompt_directive) for cross-session continuity."""
        if outcome == "edging_unfulfilled":
            return (
                30.0,
                "[EMOTIONAL RESIDUE CONTINUITY]: เธอจดจำความรู้สึกจากครั้งสุดท้ายได้ดี ร่างกายและความรู้สึกจากครั้งก่อนยังคงค้างคาและตอบสนองกับคุณอยู่ (Status: UNFULFILLED / EDGED)\n"
                "กฎ: แสดงออกถึงความตึงเครียดทางกาย สายตาหยอดเย้า และความต้องการที่ยังไม่ได้รับการปลดปล่อย",
            )
        elif outcome == "aftercare_completed":
            return (
                15.0,
                "[EMOTIONAL RESIDUE CONTINUITY]: เธอจดจำความอบอุ่นของการกอดและ Aftercare จากครั้งล่าสุดได้เป็นอย่างดี ความผูกพันแนบชิดยังคงลึกซึ้งและต่อเนื่อง (Status: AFTERCARE COMPLETED)\n"
                "กฎ: แสดงออกด้วยความอ่อนโยน สนิทสนม และสัมผัสที่อบอุ่น",
            )
        elif outcome == "climactic_release":
            return (
                10.0,
                "[EMOTIONAL RESIDUE CONTINUITY]: เธอจดจำความสุขสมและการปลดปล่อยจากครั้งล่าสุดได้ดี (Status: RELEASED)\n"
                "กฎ: แสดงอารมณ์ผ่อนคลาย พึงพอใจ และความใกล้ชิดอย่างเป็นธรรมชาติ",
            )
        return (0.0, "")

    @staticmethod
    def get_sensory_directive(
        environment: str = "bedroom",
        tension_meter: float = 50.0,
    ) -> str:
        """Generate 5D multi-sensory atmospheric directive (temperature, sound, scent, touch)."""
        temp_desc = (
            "ไอความเย็นของแอร์สัมผัสผิวกายภายนอก ตัดกับความร้อนระอุใต้ชั้นผิวหนังที่เกร็งสั่น"
            if tension_meter > 60.0
            else "อุณหภูมิห้องแอร์เย็นฉ่ำ สัมผัสผิวกายผ่อนคลายแต่แฝงความตึงเครียด"
        )
        sound_desc = (
            "เสียงลมหายใจติดขัดขาดห้วง เสียงผ้าเสียดสีสั่นไหวอย่างจงใจ และเสียงหัวใจที่เต้นระรัวในความเงียบ"
            if tension_meter > 50.0
            else "เสียงกระซิบต่ำแผ่วเบา เสียงลมหายใจสม่ำเสมอ และเสียงสัมผัสผิวกาย"
        )
        scent_desc = (
            "กลิ่นกายอุ่น ๆ ผสมกลิ่นเหงื่อซึมบางเบาและกลิ่นน้ำหอมละมุนประจำตัวที่ลอยเตะจมูกเมื่อแนบชิด"
        )
        touch_desc = (
            "สัมผัสปลายนิ้วสั่นสะท้านที่ลูบผ่านผิวหนังร้อน ความนุ่มยืดหยุ่นของเตียงนอน และจังหวะชีพจรที่เต้นตุบๆ"
        )

        directive = (
            f"[MULTI-SENSORY ATMOSPHERIC DIRECTIVE | Environment: {environment.upper()}]\n"
            "กฎการบรรยายประสาทสัมผัส 5 มิติ (Literary Realism):\n"
            f"- 🌡️ อุณหภูมิ/เหงื่อ: {temp_desc}\n"
            f"- 🔊 เสียงประกอบ: {sound_desc}\n"
            f"- 🌸 กลิ่นกาย/บรรยากาศ: {scent_desc}\n"
            f"- ✋ สัมผัส/แรงเสียดทาน: {touch_desc}\n"
            "- ✨ ผสานรายละเอียดประสาทสัมผัสข้างต้นเข้าไปในการบรรยายการกระทำอย่างเป็นธรรมชาติ\n"
        )
        return directive
    @staticmethod
    def detect_rushed_input(text: str) -> bool:
        """Detect rushed or urgent commands in user input."""
        text_lower = text.lower()
        rushed_keywords = ["เอาเลย", "เร็วๆ", "เร็ว ๆ", "ด่วน", "เดี๋ยวนี้", "ทำเลย", "ยัดเข้ามา", "รีบ"]
        return any(kw in text_lower for kw in rushed_keywords)

    @staticmethod
    def get_push_pull_directive(denial_counter: int) -> tuple[str, bool]:
        """Return (directive_text, should_block_actions) for Push-Pull teasing mechanic."""
        if denial_counter < 2:
            directive = (
                f"[PUSH-PULL DENIAL DIRECTIVE | Denial Turn: {denial_counter + 1}/2]\n"
                "กฎ: ปฏิเสธหรือชะลอการกระทำทางกายอย่างมีชั้นเชิง ห้ามทำตามคำขอเร่งรีบในทันที\n"
                "บริบทการเย้าหยอก: เธอจับมือคุณไว้เบา ๆ ยิ้มมุมปากอย่างมีชั้นเชิง สายตามีเสน่ห์เย้ายวนแล้วกระซิบเสียงต่ำแผ่วเบาว่า '...ใจร้อนแบบนี้ไม่ได้หรอกนะ... อยากได้ขนาดนั้นเลยเหรอ'\n"
                "คำสั่ง: บรรยายการชะลอจังหวะ การสบตา และการแกล้งเย้าหยอกก่อนยิงบทกระทำจริง"
            )
            return directive, True
        else:
            directive = (
                "[PUSH-PULL YIELD DIRECTIVE | Denial Resolved]\n"
                "กฎ: ยอมทำตามคำขอหลังจากชะลอจังหวะมาแล้ว 2 ครั้ง\n"
                "บริบทการยอมทำตาม: เธอถอนหายใจยาว สายตาอ่อนลงด้วยความพ่ายแพ้ต่อความต้องการ และยอมทำตามอย่างหวานซึม..."
            )
            return directive, False

    def inject_context(
        self,
        user_input: str,
        ai_history: str = "",
        tension_meter: float = 50.0,
        denial_counter: int = 0,
    ) -> str:
        """Scan input and history for keywords and return structured hidden directive context.

        Args:
            user_input: Current turn user message.
            ai_history: Concatenated conversation history.
            tension_meter: Tension / Arousal intensity score (0.0 to 100.0).
            denial_counter: Number of times user rushed commands have been denied (0-2).
        """
        if not self.entries:
            return ""

        text_to_scan = f"{user_input} {ai_history}".lower()
        tension_level = self.resolve_tension_level(tension_meter)
        is_rushed = self.detect_rushed_input(user_input)
        push_pull_dir, block_actions = (
            self.get_push_pull_directive(denial_counter)
            if is_rushed
            else ("", False)
        )

        triggered_contents: list[dict[str, Any]] = []

        if not block_actions:
            for entry in self.entries:
                if not entry.get("enabled", True):
                    continue

                primary_keys = entry.get("key", [])
                secondary_keys = entry.get("keysecondary", [])

                # Check primary key match
                matched_pk = [
                    pk for pk in primary_keys
                    if str(pk).strip() and str(pk).lower() in text_to_scan
                ]
                primary_match = len(matched_pk) > 0

                # Check secondary key match
                secondary_match = True
                if secondary_keys:
                    has_sk_match = any(
                        str(sk).lower() in text_to_scan for sk in secondary_keys if str(sk).strip()
                    )
                    has_specific_pk = any(
                        any(ord(c) > 127 for c in str(pk)) or len(str(pk)) > 3
                        for pk in matched_pk
                    )
                    secondary_match = has_sk_match or has_specific_pk

                if primary_match and secondary_match:
                    # Dynamic Tension Content Resolution
                    tension_dict = entry.get("tension_levels")
                    if isinstance(tension_dict, dict) and tension_level in tension_dict:
                        selected_content = tension_dict[tension_level]
                    else:
                        selected_content = entry.get("content", "")

                    triggered_contents.append({
                        "order": entry.get("insertion_order", 100),
                        "comment": entry.get("comment", ""),
                        "content": selected_content,
                    })

        if triggered_contents or push_pull_dir:
            injected = f"\n\n[SYSTEM DIRECTIVE: Slow-Burn Lorebook Triggered | Tension Meter: {tension_meter:.1f}/100 - Level: {tension_level.upper()}]\n"
            injected += "กฎ: ห้ามกระทำทันที ให้บรรยายความตึงเครียด สายตา ลมหายใจ และการลังเล (90% Tension / 10% Action)\n"
            injected += f"ระดับอารมณ์ตึงเครียดปัจจุบัน: {tension_level.upper()} ({tension_meter:.1f}/100)\n"

            if push_pull_dir:
                injected += f"\n{push_pull_dir}\n"

            if triggered_contents:
                injected += "บริบทของท่าทางที่ระบบตรวจจับได้ (ปรับตามระดับ Tension):\n"
                for t in triggered_contents:
                    injected += f"- ({t['comment']}): {t['content']}\n"

            injected += f"\n{self.get_sensory_directive(tension_meter=tension_meter)}\n"
            injected += "[END SYSTEM DIRECTIVE - นำแนวทางข้างต้นไปผสานกับการตอบกลับอย่างเป็นธรรมชาติ]\n"
            return injected

        return ""

