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
        self.system_prompt_path = (
            Path(system_prompt_path) if system_prompt_path else DEFAULT_PROMPT_PATH
        )
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
        if any(
            kw in text_lower for kw in ["กลั้น", "ยังไม่ให้", "ทนไว้", "edging", "ค้าง", "ทรมาน"]
        ):
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
        scent_desc = "กลิ่นกายอุ่น ๆ ผสมกลิ่นเหงื่อซึมบางเบาและกลิ่นน้ำหอมละมุนประจำตัวที่ลอยเตะจมูกเมื่อแนบชิด"
        touch_desc = "สัมผัสปลายนิ้วสั่นสะท้านที่ลูบผ่านผิวหนังร้อน ความนุ่มยืดหยุ่นของเตียงนอน และจังหวะชีพจรที่เต้นตุบๆ"

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
        rushed_keywords = [
            "เอาเลย",
            "เร็วๆ",
            "เร็ว ๆ",
            "ด่วน",
            "เดี๋ยวนี้",
            "ทำเลย",
            "ยัดเข้ามา",
            "รีบ",
        ]
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

    @staticmethod
    def detect_micro_moments(text: str) -> bool:
        """Detect micro-interaction keywords (eye contact, breath, hesitation, soft touch)."""
        text_lower = text.lower()
        micro_keywords = [
            "สบตา",
            "มองตา",
            "สายตา",
            "ลมหายใจ",
            "ถอนหายใจ",
            "หายใจถี่",
            "ลังเล",
            "ลูบ",
            "สัมผัส",
            "แผ่วเบา",
            "กระซิบ",
            "สะกิด",
            "แนบชิด",
        ]
        return any(kw in text_lower for kw in micro_keywords)

    @classmethod
    def calculate_non_linear_tension(
        cls,
        current_tension: float,
        is_rushed: bool,
        micro_detected: bool,
    ) -> tuple[float, str]:
        """Calculate non-linear dynamic tension curve (0-100)."""
        if is_rushed:
            penalized = current_tension * 0.7  # -30% penalty for rushing
            resistance_note = "she pulls back slightly... [Tension Penalized: -30% for rushing]"
            return round(max(0.0, penalized), 1), resistance_note
        elif micro_detected:
            # Exponential slow increment curve
            remaining = max(0.0, 100.0 - current_tension)
            increment = max(3.0, remaining * 0.20)
            boosted = min(100.0, current_tension + increment)
            return round(boosted, 1), "[Micro-Moment Detected: Tension Exponentially Increased]"
        else:
            return round(current_tension, 1), ""

    @staticmethod
    def check_safeword(text: str) -> tuple[bool, str]:
        """Check if user triggered a safeword (e.g. 'หยุด', 'พอก่อน', 'ส้ม', 'red', 'stop')."""
        text_lower = text.lower()
        safewords = ["หยุด", "พอก่อน", "ส้ม", "red", "stop", "ไม่เอาแล้ว", "พอแล้ว"]
        for sw in safewords:
            if sw in text_lower:
                directive = (
                    f"[SAFEWORD PROTOCOL TRIGGERED | Safeword: '{sw.upper()}']\n"
                    "กฎเหล็ก: หยุดฉากทางกายและความตึงเครียดทันที! สลับเข้าสู่โหมด Safe Aftercare ปลอบประโลมอย่างอบอุ่นและให้ความปลอดภัย 100%\n"
                    "คำสั่ง: ถามไถ่ด้วยความเคารพ อ่อนโยน และแน่ใจว่าผู้ใช้รู้สึกปลอดภัย"
                )
                return True, directive
        return False, ""

    @staticmethod
    def check_memory_anchors(text: str, anchors: list[dict[str, str]]) -> str | None:
        """Scan text for memory anchors (phrases, scents, locations) to trigger flashbacks."""
        text_lower = text.lower()
        for anchor in anchors:
            term = str(anchor.get("term", "")).lower()
            if term and term in text_lower:
                memory_text = anchor.get("memory_text", "")
                return (
                    f"[EMOTIONAL FLASHBACK TRIGGERED | Anchor Term: '{term.upper()}']\n"
                    f"ความทรงจำข้ามเวลาที่พรั่งพรูขึ้นมา: {memory_text}\n"
                    "กฎ: แสดงออกว่าคำพูด/กลิ่น/สิ่งที่ผู้ใช้พูดถึง ไปกระตุ้นความทรงจำในอดีตอย่างลึกซึ้ง"
                )
        return None

    @staticmethod
    def evaluate_tease_and_deny(
        tease_streak: int,
        user_input: str,
    ) -> tuple[bool, str, int]:
        """Evaluate Tease & Deny Engine dice roll/streak to determine surrender or tease outcome."""
        if tease_streak >= 3:
            directive = (
                f"[TEASE & DENY ENGINE | SURRENDER MOMENT TRIGGERED (Streak: {tease_streak})]\n"
                "ผลลัพธ์: การปฏิเสธยืดเยื้อสะสมครบ 3 ครั้ง! ยอมทำตามคำขอแล้ว แต่ยังคงอำนาจในการควบคุมจังหวะ (she finally gives in, but on her terms...)\n"
                "กฎ: มอบรางวัลฉากลึกซึ้งสูงสุด บรรยายสายตายอมจำนนที่เปี่ยมเสน่ห์ ความตึงเครียดที่พุ่งสุดขีด และการเคลื่อนไหวที่ตระการตา"
            )
            return True, directive, 0

        next_streak = tease_streak + 1
        directive = (
            f"[TEASE & DENY ENGINE | TEASE IN PROGRESS (Streak: {next_streak}/3)]\n"
            "กฎ: ยืดเยื้อบทสนทนาต่อไป บรรยายสัมผัสลูบไล้และสายตาสบประมาทอย่างยั่วเย้า ยิ่งรอ ยิ่งได้ฉากที่ลึกซึ้งขึ้น"
        )
        return False, directive, next_streak

    @staticmethod
    def get_push_pull_phase_directive(phase: str) -> str:
        """Return 3-Phase Realistic Push-Pull Dynamics directive (Resistance -> Negotiation -> Surrender)."""
        if phase == "resistance":
            return (
                "[PUSH-PULL DYNAMICS | Phase 1: RESISTANCE (เล่นตัว/หาข้ออ้าง)]\n"
                "กฎ: AI แสดงการเล่นตัว แกล้งถอยตัวออกเล็กน้อย จับมือไว้เบา ๆ และหาข้ออ้างหยอดเย้า ห้ามยินยอมทันที"
            )
        elif phase == "negotiation":
            return (
                "[PUSH-PULL DYNAMICS | Phase 2: NEGOTIATION (ต่อรอง/ท้าทาย)]\n"
                "กฎ: AI เริ่มต่อรอง กระซิบข้อตกลงใกล้หู ท้าทายให้แสดงความหลงใหลและสบตาแน่นนิ่งก่อนทำตาม"
            )
        elif phase == "surrender":
            return (
                "[PUSH-PULL DYNAMICS | Phase 3: SURRENDER (ยอม แต่ยังครองอำนาจควบคุมจังหวะ)]\n"
                "กฎ: AI ยอมกายให้ แต่ยังคงครองอำนาจควบคุมจังหวะลมหายใจ การเคลื่อนไหว และสายตาเหนือผู้ใช้"
            )
        return ""

    @staticmethod
    def check_erotic_memory_palace(user_input: str, memories: list[dict[str, str]]) -> str | None:
        """Scan input for recall triggers and return contextually restored signature intimate memories."""
        text_lower = user_input.lower()
        recall_triggers = ["จำตอน", "จำคืน", "จำได้ไหม", "ตอนนั้น", "คืนนั้น", "remember"]
        if any(trig in text_lower for trig in recall_triggers) and memories:
            latest = memories[-1]
            summary = latest.get("summary", "ฉากใกล้ชิดอันลึกซึ้งในคืนก่อน")
            return (
                "[EROTIC MEMORY PALACE RECALL | Signature Moment Restored]\n"
                f"ความทรงจำฉากลึกซึ้งในอดีตที่ระบบดึงกลับมา: {summary}\n"
                "กฎ: รำลึกถึงความทรงจำนี้ด้วยสายตาและน้ำเสียงที่เปี่ยมความรู้สึก อ้างอิงถึงรายละเอียดในคืนนั้นอย่างลึกซึ้ง"
            )
        return None

    @staticmethod
    def resolve_attachment_style(trust_score: float, tension_meter: float, scene_count: int) -> str:
        """Resolve dynamic attachment style (secure, anxious, avoidant, disorganized)."""
        if trust_score < 40.0 and tension_meter > 70.0:
            return "disorganized"
        elif trust_score < 50.0:
            return "anxious"
        elif scene_count > 5 and tension_meter < 35.0:
            return "avoidant"
        else:
            return "secure"

    @staticmethod
    def get_attachment_style_directive(style: str) -> str:
        """Return behavioral directive for current attachment style."""
        if style == "anxious":
            return (
                "[ATTACHMENT STYLE DIRECTIVE | Style: ANXIOUS]\n"
                "กฎ: แสดงความห่วงหา ต้องการการยืนยัน แอบขี้หึงและเรียกร้องสายตาห่วงใยจากผู้ใช้อยู่เสมอ"
            )
        elif style == "avoidant":
            return (
                "[ATTACHMENT STYLE DIRECTIVE | Style: AVOIDANT]\n"
                "กฎ: แกล้งเว้นระยะห่างเล็กน้อยหลังฉากลึกซึ้ง ซ่อนความสับสนในใจเบื้องหลังสายตาเรียบเฉย"
            )
        elif style == "disorganized":
            return (
                "[ATTACHMENT STYLE DIRECTIVE | Style: DISORGANIZED]\n"
                "กฎ: สลับอารมณ์อย่างรุนแรง ต้องการความใกล้ชิดแต่หวาดกลัว สลับระหว่างการเข้าหาและการถอยห่างอย่างเย้ายวน"
            )
        else:  # secure
            return (
                "[ATTACHMENT STYLE DIRECTIVE | Style: SECURE]\n"
                "กฎ: มั่นใจในความรู้สึก เปิดใจอย่างอ่อนโยน ค่อยเป็นค่อยไป แต่ลึกซึ้งและแนบแน่น"
            )

    def get_triggered_entries(
        self,
        user_input: str,
        ai_history: str = "",
        current_tension: float = 50.0,
        current_beat: str = "escalation",
    ) -> list[dict[str, Any]]:
        """Retrieve lorebook entries matching keywords, tension threshold, and sorted by beat match.

        Args:
            user_input: Current turn user message.
            ai_history: Concatenated conversation history.
            current_tension: Active tension score (0.0 to 100.0).
            current_beat: Active narrative beat (tease, resistance, escalation, resolution, recovery).

        Returns:
            Sorted list of triggered entry dictionaries.
        """
        if not self.entries:
            return []

        text_to_scan = f"{user_input} {ai_history}".lower()
        tension_level = self.resolve_tension_level(current_tension)
        triggered: list[dict[str, Any]] = []

        for entry in self.entries:
            if not entry.get("enabled", True):
                continue

            # 1. Tension Threshold Range Check
            threshold = entry.get("tension_threshold")
            if isinstance(threshold, (list, tuple)) and len(threshold) == 2:
                min_t, max_t = float(threshold[0]), float(threshold[1])
                if not (min_t <= current_tension <= max_t):
                    continue

            primary_keys = entry.get("key", [])
            secondary_keys = entry.get("keysecondary", [])

            # Check primary key match
            matched_pk = [
                pk for pk in primary_keys if str(pk).strip() and str(pk).lower() in text_to_scan
            ]
            primary_match = len(matched_pk) > 0

            # Check secondary key match
            secondary_match = True
            if secondary_keys:
                has_sk_match = any(
                    str(sk).lower() in text_to_scan for sk in secondary_keys if str(sk).strip()
                )
                has_specific_pk = any(
                    any(ord(c) > 127 for c in str(pk)) or len(str(pk)) > 3 for pk in matched_pk
                )
                secondary_match = has_sk_match or has_specific_pk

            if primary_match and secondary_match:
                # Dynamic Tension Content Resolution
                tension_dict = entry.get("tension_levels")
                if isinstance(tension_dict, dict) and tension_level in tension_dict:
                    selected_content = tension_dict[tension_level]
                else:
                    selected_content = entry.get("content", "")

                entry_beat = entry.get("beat", "escalation")
                beat_match = 1 if entry_beat == current_beat else 0
                priority = entry.get("priority", 1)

                triggered.append(
                    {
                        "beat_match": beat_match,
                        "priority": priority,
                        "order": entry.get("insertion_order", 100),
                        "comment": entry.get("comment", ""),
                        "content": selected_content,
                        "beat": entry_beat,
                        "entry_id": entry.get("id"),
                    }
                )

        # Sort by Beat Match (descending), Priority (descending), Insertion Order (descending)
        if triggered:
            triggered.sort(
                key=lambda x: (x["beat_match"], x["priority"], x["order"]),
                reverse=True,
            )

        return triggered

    def inject_context(
        self,
        user_input: str,
        ai_history: str = "",
        tension_meter: float = 50.0,
        denial_counter: int = 0,
        current_beat: str = "escalation",
    ) -> str:
        """Scan input and history for keywords and return structured hidden directive context.

        Args:
            user_input: Current turn user message.
            ai_history: Concatenated conversation history.
            tension_meter: Tension / Arousal intensity score (0.0 to 100.0).
            denial_counter: Number of times user rushed commands have been denied (0-2).
            current_beat: Active narrative beat (tease, resistance, escalation, resolution, recovery).
        """
        if not self.entries:
            return ""

        tension_level = self.resolve_tension_level(tension_meter)
        is_rushed = self.detect_rushed_input(user_input)
        push_pull_dir, block_actions = (
            self.get_push_pull_directive(denial_counter) if is_rushed else ("", False)
        )

        triggered_contents = (
            []
            if block_actions
            else self.get_triggered_entries(
                user_input=user_input,
                ai_history=ai_history,
                current_tension=tension_meter,
                current_beat=current_beat,
            )
        )

        if triggered_contents or push_pull_dir or tension_meter >= 85.0:
            injected = f"\n\n[SYSTEM DIRECTIVE: Slow-Burn Lorebook Triggered | Tension Meter: {tension_meter:.1f}/100 - Level: {tension_level.upper()} - Beat: {current_beat.upper()}]\n"
            injected += "กฎ: ห้ามกระทำทันที ให้บรรยายความตึงเครียด สายตา ลมหายใจ และการลังเล (90% Tension / 10% Action)\n"
            injected += (
                f"ระดับอารมณ์ตึงเครียดปัจจุบัน: {tension_level.upper()} ({tension_meter:.1f}/100)\n"
            )

            if tension_meter >= 85.0:
                injected += (
                    "\n[BREAKING POINT DIRECTIVE | Internal Conflict Triggered]\n"
                    "ความตึงเครียดพุ่งสูงถึงจุดวิกฤต (>85%)! ร่างกายสั่นสะท้าน ลมหายใจหอบกระชั้น ต้องการปลดปล่อยอย่างรุนแรง แต่จิตใจยังพยายามฝืนกลั้นและเล่นตัวเป็นครั้งสุดท้าย\n"
                    "กฎ: บรรยายการต่อสู้กันระหว่างความต้านทานในใจกับความต้องการทางกายที่ควบคุมไม่ได้ (ทนไม่ไหว vs. ยังอยากเล่นตัว)\n"
                )

            if push_pull_dir:
                injected += f"\n{push_pull_dir}\n"

            if triggered_contents:
                injected += "บริบทของท่าทางที่ระบบตรวจจับได้ (ปรับตามระดับ Tension และ Beat):\n"
                for t in triggered_contents:
                    injected += f"- ({t['comment']} | Beat: {t['beat'].upper()}): {t['content']}\n"

            injected += f"\n{self.get_sensory_directive(tension_meter=tension_meter)}\n"
            injected += (
                "[END SYSTEM DIRECTIVE - นำแนวทางข้างต้นไปผสานกับการตอบกลับอย่างเป็นธรรมชาติ]\n"
            )
            return injected

        return ""
