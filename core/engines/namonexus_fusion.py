from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from threading import RLock


class NamoNexusEngine:
    """
    NamoNexus Fusion Engine v4.0.0 (Bayesian Multimodal Fusion)
    ใช้ Golden Ratio (phi) เป็นค่าคงที่ในการถ่วงน้ำหนักสัญญาณประสาท
    """

    _state_root = Path("state") / "fusion_engine"
    _state_lock = RLock()
    _drift_cooldown_seconds = 5.0

    def __init__(self, persistence_key: str = "default"):
        self.persistence_key = persistence_key or "default"
        self.phi = 1.618034
        self.fused_score = 0.5
        self.confidence = 0.0
        self.has_drift_alarm = False
        self.drift_threshold = 0.4
        self.history: list[dict[str, float | str]] = []
        self.last_drift_at: float | None = None
        self.logger = logging.getLogger(__name__)
        self._load_state()

    def _state_path(self) -> Path:
        safe_key = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in self.persistence_key)
        return self._state_root / f"{safe_key}.json"

    def _load_state(self) -> None:
        path = self._state_path()
        try:
            with self._state_lock:
                if not path.exists():
                    return
                data = json.loads(path.read_text(encoding="utf-8"))
            self.fused_score = float(data.get("fused_score", self.fused_score))
            self.confidence = float(data.get("confidence", self.confidence))
            self.has_drift_alarm = bool(data.get("has_drift_alarm", self.has_drift_alarm))
            raw_history = data.get("history", [])
            if isinstance(raw_history, list):
                self.history = [item for item in raw_history if isinstance(item, dict)]
            last_drift_at = data.get("last_drift_at")
            self.last_drift_at = float(last_drift_at) if last_drift_at is not None else None
        except Exception:
            self.history = []
            self.last_drift_at = None

    def _save_state(self) -> None:
        path = self._state_path()
        payload = {
            "fused_score": self.fused_score,
            "confidence": self.confidence,
            "has_drift_alarm": self.has_drift_alarm,
            "last_drift_at": self.last_drift_at,
            "history": self.history[-200:],
        }
        try:
            with self._state_lock:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))

    def _recover_from_drift(self) -> None:
        if not self.has_drift_alarm:
            return
        if self.last_drift_at is None:
            self.has_drift_alarm = False
            return
        if time.time() - self.last_drift_at >= self._drift_cooldown_seconds:
            self.has_drift_alarm = False

    def update(self, score: float, confidence: float, modality: str):
        """รับค่าจาก Text/Voice/Face และคำนวณการหลอมรวม"""
        score = self._clamp(float(score))
        confidence = self._clamp(float(confidence))
        self._recover_from_drift()

        # น้ำหนักตาม modality (Face > Voice > Text)
        weight = {"face": self.phi**2, "voice": self.phi, "text": 1.0}.get(modality, 1.0)

        # Bayesian fusion approximation
        new_fused = (self.fused_score + (score * confidence * weight)) / (1 + weight)
        new_fused = self._clamp(new_fused)

        # Drift Detection
        if abs(new_fused - self.fused_score) > self.drift_threshold:
            self.has_drift_alarm = True
            self.last_drift_at = time.time()
            self.logger.warning(
                f"[DRIFT ALARM]: Detected emotional deviation! Fused: {new_fused:.2f}"
            )
        else:
            self.has_drift_alarm = False
            self.last_drift_at = None

        self.fused_score = new_fused
        self.confidence = confidence
        self.history.append(
            {
                "timestamp": time.time(),
                "modality": modality,
                "score": score,
                "confidence": confidence,
                "fused_score": self.fused_score,
            }
        )
        self._save_state()

    def explain(self) -> str:
        return f"Fusion Score: {self.fused_score:.2f} (Confidence: {self.confidence:.2f})"
