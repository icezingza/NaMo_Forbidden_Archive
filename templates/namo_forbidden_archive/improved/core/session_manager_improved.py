"""
Thread-safe session management with locking.
"""

import threading
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class SessionData:
    """Thread-safe session data."""

    created_at: datetime
    last_active: datetime
    message_count: int = 0
    arousal_history: list = field(default_factory=list)
    context: dict = field(default_factory=dict)
    lock: threading.RLock = field(default_factory=threading.RLock)


class ThreadSafeSessionManager:
    """
    Thread-safe session manager with RLock protection.
    """

    def __init__(self, session_timeout_minutes: int = 60):
        self.sessions: Dict[str, SessionData] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.global_lock = threading.RLock()
        self.logger = logging.getLogger(f"{__name__}.ThreadSafeSessionManager")

    def create_session(self, session_id: str) -> SessionData:
        """
        Create a new session (thread-safe).

        Args:
            session_id: Unique session identifier

        Returns:
            New SessionData
        """
        with self.global_lock:
            if session_id in self.sessions:
                self.logger.warning(f"Session already exists: {session_id}")
                return self.sessions[session_id]

            session = SessionData(created_at=datetime.now(), last_active=datetime.now())

            self.sessions[session_id] = session
            self.logger.info(f"Created session: {session_id}")

            return session

    def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Get existing session (thread-safe).

        Args:
            session_id: Session identifier

        Returns:
            SessionData if exists, None otherwise
        """
        with self.global_lock:
            if session_id not in self.sessions:
                return self.create_session(session_id)

            session = self.sessions[session_id]

            # Check if expired
            if self._is_expired(session):
                self.logger.info(f"Session expired: {session_id}")
                del self.sessions[session_id]
                return self.create_session(session_id)

            # Update last active
            session.last_active = datetime.now()

            return session

    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update session data (thread-safe).

        Args:
            session_id: Session identifier
            data: Data to update

        Returns:
            True if successful, False otherwise
        """
        with self.global_lock:
            if session_id not in self.sessions:
                self.logger.warning(f"Session not found: {session_id}")
                return False

            session = self.sessions[session_id]

            with session.lock:
                for key, value in data.items():
                    if hasattr(session, key):
                        setattr(session, key, value)

                session.last_active = datetime.now()

            return True

    def add_arousal_entry(self, session_id: str, arousal: float):
        """
        Add arousal entry to session (thread-safe).

        Args:
            session_id: Session identifier
            arousal: Arousal level to add
        """
        with self.global_lock:
            if session_id not in self.sessions:
                self.logger.warning(f"Session not found: {session_id}")
                return

            session = self.sessions[session_id]

            with session.lock:
                session.arousal_history.append(arousal)
                # Keep only last 100
                session.arousal_history = session.arousal_history[-100:]
                session.message_count += 1

    def increment_message_count(self, session_id: str):
        """
        Increment message count (thread-safe).

        Args:
            session_id: Session identifier
        """
        with self.global_lock:
            if session_id not in self.sessions:
                return

            session = self.sessions[session_id]
            with session.lock:
                session.message_count += 1

    def _is_expired(self, session: SessionData) -> bool:
        """Check if session has expired."""
        return datetime.now() - session.last_active > self.session_timeout

    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions (thread-safe).

        Returns:
            Number of sessions removed
        """
        with self.global_lock:
            expired_ids = [
                sid for sid, session in self.sessions.items() if self._is_expired(session)
            ]

            for sid in expired_ids:
                del self.sessions[sid]

            if expired_ids:
                self.logger.info(f"Cleaned up {len(expired_ids)} expired sessions")

            return len(expired_ids)

    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all sessions info (thread-safe).

        Returns:
            Dictionary of all sessions
        """
        with self.global_lock:
            result = {}
            for sid, session in self.sessions.items():
                with session.lock:
                    result[sid] = {
                        "created_at": session.created_at.isoformat(),
                        "last_active": session.last_active.isoformat(),
                        "message_count": session.message_count,
                        "arousal_avg": (
                            sum(session.arousal_history) / len(session.arousal_history)
                            if session.arousal_history
                            else 0
                        ),
                    }
            return result

    def get_session_count(self) -> int:
        """Get active session count (thread-safe)."""
        with self.global_lock:
            return len(self.sessions)
