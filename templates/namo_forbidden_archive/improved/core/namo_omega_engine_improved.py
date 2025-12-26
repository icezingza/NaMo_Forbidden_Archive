"""
Enhanced NaMo Omega Engine with better error handling, caching, and async support.
"""

import logging
import asyncio
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
from functools import lru_cache
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntensityLevel(Enum):
    """Intensity levels for dialogue responses."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ArousalState:
    """Data class representing arousal state with proper validation."""

    level: float  # 0.0 to 1.0
    category: IntensityLevel
    confidence: float
    triggers: List[str]
    timestamp: datetime

    def __post_init__(self):
        """Validate arousal state values."""
        if not 0.0 <= self.level <= 1.0:
            raise ValueError(f"Arousal level must be 0.0-1.0, got {self.level}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")


@dataclass
class SystemStatus:
    """Data class for system status information."""

    arousal: str
    sin_status: str
    active_personas: List[str]
    engine_health: str
    response_time_ms: float


@dataclass
class EngineResponse:
    """Structured response from the engine."""

    text: str
    media_trigger: Optional[Dict[str, Any]] = None
    system_status: Optional[SystemStatus] = None
    error: Optional[str] = None


class SessionManager:
    """Manages user sessions with automatic cleanup."""

    def __init__(self, session_timeout_minutes: int = 60):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.logger = logging.getLogger(f"{__name__}.SessionManager")

    def create_session(self, session_id: str) -> Dict[str, Any]:
        """Create a new session with metadata."""
        session = {
            "created_at": datetime.now(),
            "last_active": datetime.now(),
            "message_count": 0,
            "arousal_history": [],
            "context": {},
        }
        self.sessions[session_id] = session
        self.logger.info(f"Created session: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get existing session, return None if expired."""
        if session_id not in self.sessions:
            return self.create_session(session_id)

        session = self.sessions[session_id]
        if self._is_expired(session):
            self.logger.info(f"Session expired: {session_id}, creating new one")
            del self.sessions[session_id]
            return self.create_session(session_id)

        session["last_active"] = datetime.now()
        return session

    def _is_expired(self, session: Dict[str, Any]) -> bool:
        """Check if session has expired."""
        return datetime.now() - session["last_active"] > self.session_timeout

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions, return count of removed sessions."""
        expired_ids = [sid for sid, session in self.sessions.items() if self._is_expired(session)]
        for sid in expired_ids:
            del self.sessions[sid]

        if expired_ids:
            self.logger.info(f"Cleaned up {len(expired_ids)} expired sessions")
        return len(expired_ids)


class ArousalDetectionMatrix:
    """Enhanced arousal detection with better algorithms and caching."""

    def __init__(self):
        self.base_intensity = 0.5
        self.adaptation_rate = 0.1
        self.logger = logging.getLogger(f"{__name__}.ArousalDetectionMatrix")
        self._detection_cache: Dict[str, tuple] = {}

    def detect_arousal(
        self,
        text_input: str,
        historical_patterns: Optional[List[float]] = None,
        use_cache: bool = True,
    ) -> ArousalState:
        """
        Detect arousal level with multi-dimensional analysis.

        Args:
            text_input: User text input
            historical_patterns: Previous arousal levels
            use_cache: Whether to use cached results

        Returns:
            ArousalState with detailed information
        """
        # Check cache
        cache_key = hash(text_input)
        if use_cache and cache_key in self._detection_cache:
            return self._detection_cache[cache_key][0]

        try:
            # Multi-dimensional arousal calculation
            textual_arousal = self._analyze_text_intensity(text_input)
            behavioral_arousal = self._analyze_interaction_patterns(text_input)

            # Temporal weighting
            temporal_weight = self._calculate_temporal_decay(historical_patterns)

            # Composite arousal score
            composite_arousal = (textual_arousal * 0.5 + behavioral_arousal * 0.5) * temporal_weight

            # Clamp to valid range
            composite_arousal = max(0.0, min(1.0, composite_arousal))

            # Categorize intensity
            category = self._categorize_intensity(composite_arousal)

            # Identify triggers
            triggers = self._identify_arousal_triggers(text_input)

            # Calculate confidence
            confidence = self._calculate_confidence(
                textual_arousal, behavioral_arousal, temporal_weight
            )

            arousal_state = ArousalState(
                level=composite_arousal,
                category=category,
                confidence=confidence,
                triggers=triggers,
                timestamp=datetime.now(),
            )

            # Cache result
            if use_cache:
                self._detection_cache[cache_key] = (arousal_state, time.time())

            self.logger.debug(
                f"Arousal detected: {composite_arousal:.2f} "
                f"({category.value}) - Confidence: {confidence:.2f}"
            )

            return arousal_state

        except Exception as e:
            self.logger.error(f"Error in arousal detection: {str(e)}", exc_info=True)
            # Return safe default
            return ArousalState(
                level=0.5,
                category=IntensityLevel.MEDIUM,
                confidence=0.0,
                triggers=[],
                timestamp=datetime.now(),
            )

    def _analyze_text_intensity(self, text: str) -> float:
        """Analyze textual intensity indicators."""
        try:
            # Keyword analysis
            intense_keywords = ["รุนแรง", "มากขึ้น", "เพิ่มเติม", "อีก"]
            keyword_count = sum(1 for kw in intense_keywords if kw.lower() in text.lower())

            # Text length factor
            text_length_factor = min(len(text) / 100.0, 1.0)

            # Exclamation marks
            exclamation_factor = min(text.count("!") * 0.1, 1.0)

            # Combined score
            score = (
                keyword_count * 0.2 + text_length_factor * 0.3 + exclamation_factor * 0.2
            ) / 0.7
            return min(score, 1.0)

        except Exception as e:
            self.logger.warning(f"Error analyzing text intensity: {str(e)}")
            return 0.5

    def _analyze_interaction_patterns(self, text: str) -> float:
        """Analyze interaction patterns."""
        try:
            # Pattern indicators
            patterns = {
                "repetition": len(text) > 0 and (text[0] * 3 in text),
                "question_mark": "?" in text,
                "continuation": "..." in text,
            }

            pattern_score = sum(patterns.values()) / len(patterns)
            return pattern_score

        except Exception as e:
            self.logger.warning(f"Error analyzing patterns: {str(e)}")
            return 0.5

    def _calculate_temporal_decay(self, historical_patterns: Optional[List[float]]) -> float:
        """Calculate temporal weighting with decay."""
        if not historical_patterns or len(historical_patterns) == 0:
            return 1.0

        # Recent patterns weighted more heavily
        decay_factor = 0.9
        weight = 0.0
        multiplier = 1.0

        for pattern in reversed(historical_patterns[-10:]):  # Last 10
            weight += pattern * multiplier
            multiplier *= decay_factor

        return min(
            weight / sum(decay_factor**i for i in range(len(historical_patterns[-10:]))), 1.0
        )

    def _categorize_intensity(self, arousal: float) -> IntensityLevel:
        """Categorize arousal level into intensity categories."""
        if arousal < 0.33:
            return IntensityLevel.LOW
        elif arousal < 0.67:
            return IntensityLevel.MEDIUM
        else:
            return IntensityLevel.HIGH

    def _identify_arousal_triggers(self, text: str) -> List[str]:
        """Identify specific triggers in the text."""
        triggers = []

        trigger_keywords = {
            "excitement": ["ตื่นเต้น", "หนูชอบ"],
            "passion": ["เร่าร้อน", "ปรารถนา"],
            "intensity": ["รุนแรง", "สูงสุด"],
        }

        for category, keywords in trigger_keywords.items():
            if any(kw.lower() in text.lower() for kw in keywords):
                triggers.append(category)

        return triggers

    def _calculate_confidence(
        self, textual_arousal: float, behavioral_arousal: float, temporal_weight: float
    ) -> float:
        """Calculate confidence of arousal detection."""
        # If sources agree, confidence is higher
        agreement = 1.0 - abs(textual_arousal - behavioral_arousal)
        confidence = (agreement + temporal_weight) / 2.0
        return max(0.0, min(1.0, confidence))

    def clear_cache(self):
        """Clear detection cache."""
        self._detection_cache.clear()
        self.logger.info("Detection cache cleared")


class DialogueBank:
    """Manages dialogue templates with efficient retrieval."""

    def __init__(self):
        self.dialogues: Dict[str, List[Dict[str, Any]]] = {"low": [], "medium": [], "high": []}
        self.logger = logging.getLogger(f"{__name__}.DialogueBank")
        self._load_default_dialogues()

    def _load_default_dialogues(self):
        """Load default dialogues for each intensity level."""
        self.dialogues["low"] = [
            {
                "id": "L001",
                "content": "ฉันรู้สึกถึงความปรารถนาอ่อนๆ ของคุณ...",
                "emotional_tone": "subtle",
                "moan_intensity": 0.2,
            }
        ]

        self.dialogues["medium"] = [
            {
                "id": "M001",
                "content": "ความร้อนเริ่มแผ่ซ่าน... คุณต้องการมากขึ้นใช่ไหม?",
                "emotional_tone": "teasing",
                "moan_intensity": 0.5,
            }
        ]

        self.dialogues["high"] = [
            {
                "id": "H001",
                "content": "ใช่... ปล่อยมันออกมา! ฉันรับรู้ถึงพลังงานอันรุนแรงนี้!",
                "emotional_tone": "intense",
                "moan_intensity": 0.9,
            }
        ]

    def get_dialogue(self, intensity: IntensityLevel) -> Optional[Dict[str, Any]]:
        """Get appropriate dialogue based on intensity."""
        try:
            intensity_key = intensity.value
            dialogues = self.dialogues.get(intensity_key, [])

            if not dialogues:
                self.logger.warning(f"No dialogues for intensity: {intensity_key}")
                return None

            # For now, return first dialogue (could add randomization)
            return dialogues[0]

        except Exception as e:
            self.logger.error(f"Error getting dialogue: {str(e)}")
            return None

    def add_dialogue(self, intensity: str, dialogue: Dict[str, Any]):
        """Add custom dialogue."""
        if intensity not in self.dialogues:
            self.logger.warning(f"Unknown intensity level: {intensity}")
            return

        self.dialogues[intensity].append(dialogue)
        self.logger.info(f"Added dialogue to {intensity} intensity")


class NaMoOmegaEngine:
    """Main NaMo Omega Engine with improved architecture."""

    def __init__(self, memory_service_url: Optional[str] = None):
        self.session_manager = SessionManager()
        self.arousal_detector = ArousalDetectionMatrix()
        self.dialogue_bank = DialogueBank()
        self.memory_service_url = memory_service_url or "http://localhost:8081"
        self.logger = logging.getLogger(__name__)
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        """Start background task for session cleanup."""

        def cleanup_loop():
            while True:
                try:
                    time.sleep(300)  # Every 5 minutes
                    self.session_manager.cleanup_expired_sessions()
                except Exception as e:
                    self.logger.error(f"Error in cleanup task: {str(e)}")

        import threading

        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()

    def process_input(
        self, input_text: str, session_id: str, use_cache: bool = True
    ) -> EngineResponse:
        """
        Process user input and generate response.

        Args:
            input_text: User message
            session_id: Session identifier
            use_cache: Use caching where applicable

        Returns:
            EngineResponse with generated content
        """
        start_time = time.time()

        try:
            # Input validation
            if not isinstance(input_text, str) or not input_text.strip():
                return EngineResponse(text="", error="Invalid input: message cannot be empty")

            if len(input_text) > 5000:
                return EngineResponse(text="", error="Input too long: maximum 5000 characters")

            # Get or create session
            session = self.session_manager.get_session(session_id)
            if not session:
                return EngineResponse(text="", error="Failed to create session")

            # Detect arousal
            historical_arousal = session.get("arousal_history", [])
            arousal_state = self.arousal_detector.detect_arousal(
                input_text, historical_arousal, use_cache=use_cache
            )

            # Update session
            session["message_count"] += 1
            session["arousal_history"].append(arousal_state.level)
            session["arousal_history"] = session["arousal_history"][-100:]  # Keep last 100

            # Get appropriate dialogue
            dialogue = self.dialogue_bank.get_dialogue(arousal_state.category)

            if not dialogue:
                return EngineResponse(
                    text="เกิดข้อผิดพลาด: ไม่สามารถสร้างการตอบสนองได้", error="No dialogue available"
                )

            # Generate response text
            response_text = self._generate_response(dialogue, arousal_state)

            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000

            # Create system status
            system_status = SystemStatus(
                arousal=f"{arousal_state.level * 100:.0f}%",
                sin_status=f"[Session {session['message_count']}] Activity Level: High",
                active_personas=["NaMo"],
                engine_health="OK",
                response_time_ms=response_time_ms,
            )

            self.logger.info(
                f"Processed input for session {session_id} in {response_time_ms:.2f}ms"
            )

            return EngineResponse(text=response_text, system_status=system_status)

        except Exception as e:
            self.logger.error(f"Error processing input: {str(e)}", exc_info=True)
            response_time_ms = (time.time() - start_time) * 1000

            return EngineResponse(text="", error=f"Processing error: {str(e)}")

    def _generate_response(self, dialogue: Dict[str, Any], arousal_state: ArousalState) -> str:
        """Generate response from dialogue template."""
        try:
            base_response = dialogue.get("content", "")

            # Could add more complex response generation here
            # For now, return base response
            return f"NaMo: {base_response}"

        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return "NaMo: เสียใจค่ะ เกิดข้อผิดพลาด"

    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a session."""
        session = self.session_manager.sessions.get(session_id)

        if not session:
            return None

        return {
            "session_id": session_id,
            "created_at": session["created_at"].isoformat(),
            "last_active": session["last_active"].isoformat(),
            "message_count": session["message_count"],
            "average_arousal": (
                sum(session.get("arousal_history", [])) / len(session.get("arousal_history", [1]))
            ),
            "arousal_history": session.get("arousal_history", [])[-20:],  # Last 20
        }
