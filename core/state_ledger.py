import copy
import json
import math
import os
import tempfile
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock, RLock
from typing import Any, ClassVar


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class StateLedgerError(RuntimeError):
    """Base error for state-ledger persistence failures."""


class StateLedgerCorruptionError(StateLedgerError):
    """Raised when stored ledger data cannot be safely interpreted."""


class StateConflictError(StateLedgerError):
    """Raised when a stale state snapshot attempts to overwrite a newer turn."""


@dataclass(frozen=True, slots=True)
class SessionState:
    session_id: str
    relationship_stage: str = "awakening"
    fused_score: float = 0.0
    attachment_style: str = "secure"
    confidence: float = 1.0
    turn_count: int = 0
    last_updated: str = field(default_factory=_utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)


class StateLedger:
    SCHEMA_VERSION = 1
    _locks_guard: ClassVar[Lock] = Lock()
    _path_locks: ClassVar[dict[Path, RLock]] = {}

    def __init__(
        self,
        storage_path: str | os.PathLike[str] = "state/namo_state.json",
        *,
        history_limit: int = 500,
    ) -> None:
        if isinstance(history_limit, bool) or not isinstance(history_limit, int):
            raise TypeError("history_limit must be an integer")
        if history_limit <= 0:
            raise ValueError("history_limit must be positive")

        self.storage_path = Path(storage_path)
        self.history_limit = history_limit
        lock_key = self.storage_path.resolve()
        with self._locks_guard:
            self._lock = self._path_locks.setdefault(lock_key, RLock())

    @staticmethod
    def _validate_session_id(session_id: str) -> str:
        if not isinstance(session_id, str):
            raise TypeError("session_id must be a string")
        if not session_id.strip():
            raise ValueError("session_id must not be empty")
        if len(session_id) > 256:
            raise ValueError("session_id must not exceed 256 characters")
        return session_id

    @staticmethod
    def _finite_float(value: Any, field_name: str) -> float:
        if isinstance(value, bool):
            raise TypeError(f"{field_name} must be numeric")
        try:
            result = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(f"{field_name} must be numeric") from exc
        if not math.isfinite(result):
            raise ValueError(f"{field_name} must be finite")
        return result

    @staticmethod
    def _validate_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(metadata, dict):
            raise TypeError("metadata must be a dictionary")
        isolated = copy.deepcopy(metadata)
        try:
            json.dumps(isolated, ensure_ascii=False, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError("metadata must be JSON-serializable") from exc
        return isolated

    @staticmethod
    def _stage_for_score(score: float) -> str:
        if score >= 0.8:
            return "maximum_resonance"
        if score >= 0.5:
            return "deep_attachment"
        if score >= 0.2:
            return "synchronized"
        return "awakening"

    @classmethod
    def _empty_ledger(cls) -> dict[str, Any]:
        return {"schema_version": cls.SCHEMA_VERSION, "sessions": {}}

    def _migrate_legacy(self, data: dict[str, Any]) -> dict[str, Any]:
        if isinstance(data.get("session_id"), str):
            session_id = self._validate_session_id(data["session_id"])
            return {
                "schema_version": self.SCHEMA_VERSION,
                "sessions": {session_id: {"state": data, "transitions": []}},
            }

        if data and all(isinstance(value, dict) for value in data.values()):
            sessions = {}
            for session_id, state in data.items():
                validated_id = self._validate_session_id(session_id)
                migrated_state = dict(state)
                migrated_state["session_id"] = validated_id
                sessions[validated_id] = {"state": migrated_state, "transitions": []}
            return {"schema_version": self.SCHEMA_VERSION, "sessions": sessions}

        raise StateLedgerCorruptionError("unsupported state-ledger schema")

    def _read_unlocked(self) -> dict[str, Any]:
        if not self.storage_path.exists():
            return self._empty_ledger()
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise StateLedgerCorruptionError("state ledger is unreadable or corrupt") from exc
        if not isinstance(data, dict):
            raise StateLedgerCorruptionError("state ledger root must be an object")
        if "schema_version" not in data:
            return self._migrate_legacy(data)
        if data.get("schema_version") != self.SCHEMA_VERSION:
            raise StateLedgerCorruptionError(
                f"unsupported state-ledger version: {data.get('schema_version')}"
            )
        if not isinstance(data.get("sessions"), dict):
            raise StateLedgerCorruptionError("state ledger sessions must be an object")
        return data

    def _deserialize_state(self, session_id: str, payload: Any) -> SessionState:
        if not isinstance(payload, dict):
            raise StateLedgerCorruptionError("session state must be an object")
        try:
            stored_session_id = payload.get("session_id", session_id)
            if stored_session_id != session_id:
                raise StateLedgerCorruptionError("session key does not match stored session_id")
            score = self._finite_float(payload.get("fused_score", 0.0), "fused_score")
            confidence = self._finite_float(payload.get("confidence", 1.0), "confidence")
            turn_count = payload.get("turn_count", 0)
            if isinstance(turn_count, bool) or not isinstance(turn_count, int) or turn_count < 0:
                raise StateLedgerCorruptionError("turn_count must be a non-negative integer")
            return SessionState(
                session_id=session_id,
                relationship_stage=str(payload.get("relationship_stage", "awakening")),
                fused_score=max(0.0, min(1.0, score)),
                attachment_style=str(payload.get("attachment_style", "secure")),
                confidence=max(0.0, min(1.0, confidence)),
                turn_count=turn_count,
                last_updated=str(payload.get("last_updated", _utc_now())),
                metadata=self._validate_metadata(payload.get("metadata", {})),
            )
        except StateLedgerCorruptionError:
            raise
        except (TypeError, ValueError) as exc:
            raise StateLedgerCorruptionError("invalid session state") from exc

    def load_state(self, session_id: str) -> SessionState:
        session_id = self._validate_session_id(session_id)
        with self._lock:
            ledger = self._read_unlocked()
            entry = ledger["sessions"].get(session_id)
            if entry is None:
                return SessionState(session_id=session_id)
            if not isinstance(entry, dict):
                raise StateLedgerCorruptionError("session entry must be an object")
            return self._deserialize_state(session_id, entry.get("state"))

    def get_history(self, session_id: str) -> list[dict[str, Any]]:
        session_id = self._validate_session_id(session_id)
        with self._lock:
            ledger = self._read_unlocked()
            entry = ledger["sessions"].get(session_id)
            if entry is None:
                return []
            transitions = entry.get("transitions", [])
            if not isinstance(transitions, list) or not all(
                isinstance(item, dict) for item in transitions
            ):
                raise StateLedgerCorruptionError("session transitions must be a list of objects")
            return copy.deepcopy(transitions)

    def commit_transition(
        self,
        current_state: SessionState,
        score_delta: float,
        event_meta: dict[str, Any] | None = None,
    ) -> SessionState:
        if not isinstance(current_state, SessionState):
            raise TypeError("current_state must be a SessionState")
        session_id = self._validate_session_id(current_state.session_id)
        if (
            isinstance(current_state.turn_count, bool)
            or not isinstance(current_state.turn_count, int)
            or current_state.turn_count < 0
        ):
            raise ValueError("current_state.turn_count must be a non-negative integer")
        if (
            not isinstance(current_state.relationship_stage, str)
            or not current_state.relationship_stage
        ):
            raise ValueError("current_state.relationship_stage must be a non-empty string")
        if (
            not isinstance(current_state.attachment_style, str)
            or not current_state.attachment_style
        ):
            raise ValueError("current_state.attachment_style must be a non-empty string")
        delta = self._finite_float(score_delta, "score_delta")
        current_score = self._finite_float(current_state.fused_score, "fused_score")
        confidence = self._finite_float(current_state.confidence, "confidence")
        metadata = self._validate_metadata(
            event_meta if event_meta is not None else current_state.metadata
        )

        with self._lock:
            ledger = self._read_unlocked()
            existing_entry = ledger["sessions"].get(session_id)
            if existing_entry is None:
                persisted_turn = 0
                transitions: list[dict[str, Any]] = []
            else:
                if not isinstance(existing_entry, dict):
                    raise StateLedgerCorruptionError("session entry must be an object")
                persisted_state = self._deserialize_state(session_id, existing_entry.get("state"))
                persisted_turn = persisted_state.turn_count
                raw_transitions = existing_entry.get("transitions", [])
                if not isinstance(raw_transitions, list) or not all(
                    isinstance(item, dict) for item in raw_transitions
                ):
                    raise StateLedgerCorruptionError(
                        "session transitions must be a list of objects"
                    )
                transitions = copy.deepcopy(raw_transitions)

            if current_state.turn_count != persisted_turn:
                raise StateConflictError(
                    f"stale state for {session_id}: expected turn {persisted_turn}, "
                    f"got {current_state.turn_count}"
                )

            new_score = max(0.0, min(1.0, current_score + delta))
            new_stage = self._stage_for_score(new_score)
            timestamp = _utc_now()
            updated_state = SessionState(
                session_id=session_id,
                relationship_stage=new_stage,
                fused_score=round(new_score, 4),
                attachment_style=current_state.attachment_style,
                confidence=max(0.0, min(1.0, confidence)),
                turn_count=current_state.turn_count + 1,
                last_updated=timestamp,
                metadata=copy.deepcopy(metadata),
            )
            transitions.append(
                {
                    "transition_id": str(uuid.uuid4()),
                    "timestamp": timestamp,
                    "turn": updated_state.turn_count,
                    "previous_stage": current_state.relationship_stage,
                    "new_stage": new_stage,
                    "previous_fused_score": current_score,
                    "new_fused_score": updated_state.fused_score,
                    "score_delta": delta,
                    "metadata": copy.deepcopy(event_meta or {}),
                }
            )
            ledger["sessions"][session_id] = {
                "state": asdict(updated_state),
                "transitions": transitions[-self.history_limit :],
            }
            self._atomic_write_unlocked(ledger)
            return SessionState(**asdict(updated_state))

    def _atomic_write_unlocked(self, ledger: dict[str, Any]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        file_descriptor, temp_name = tempfile.mkstemp(
            dir=self.storage_path.parent,
            prefix=f".{self.storage_path.name}.",
            suffix=".tmp",
        )
        temp_path = Path(temp_name)
        try:
            with os.fdopen(file_descriptor, "w", encoding="utf-8") as handle:
                json.dump(ledger, handle, ensure_ascii=False, indent=2, allow_nan=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, self.storage_path)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise
