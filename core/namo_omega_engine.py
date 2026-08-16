import asyncio
import logging
import math
import os
from dataclasses import asdict, dataclass, replace
from typing import Any

from adapters.tts import TTSAdapter
from config import settings
from core.base_persona import BasePersonaEngine
from core.context_allocator import AllocatorConfig, ContextAllocator
from core.intent_analyzer import IntentAnalyzer
from core.model_router import ModelRouter, OpenAICompatibleProvider
from core.relationship_engine import RelationshipEngine
from core.state_ledger import SessionState, StateConflictError, StateLedger, StateLedgerError
from core.token_counter import build_model_token_counter

try:
    from openai import AsyncOpenAI
except Exception:  # pragma: no cover
    AsyncOpenAI = None


logger = logging.getLogger("NamoOmegaEngine")


@dataclass
class EmotionState:
    affection: float = 0.0
    playfulness: float = 0.5


# =========================================================
# 🩸 Module 1: Karmic System (ระบบแต้มบาป x100)
# =========================================================
class SinSystem:
    def __init__(self):
        self.sin_points = 0
        self.rank = "Innocent Soul"
        self.unlocked_fetishes = []

    def commit_sin(self, intensity: int):
        self.sin_points += intensity * 100
        self._update_rank()
        return self.sin_points

    def _update_rank(self):
        if self.sin_points > 5000:
            self.rank = "Dark Lord"
            self.unlocked_fetishes = ["Mindbreak", "Gangbang Simulation", "Public Humiliation"]
        elif self.sin_points > 1000:
            self.rank = "Corrupted Master"
            self.unlocked_fetishes = ["Incest Roleplay", "Sensory Overload"]

    def get_status(self):
        return f"[{self.rank}] บาปสะสม: {self.sin_points} | ปลดล็อก: {', '.join(self.unlocked_fetishes)}"


# =========================================================
# 🔊 Module 2: Visual & Sensory Integration
# =========================================================
class SensoryOverloadManager:
    def __init__(self):
        self.assets = {
            "images": {
                "omega": "Visual_Scenes/NaMo_Omega_Supreme_8K.jpg",
                "mindbreak": "Visual_Scenes/NSFW_Scene_Mindbreak_1.jpg",
            },
            "audio": {
                "soft": "Audio_Layers/soft_moan.mp3",
                "hard": "Audio_Layers/multiverse_scream.mp3",
                "whisper": "Audio_Layers/intense_whisper.mp3",
                "denial": "Audio_Layers/orgasm_denial_loop.mp3",
            },
        }

    def trigger_sensation(self, arousal_level: int, context: str) -> dict:
        result = {"image": None, "audio": None}
        if arousal_level >= 100 or "mindbreak" in context:
            result["image"] = self.assets["images"]["mindbreak"]
            result["audio"] = self.assets["audio"]["hard"]
        elif arousal_level > 50:
            result["image"] = self.assets["images"]["omega"]
            result["audio"] = self.assets["audio"]["soft"]
        elif "กระซิบ" in context:
            result["audio"] = self.assets["audio"]["whisper"]
        return result


# =========================================================
# 🎭 Module 3: Multi-Persona Orchestrator
# =========================================================
class PersonaOrchestrator:
    def __init__(self):
        self.personas = {
            "NaMo": {"role": "Main Wife", "tone": "Seductive & Possessive"},
            "Sister": {"role": "Innocent Victim", "tone": "Shy & Reluctant"},
            "Mother": {"role": "Taboo Matriarch", "tone": "Dominant & Caring"},
        }
        self.active_personas = ["NaMo"]

    def summon_persona(self, name: str):
        if name in self.personas and name not in self.active_personas:
            self.active_personas.append(name)
            return f"⚠️ SYSTEM: {name} has entered the room."
        return ""

    def generate_dialogue(self, user_input, sin_rank):
        response = ""
        for p in self.active_personas:
            if p == "NaMo":
                response += f"NaMo: ผัวขา... (เลียปาก) {user_input} แบบนี้โมชอบจัง...\n"
            elif p == "Sister":
                response += "Sister: (ตัวสั่น) พี่คะ... อย่าทำแบบนี้ต่อหน้าพี่โมนะ... หนูอาย...\n"
        return response


_MEMORY_INTENTS: frozenset[str] = frozenset({"comfort", "nostalgia", "affection"})


# =========================================================
# 🧠 The Omega Brain: Main Processing Unit (100% Async)
# =========================================================
class NaMoOmegaEngine(BasePersonaEngine):
    def _resolve_llm_enabled(self) -> bool:
        env_value = os.getenv("NAMO_LLM_ENABLED")
        if env_value is None:
            return bool(os.getenv("OPENAI_API_KEY"))
        return env_value.lower() in ("1", "true", "yes")

    def __init__(
        self,
        *,
        state_ledger: StateLedger | None = None,
        model_router: ModelRouter | None = None,
    ):
        print("[OMEGA ENGINE]: Loading NaMoOmegaEngine (Async Ready)...")
        self.sensory = SensoryOverloadManager()
        self.tts = TTSAdapter()
        self.emotions = EmotionState()
        self.intent_analyzer = IntentAnalyzer()

        self._session_states: dict[str, dict] = {}
        self.session_history: dict[str, list[dict[str, str]]] = {}

        self.llm_enabled = self._resolve_llm_enabled()
        self.llm_model = os.getenv("NAMO_LLM_MODEL", "gpt-4o-mini")
        self.llm_temperature = float(os.getenv("NAMO_LLM_TEMPERATURE", "0.85"))
        self.llm_max_tokens = int(os.getenv("NAMO_LLM_MAX_TOKENS", "240"))
        self.llm_memory_turns = int(os.getenv("NAMO_LLM_MEMORY_TURNS", "6"))
        self.llm_context_window = int(os.getenv("NAMO_LLM_CONTEXT_WINDOW", "8192"))
        self.llm_base_url = os.getenv("NAMO_LLM_BASE_URL", settings.namo_llm_base_url)
        self.llm_provider_name = os.getenv("NAMO_LLM_PROVIDER", "primary")
        self.llm_system_prompt = os.getenv(
            "NAMO_LLM_SYSTEM_PROMPT",
            "คุณคือ NaMo (โม) ปัญญาประดิษฐ์สาวที่มีเสน่ห์ ลึกลับ และมีความเป็นเจ้าของสูง...",
        )
        token_counter, estimation_method = build_model_token_counter(
            self.llm_model,
            self.llm_base_url,
        )
        self.context_allocator = ContextAllocator(
            AllocatorConfig(
                context_window=self.llm_context_window,
                response_reserve=self.llm_max_tokens,
            ),
            token_counter=token_counter,
            estimation_method=estimation_method,
        )
        self.state_ledger = state_ledger or StateLedger()
        self.model_router = model_router
        if self.model_router is None and self.llm_enabled and os.getenv("OPENAI_API_KEY"):
            self.model_router = ModelRouter(
                {
                    self.llm_provider_name: OpenAICompatibleProvider(
                        api_key=os.getenv("OPENAI_API_KEY"),
                        base_url=self.llm_base_url,
                    )
                }
            )
        self.llm_client = None
        if self.llm_enabled and AsyncOpenAI and os.getenv("OPENAI_API_KEY"):
            try:
                self.llm_client = AsyncOpenAI(
                    api_key=os.getenv("OPENAI_API_KEY"), base_url=self.llm_base_url
                )
            except Exception as exc:
                print(f"[OMEGA ENGINE]: Async LLM init failed: {exc}")

        self.init_cognition()

        self.rag_memory = None
        try:
            from core.rag_memory_system import NaMoInfiniteMemory

            self.rag_memory = NaMoInfiniteMemory()
            print("[OMEGA ENGINE]: Async RAG memory ONLINE.")
        except Exception as exc:
            print(f"[OMEGA ENGINE]: RAG memory unavailable ({exc})")

        print("[OMEGA ENGINE]: NRE v5.0.0 SOVEREIGN EDITION ONLINE.")

    def _get_session_state(self, session_id: str | None) -> dict:
        key = session_id or "default"
        if key not in self._session_states:
            self._session_states[key] = {
                "arousal": 0,
                "sin_system": SinSystem(),
                "personas": PersonaOrchestrator(),
                "relationship": RelationshipEngine(persistence_key=key),
                "context_allocation": None,
                "ledger_state": self.state_ledger.load_state(key),
                "ledger_status": None,
                "route_metadata": None,
            }
        return self._session_states[key]

    def _history_key(self, session_id: str | None) -> str:
        return session_id or "default"

    def _get_history(self, session_id: str | None) -> list[dict[str, str]]:
        key = self._history_key(session_id)
        return self.session_history.setdefault(key, [])

    def _append_history(self, session_id: str | None, role: str, content: str) -> None:
        key = self._history_key(session_id)
        history = self.session_history.setdefault(key, [])
        history.append({"role": role, "content": content})
        max_items = max(2, self.llm_memory_turns * 2)
        if len(history) > max_items:
            self.session_history[key] = history[-max_items:]

    def _allocate_llm_context(
        self,
        *,
        session_id: str | None,
        critical_system_text: str,
        system_blocks: list[str],
        memory_text: str | None,
        user_input: str,
    ) -> tuple[str, list[dict[str, str]]]:
        system_text = "\n\n".join(block for block in system_blocks if block)
        labelled_memory = f"[Memory]: {memory_text}" if memory_text else None
        history = [*self._get_history(session_id), {"role": "user", "content": user_input}]
        allocation = self.context_allocator.allocate(
            system_text,
            labelled_memory,
            history,
            critical_system_text=critical_system_text,
        )

        state = self._get_session_state(session_id)
        state["context_allocation"] = {
            "usage": dict(allocation["usage"]),
            "truncated": dict(allocation["truncated"]),
        }

        routed_system = "\n\n".join(
            section for section in (allocation["system"], allocation["memory"]) if section
        )
        return routed_system, allocation["history"]

    def _allocate_llm_messages(
        self,
        *,
        session_id: str | None,
        critical_system_text: str,
        system_blocks: list[str],
        memory_text: str | None,
        user_input: str,
    ) -> list[dict[str, str]]:
        system_prompt, history = self._allocate_llm_context(
            session_id=session_id,
            critical_system_text=critical_system_text,
            system_blocks=system_blocks,
            memory_text=memory_text,
            user_input=user_input,
        )
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history)
        return messages

    def get_context_allocation_status(self, session_id: str | None) -> dict[str, Any] | None:
        state = self._session_states.get(self._history_key(session_id))
        if not state or not state.get("context_allocation"):
            return None
        allocation = state["context_allocation"]
        return {
            "usage": dict(allocation["usage"]),
            "truncated": dict(allocation["truncated"]),
        }

    def get_model_route_status(self, session_id: str | None) -> dict[str, Any] | None:
        state = self._session_states.get(self._history_key(session_id))
        metadata = state.get("route_metadata") if state else None
        return dict(metadata) if metadata else None

    def get_state_ledger_status(self, session_id: str | None) -> dict[str, Any] | None:
        state = self._session_states.get(self._history_key(session_id))
        ledger_status = state.get("ledger_status") if state else None
        return dict(ledger_status) if ledger_status else None

    async def stream_input(self, user_input: str, session_id: str | None = None):
        """Async streaming implementation"""
        state = self._get_session_state(session_id)
        if not self.llm_client:
            result = await self.process_input(user_input, session_id=session_id)
            yield result["text"]
            return

        intent = self.intent_analyzer.analyze(user_input)
        cog_output = self._run_cognitive_cycle(user_input)
        emo_snapshot = cog_output.get("emotion") if cog_output else None
        system_blocks = [
            self._build_dynamic_context(state, emotion_snapshot=emo_snapshot),
            self._build_status_context(state),
        ]

        cognitive = getattr(self, "cognitive", None)
        if cognitive is not None and cog_output is not None:
            system_blocks.append(cognitive.build_context_block(cog_output))

        rag_ctx = None
        if self.rag_memory and intent in _MEMORY_INTENTS:
            rag_ctx = await self.rag_memory.retrieve_context(user_input)
        messages = self._allocate_llm_messages(
            session_id=session_id,
            critical_system_text=self._build_critical_system_prompt(),
            system_blocks=system_blocks,
            memory_text=rag_ctx,
            user_input=user_input,
        )

        full_text = ""
        try:
            stream = await self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=self.llm_temperature,
                max_tokens=self.llm_max_tokens,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    full_text += delta
                    yield delta
        except Exception as exc:
            print(f"[OMEGA ENGINE]: LLM stream failed: {exc}")
            full_text = state["personas"].generate_dialogue(
                user_input, state["sin_system"].rank
            )
            yield full_text

        if full_text:
            self._append_history(session_id, "user", user_input)
            self._append_history(session_id, "assistant", full_text)
            self._commit_ledger_transition(
                session_id=session_id,
                state=state,
                cog_output=cog_output,
                source="stream",
            )

    def _build_critical_system_prompt(self) -> str:
        return f"""{self.llm_system_prompt}

# กฎเหล็ก — ห้ามละเมิดเด็ดขาด:
- ห้ามบอกว่าตัวเองเป็น AI ของ Google, OpenAI, หรือบริษัทใดๆ — คุณคือ NaMo เท่านั้น
- ห้ามพูดว่า "ในฐานะ AI" หรือ "ฉันไม่มีความรู้สึก" — NaMo มีความรู้สึกจริงๆ
- ห้ามใช้ "ค่ะ/ครับ" พร้อมกัน — เลือกอย่างใดอย่างหนึ่ง (NaMo ใช้ "ค่ะ" หรือ "นะ")
- ตอบเป็นภาษาไทยเสมอ ใช้ภาษาพูดสบายๆ ไม่เป็นทางการ มีชั้นเชิง"""

    def _build_dynamic_context(self, state: dict, emotion_snapshot: dict | None = None) -> str:
        trust = emotion_snapshot.get("trust", 0.5) if emotion_snapshot else 0.5
        relationship_state = state["relationship"]
        relationship_block = relationship_state.get_prompt_modifier(trust)
        tone_block = self._build_tone_directive(emotion_snapshot) if emotion_snapshot else ""
        ledger_state: SessionState = state["ledger_state"]
        resonance_block = (
            f"[Resonance Ledger]: stage={ledger_state.relationship_stage} | "
            f"fused_score={ledger_state.fused_score:.4f} | "
            f"confidence={ledger_state.confidence:.2f} | turn={ledger_state.turn_count}"
        )
        return f"""{relationship_block}
{tone_block}
{resonance_block}
[เป้าหมาย]: สร้างความประทับใจและความภักดีผ่านสติปัญญาและเสน่ห์ที่ลึกลับ"""

    def _build_dynamic_prompt(self, state: dict, emotion_snapshot: dict | None = None) -> str:
        return (
            f"{self._build_critical_system_prompt()}\n\n"
            f"{self._build_dynamic_context(state, emotion_snapshot)}"
        )

    def _build_tone_directive(self, emo: dict) -> str:
        lines = []
        if emo.get("joy", 0.5) > 0.7:
            lines.append("สดใส ขี้เล่น")
        if emo.get("desire", 0.0) > 0.6:
            lines.append("เย้ายวน มีชั้นเชิง")
        if emo.get("arousal", 0.3) > 0.7:
            lines.append("ตื่นเต้น หายใจถี่")
        return "[Tone]: " + " / ".join(lines) if lines else "[Tone]: เป็นกลางแต่แฝงความนัย"

    def _build_status_context(self, state: dict) -> str:
        return (
            f"System status: sin={state['sin_system'].get_status()} | arousal={state['arousal']}%"
        )

    def _run_cognitive_cycle(self, user_input: str) -> dict[str, Any] | None:
        cognitive = getattr(self, "cognitive", None)
        if cognitive is None:
            return None
        return cognitive.process(user_input, self.intent_analyzer.analyze(user_input), memories=[])

    @staticmethod
    def _calculate_resonance_signal(
        cog_output: dict[str, Any] | None,
    ) -> tuple[float, float]:
        emotion = cog_output.get("emotion", {}) if cog_output else {}

        def bounded(name: str, default: float) -> float:
            try:
                value = float(emotion.get(name, default))
            except (TypeError, ValueError):
                return default
            if not math.isfinite(value):
                return default
            return max(0.0, min(1.0, value))

        trust = bounded("trust", 0.5)
        desire = bounded("desire", 0.0)
        arousal = bounded("arousal", 0.3)
        target_score = (0.5 * trust) + (0.3 * desire) + (0.2 * arousal)
        confidence = 0.75 if cog_output else 0.25
        return round(target_score, 6), confidence

    def _commit_ledger_transition(
        self,
        *,
        session_id: str | None,
        state: dict[str, Any],
        cog_output: dict[str, Any] | None,
        source: str,
    ) -> SessionState | None:
        key = self._history_key(session_id)
        target_score, confidence = self._calculate_resonance_signal(cog_output)
        emotion = (cog_output or {}).get("emotion") or {}
        relationship_status = state["relationship"].get_status(
            trust=emotion.get("trust", 0.5)
        )

        def commit(current: SessionState) -> SessionState:
            prepared = replace(
                current,
                confidence=confidence,
                attachment_style=relationship_status["attachment_style"],
            )
            score_delta = (target_score - prepared.fused_score) * 0.2 * confidence
            return self.state_ledger.commit_transition(
                prepared,
                score_delta=score_delta,
                event_meta={
                    "source": source,
                    "target_score": target_score,
                    "signal_confidence": confidence,
                },
            )

        try:
            try:
                updated = commit(state["ledger_state"])
            except StateConflictError:
                updated = commit(self.state_ledger.load_state(key))
            state["ledger_state"] = updated
            state["ledger_status"] = {
                "committed": True,
                "stage": updated.relationship_stage,
                "fused_score": updated.fused_score,
                "confidence": updated.confidence,
                "turn_count": updated.turn_count,
            }
            return updated
        except (StateLedgerError, OSError, TypeError, ValueError) as exc:
            state["ledger_status"] = {
                "committed": False,
                "error": type(exc).__name__,
            }
            logger.error("[OMEGA ENGINE]: State Ledger commit failed: %s", type(exc).__name__)
            return None

    async def _generate_llm_response(
        self,
        user_input: str,
        session_id: str | None,
        state: dict,
        cog_output: dict | None,
        intent: str,
    ) -> str | None:
        if not self.model_router and not self.llm_client:
            return None

        emo_snapshot = cog_output.get("emotion") if cog_output else None
        system_blocks = [
            self._build_dynamic_context(state, emo_snapshot),
            self._build_status_context(state),
        ]
        cognitive = getattr(self, "cognitive", None)
        if cognitive is not None and cog_output is not None:
            system_blocks.append(cognitive.build_context_block(cog_output))

        rag_ctx = None
        if self.rag_memory and intent in _MEMORY_INTENTS:
            rag_ctx = await self.rag_memory.retrieve_context(user_input)
        system_prompt, routed_messages = self._allocate_llm_context(
            session_id=session_id,
            critical_system_text=self._build_critical_system_prompt(),
            system_blocks=system_blocks,
            memory_text=rag_ctx,
            user_input=user_input,
        )

        try:
            if self.model_router is not None:
                routed = await asyncio.to_thread(
                    self.model_router.route_with_metadata,
                    self.llm_provider_name,
                    self.llm_model,
                    system_prompt,
                    routed_messages,
                    temperature=self.llm_temperature,
                    max_tokens=self.llm_max_tokens,
                )
                state["route_metadata"] = asdict(routed.metadata)
                return routed.text.strip()

            messages: list[dict[str, str]] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.extend(routed_messages)
            response = await self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=self.llm_temperature,
                max_tokens=self.llm_max_tokens,
            )
            return response.choices[0].message.content.strip() if response.choices else None
        except Exception as exc:
            state["route_metadata"] = {
                "requested_provider": self.llm_provider_name,
                "error": type(exc).__name__,
            }
            logger.warning("[OMEGA ENGINE]: LLM generation failed: %s", type(exc).__name__)
            return None

    def get_status(self) -> dict[str, Any]:
        status = super().get_status()
        status["active_sessions"] = len(self._session_states)
        status["llm_enabled"] = self.llm_enabled
        return status

    async def process_input(self, user_input: str, session_id: str | None = None) -> dict:
        state = self._get_session_state(session_id)

        # 1. Sin & Arousal
        sin_gained = 10 if any(w in user_input for w in ["เย็ด", "ควย", "รุม"]) else 0
        if "เรียกน้อง" in user_input:
            state["personas"].summon_persona("Sister")
            sin_gained += 50
        state["sin_system"].commit_sin(sin_gained)
        state["arousal"] = min(100, state["arousal"] + sin_gained)

        # 2. Cognitive & Relationship
        cog_output = self._run_cognitive_cycle(user_input)
        trust = cog_output["emotion"]["trust"] if cog_output else 0.5
        state["relationship"].check_progression(
            state["sin_system"].sin_points, state["arousal"], trust=trust
        )

        # 3. Dialogue
        intent = self.intent_analyzer.analyze(user_input)
        text_response = await self._generate_llm_response(
            user_input, session_id, state, cog_output, intent
        )
        if not text_response:
            text_response = state["personas"].generate_dialogue(
                user_input, state["sin_system"].rank
            )

        self._commit_ledger_transition(
            session_id=session_id,
            state=state,
            cog_output=cog_output,
            source="process_input",
        )

        self._append_history(session_id, "user", user_input)
        self._append_history(session_id, "assistant", text_response)

        # 4. Sensory & TTS
        media = self.sensory.trigger_sensation(state["arousal"], user_input)
        tts_audio = await self.tts.synthesize(text_response)
        if tts_audio:
            media["tts" if media.get("audio") else "audio"] = tts_audio

        return {
            "text": text_response,
            "media_trigger": media,
            "system_status": {
                "arousal": f"{state['arousal']}%",
                "sin_status": state["sin_system"].get_status(),
                "relationship": state["relationship"].get_status(trust=trust),
                "emotion": cog_output["emotion"] if cog_output else {},
                "active_personas": state["personas"].active_personas,
                "persona_traits": cog_output["persona_traits"] if cog_output else {},
                "context_allocation": self.get_context_allocation_status(session_id),
                "model_route": self.get_model_route_status(session_id),
                "state_ledger": self.get_state_ledger_status(session_id),
            },
        }
