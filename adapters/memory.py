import json
import datetime
import os
from typing import Any

import requests

from config import settings


class MemoryAdapter:
    """Adapter สำหรับบันทึกความทรงจำระยะยาว

    เขียนลงไฟล์ JSON เสมอ (local store).
    ถ้า MEMORY_API_URL ถูกตั้งค่าไว้ จะ forward ไปยัง memory service ด้วย
    เพื่อให้ทุก engine ใช้ store เดียวกัน (unified memory).
    """

    def __init__(self, db_file: str = "memory_history.json") -> None:
        self.db_file = db_file
        self._memory_url: str | None = settings.memory_api_url
        self._memory_key: str | None = settings.memory_api_key

        if not os.path.exists(self.db_file):
            with open(self.db_file, "w", encoding="utf-8") as f:
                json.dump([], f)

        remote = f" + remote({self._memory_url})" if self._memory_url else ""
        print(f"[MemoryAdapter]: Initialized. Storage: {self.db_file}{remote}")

    def store_interaction(
        self,
        user_input: str,
        response: str,
        emotions: Any = None,
        *,
        arousal_level: int | None = None,
        infection_status: str | None = None,
        session_id: str | None = None,
        desire_map: dict | None = None,
    ) -> None:
        """บันทึกบทสนทนาพร้อม metadata ลง local JSON และ (optionally) memory service."""
        entry: dict[str, Any] = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "session_id": session_id,
            "user": user_input,
            "bot": response,
            "state_snapshot": emotions,
            "arousal_level": arousal_level,
            "infection_status": infection_status,
            "desire_map": desire_map,
        }
        # Drop None values to keep the file tidy
        entry = {k: v for k, v in entry.items() if v is not None}

        # 1. Local JSON store
        try:
            with open(self.db_file, "r+", encoding="utf-8") as f:
                history: list = json.load(f)
                history.append(entry)
                f.seek(0)
                json.dump(history, f, ensure_ascii=False, indent=4)
        except Exception as exc:
            print(f"[MemoryAdapter]: local write error: {exc}")

        # 2. Forward to memory service when configured (unified store)
        if self._memory_url:
            self._forward_to_service(user_input, response, session_id, entry)

    def _forward_to_service(
        self,
        user_input: str,
        response: str,
        session_id: str | None,
        metadata: dict,
    ) -> None:
        payload = {
            "content": f"user: {user_input}\nassistant: {response}",
            "type": "contextual",
            "session_id": session_id,
            "metadata": metadata,
        }
        headers: dict[str, str] = {}
        if self._memory_key:
            headers["x-api-key"] = self._memory_key
        try:
            requests.post(self._memory_url, json=payload, headers=headers, timeout=2)
        except requests.RequestException as exc:
            print(f"[MemoryAdapter]: remote forward failed: {exc}")

    def get_last_conversation(self) -> dict | None:
        """ดึงบทสนทนาล่าสุดมาดูบริบท"""
        try:
            with open(self.db_file, "r", encoding="utf-8") as f:
                history: list = json.load(f)
                return history[-1] if history else None
        except Exception:
            return None
