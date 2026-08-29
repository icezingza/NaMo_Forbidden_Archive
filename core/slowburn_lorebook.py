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

    def inject_context(self, user_input: str, ai_history: str = "") -> str:
        """Scan input and history for keywords and return structured hidden directive context."""
        if not self.entries:
            return ""

        text_to_scan = f"{user_input} {ai_history}".lower()
        triggered_contents: list[dict[str, Any]] = []

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
                # If matched primary key is specific (e.g. contains Thai chars or length > 3), allow trigger even without generic secondary keys like 'sex'/'fuck'
                has_specific_pk = any(
                    any(ord(c) > 127 for c in str(pk)) or len(str(pk)) > 3
                    for pk in matched_pk
                )
                secondary_match = has_sk_match or has_specific_pk

            if primary_match and secondary_match:
                triggered_contents.append({
                    "order": entry.get("insertion_order", 100),
                    "comment": entry.get("comment", ""),
                    "content": entry.get("content", ""),
                })

        if triggered_contents:
            injected = "\n\n[SYSTEM DIRECTIVE: Slow-Burn Lorebook Triggered]\n"
            injected += "กฎ: ห้ามกระทำทันที ให้บรรยายความตึงเครียด สายตา ลมหายใจ และการลังเล (90% Tension / 10% Action)\n"
            injected += "บริบทของท่าทางที่ระบบตรวจจับได้:\n"
            for t in triggered_contents:
                injected += f"- ({t['comment']}): {t['content']}\n"
            injected += "[END SYSTEM DIRECTIVE - นำแนวทางข้างต้นไปผสานกับการตอบกลับอย่างเป็นธรรมชาติ]\n"
            return injected

        return ""
