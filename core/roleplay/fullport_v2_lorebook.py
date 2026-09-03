"""NaMo Roleplay FullPort v2 loader.

Thai-first, lossless-source runtime context injector built from the four original ZIP
archives supplied by the user.  It deliberately does not depend on v1 artifacts.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "lorebooks"
DEFAULT_FILES = (
    "advanced_personality_traits_th_v2.json",
    "story_engine_th_v2.json",
    "dynamic_erp_bilingual_v2.json",
    "heightened_nsfw_bilingual_v2.json",
)

@dataclass(frozen=True, slots=True)
class FullPortMatch:
    entry_id: str
    category: str
    name_th: str
    priority: int
    insertion_order: int
    text: str
    source_uid: int | str | None
    match_score: int = 0

class FullPortV2Lorebook:
    """Load and match FullPort v2 entries without flattening the corpora into one prompt."""

    def __init__(
        self,
        data_dir: str | Path | None = None,
        *,
        mode: str = "full",
        max_matches: int = 6,
        max_context_chars: int = 18_000,
    ) -> None:
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
        self.mode = mode if mode in {"full", "compact"} else "full"
        self.max_matches = max(1, int(max_matches))
        self.max_context_chars = max(2_000, int(max_context_chars))
        self.entries: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        loaded: list[dict[str, Any]] = []
        for filename in DEFAULT_FILES:
            path = self.data_dir / filename
            if not path.exists():
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            for entry in payload.get("entries", []):
                if not isinstance(entry, dict) or not entry.get("enabled", True):
                    continue
                item = dict(entry)
                item["_file"] = filename
                loaded.append(item)
        self.entries = loaded

    @staticmethod
    def _norm(text: str) -> str:
        return " ".join((text or "").casefold().split())

    @classmethod
    def _keyword_match_score(cls, haystack: str, key: str) -> int:
        """Return a specificity score for a lorebook key match.

        Phrase keys outrank broad singleton keys.  This prevents generic technical
        triggers such as ``deep`` from crowding out an exact phrase such as
        ``deep kiss`` while preserving singleton matching when no phrase exists.
        """
        if not key:
            return 0
        if len(key) >= 2 and key.startswith("/") and key.endswith("/"):
            pattern = key[1:-1]
            try:
                return 30 if re.search(pattern, haystack, re.IGNORECASE) is not None else 0
            except re.error:
                return 0

        normalized_key = cls._norm(key)
        if not normalized_key:
            return 0

        # ASCII word-like keys use lexical boundaries to avoid accidental substring
        # hits (for example ``oral`` inside an unrelated longer token).
        if re.fullmatch(r"[a-z0-9_+\- ]+", normalized_key):
            pattern = r"(?<![a-z0-9_])" + re.escape(normalized_key).replace(r"\ ", r"\s+") + r"(?![a-z0-9_])"
            if re.search(pattern, haystack, re.IGNORECASE) is None:
                return 0
        elif normalized_key not in haystack:
            return 0

        token_count = len(normalized_key.split())
        if token_count >= 2:
            return 120 + token_count * 20 + min(len(normalized_key), 80)
        if any(ord(ch) > 127 for ch in normalized_key):
            return 55 + min(len(normalized_key), 40)
        return 25 + min(len(normalized_key), 30)

    @staticmethod
    def _entry_name(entry: dict[str, Any]) -> str:
        return str(entry.get("name_th") or entry.get("comment_th") or entry.get("comment_en") or entry.get("id") or "entry")

    def _render_entry(self, entry: dict[str, Any]) -> str:
        thai = str(entry.get("content_th") or entry.get("thai_runtime_directive") or "").strip()
        source = str(entry.get("source_content_en") or "").strip()
        include_source = bool(entry.get("inject_source_en_in_full_mode", entry.get("preserve_source_in_full_mode", False)))
        if self.mode == "full" and include_source and source:
            return f"{thai}\n\n[SOURCE DETAIL — preserve nuance]\n{source}" if thai else source
        return thai or source

    def get_base_context(self) -> str:
        """Return stable Thai context suitable for a system-prefix block.

        Only high-value structural entries are included here. Technical constant entries
        are intentionally excluded to avoid context bloat and prompt collisions.
        """
        wanted = {"story:1", "story:7", "personality:1"}
        blocks=[]
        for entry in self.entries:
            if entry.get("id") in wanted:
                text=self._render_entry(entry)
                if text:
                    blocks.append(f"[{self._entry_name(entry)}]\n{text}")
        return "\n\n".join(blocks)

    def match_entries(self, user_input: str, *, ai_history: str = "") -> list[FullPortMatch]:
        haystack=self._norm(f"{user_input}\n{ai_history}")
        matches: list[FullPortMatch]=[]
        for entry in self.entries:
            keys=entry.get("keys_bilingual") or entry.get("keys") or []
            if not isinstance(keys, list):
                continue
            scores=[self._keyword_match_score(haystack, str(k)) for k in keys if str(k).strip()]
            positive_scores=[score for score in scores if score > 0]
            best_key_score=max(positive_scores, default=0)
            # Multiple independent matching aliases are stronger evidence than one broad key.
            match_score=best_key_score + min(60, max(0, len(positive_scores) - 1) * 20)
            # Questions source entry uses a broad regex. Avoid triggering it for every message;
            # require a question marker or Thai question particle/word.
            if entry.get("id") == "story:4":
                matched_question = bool(re.search(r"\?|ไหม\b|หรือเปล่า\b|ทำไม\b|อะไร\b|อย่างไร\b|ยังไง\b|เมื่อไหร่\b|ที่ไหน\b", user_input, re.IGNORECASE))
                match_score = max(match_score, 80 if matched_question else 0) if matched_question else 0
            if match_score <= 0:
                continue
            text=self._render_entry(entry)
            if not text:
                continue
            matches.append(FullPortMatch(
                entry_id=str(entry.get("id")), category=str(entry.get("category","unknown")),
                name_th=self._entry_name(entry), priority=int(entry.get("priority",100) or 100),
                insertion_order=int(entry.get("insertion_order",100) or 100), text=text,
                source_uid=entry.get("source_uid"), match_score=match_score,
            ))

        # If a specific phrase matched, suppress broad singleton collisions from unrelated
        # technical entries.  Otherwise preserve normal singleton behavior.
        best_score=max((m.match_score for m in matches), default=0)
        if best_score >= 120:
            cutoff=max(80, int(best_score * 0.55))
            matches=[m for m in matches if m.match_score >= cutoff]

        matches.sort(
            key=lambda m:(m.match_score, m.priority, -m.insertion_order),
            reverse=True,
        )
        return matches[: self.max_matches]

    def inject_context(
        self,
        user_input: str,
        ai_history: str = "",
        tension_meter: float | None = None,
        denial_counter: int | None = None,
        **_: Any,
    ) -> str:
        """Compatibility-style injector; extra SlowBurnLorebook args are accepted."""
        del tension_meter, denial_counter
        matches=self.match_entries(user_input, ai_history=ai_history)
        if not matches:
            return ""
        blocks=[f"[FULLPORT V2 | {m.category} | {m.name_th} | {m.entry_id}]\n{m.text}" for m in matches]
        result="\n\n".join(blocks)
        if len(result) > self.max_context_chars:
            result=result[: self.max_context_chars].rsplit("\n",1)[0] + "\n[TRUNCATED BY FULLPORT CONTEXT BUDGET]"
        return result

    def status(self) -> dict[str, Any]:
        by_category: dict[str,int]={}
        for e in self.entries:
            cat=str(e.get("category","unknown")); by_category[cat]=by_category.get(cat,0)+1
        return {"mode":self.mode,"entries":len(self.entries),"categories":by_category,"data_dir":str(self.data_dir)}
