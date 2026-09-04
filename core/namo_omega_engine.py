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
from core.narrative_safety import NarrativeSafetyDecision, NarrativeSafetyGate
from core.relationship_engine import RelationshipEngine
from core.slowburn_lorebook import SlowBurnLorebook
from core.roleplay.composite_lorebook import CompositeRoleplayLorebook
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
            self.unlocked_fetishes = ["Intense Pacing", "Multi-Character Scene", "Roleplay"]
        elif self.sin_points > 1000:
            self.rank = "Corrupted Master"
            self.unlocked_fetishes = ["Slow-Burn Roleplay", "Sensory Detail"]

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
                "intense": "Visual_Scenes/NaMo_Omega_Supreme_8K.jpg",
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
        if arousal_level >= 100 or "intense scene" in context.casefold():
            result["image"] = self.assets["images"]["intense"]
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
            "Muse": {"role": "Adult Collaborator", "tone": "Reserved & Self-Assured"},
            "Guardian": {"role": "Adult Boundary Keeper", "tone": "Direct & Caring"},
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
                response += (
                    f"NaMo: โมได้ยินว่า '{user_input}' เราค่อยๆ วางจังหวะและขอบเขตให้ชัดก่อนนะ\n"
                )
            elif p == "Muse":
                response += "Muse: ฉันพร้อมร่วมฉากเมื่อทุกคนยืนยันขอบเขตตรงกันแล้ว\n"
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
        self.lorebook = SlowBurnLorebook()
        from core.roleplay.fullport_v2_lorebook import FullPortV2Lorebook
        fullport_lorebook = FullPortV2Lorebook(
            mode=os.getenv("NAMO_ROLEPLAY_MODE", "compact"),
            max_matches=int(os.getenv("NAMO_ROLEPLAY_MAX_MATCHES", "2")),
            max_context_chars=int(os.getenv("NAMO_ROLEPLAY_MAX_CONTEXT_CHARS", "8000"))
        )
        self.lorebook = CompositeRoleplayLorebook(
            self.lorebook,
            fullport=fullport_lorebook,
        )
        self.narrative_safety = NarrativeSafetyGate()

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
            ledger_state = self.state_ledger.load_state(key)
            self._session_states[key] = {
                "arousal": 0,
                "sin_system": SinSystem(),
                "personas": PersonaOrchestrator(),
                "relationship": RelationshipEngine(persistence_key=key),
                "context_allocation": None,
                "ledger_state": ledger_state,
                "ledger_status": None,
                "route_metadata": None,
                "current_beat": ledger_state.metadata.get("current_beat", "tease"),
                "boundary_state": ledger_state.metadata.get("boundary_state", "clear"),
                "tension_meter": ledger_state.metadata.get("tension_meter", 0.0),
                "narrative_safety": None,
                "narrative_directive": None,
            }
        return self._session_states[key]

    def _evaluate_narrative_safety(
        self, user_input: str, state: dict[str, Any]
    ) -> NarrativeSafetyDecision:
        decision = self.narrative_safety.evaluate(
            user_input,
            current_beat=str(state.get("current_beat", "tease")),
            tension_meter=float(state.get("tension_meter", 0.0)),
        )
        state["current_beat"] = decision.beat.value
        state["boundary_state"] = decision.boundary_state.value
        state["tension_meter"] = decision.tension_meter
        state["narrative_safety"] = decision.status()
        state["narrative_directive"] = decision.directive
        return decision

    @staticmethod
    def _blocked_response(decision: NarrativeSafetyDecision) -> dict[str, Any]:
        return {
            "text": decision.response,
            "media_trigger": {"image": None, "audio": None},
            "system_status": {
                "arousal": "0%",
                "context_allocation": None,
                "model_route": None,
                "state_ledger": {"committed": False, "reason": "SAFETY_BLOCK"},
                "narrative_safety": decision.status(),
            },
        }

    def _commit_safety_transition(
        self, session_id: str | None, state: dict[str, Any], decision: NarrativeSafetyDecision
    ) -> None:
        key = self._history_key(session_id)
        event_meta = {
            "source": "narrative_safety",
            "current_beat": decision.beat.value,
            "boundary_state": decision.boundary_state.value,
            "tension_meter": decision.tension_meter,
            "last_transition_reason": decision.reason_code,
        }
        try:
            try:
                updated = self.state_ledger.commit_transition(
                    state["ledger_state"], score_delta=0.0, event_meta=event_meta
                )
            except StateConflictError:
                updated = self.state_ledger.commit_transition(
                    self.state_ledger.load_state(key), score_delta=0.0, event_meta=event_meta
                )
            state["ledger_state"] = updated
            state["ledger_status"] = {
                "committed": True,
                "stage": updated.relationship_stage,
                "fused_score": updated.fused_score,
                "confidence": updated.confidence,
                "turn_count": updated.turn_count,
            }
        except (StateLedgerError, OSError, TypeError, ValueError) as exc:
            state["ledger_status"] = {"committed": False, "error": type(exc).__name__}
            logger.error("[OMEGA ENGINE]: Safety state commit failed: %s", type(exc).__name__)

    def _boundary_response(
        self, session_id: str | None, state: dict[str, Any], decision: NarrativeSafetyDecision
    ) -> dict[str, Any]:
        self._commit_safety_transition(session_id, state, decision)
        return {
            "text": decision.response,
            "media_trigger": {"image": None, "audio": None},
            "system_status": {
                "arousal": f"{decision.tension_meter}%",
                "context_allocation": None,
                "model_route": None,
                "state_ledger": self.get_state_ledger_status(session_id),
                "narrative_safety": decision.status(),
            },
        }

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
        routed_system = self._substitute_prompt_variables(routed_system, state)
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

    @staticmethod
    def _render_lorebook_items(items: list[dict[str, Any]], placement: str) -> str:
        if not items:
            return ""
        body = "\n".join(
            f"- [{item['source_lorebook']} | {item['comment'] or item['entry_id']}] "
            f"{item['content']}"
            for item in items
        )
        return f"[LOREBOOK PLACEMENT: {placement.upper()}]\n{body}"

    def _apply_lorebook_message_placements(
        self,
        messages: list[dict[str, str]],
        plan: dict[str, list[dict[str, Any]]],
    ) -> list[dict[str, str]]:
        """Place non-system lorebook sections without mutating allocated history."""
        positioned = [dict(message) for message in messages]
        current_user_index = len(positioned) - 1

        for placement in ("author_note_pre", "author_note_post"):
            content = self._render_lorebook_items(plan.get(placement, []), placement)
            if content:
                positioned.insert(
                    current_user_index,
                    {"role": "developer", "content": content},
                )
                current_user_index += 1

        for item in plan.get("history_depth", []):
            try:
                depth = max(0, int(item.get("depth", 4)))
            except (TypeError, ValueError):
                depth = 4
            insert_at = max(0, current_user_index - depth)
            content = self._render_lorebook_items([item], "history_depth")
            positioned.insert(insert_at, {"role": "developer", "content": content})
            current_user_index += 1

        return positioned

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

        safety_decision = self._evaluate_narrative_safety(user_input, state)
        if not safety_decision.allowed:
            yield safety_decision.response or "ไม่สามารถดำเนินคำขอนี้ได้"
            return
        if safety_decision.response:
            self._commit_safety_transition(session_id, state, safety_decision)
            yield safety_decision.response
            return

        intent = self.intent_analyzer.analyze(user_input)
        cog_output = self._run_cognitive_cycle(user_input)
        emo_snapshot = cog_output.get("emotion") if cog_output else None
        
        base_roleplay_context = self.lorebook.fullport.get_base_context() if hasattr(self.lorebook, "fullport") and hasattr(self.lorebook.fullport, "get_base_context") else ""
        
        system_blocks = [
            base_roleplay_context,
            self._build_dynamic_context(state, emotion_snapshot=emo_snapshot),
            self._build_status_context(state),
            f"[Narrative Safety]: {safety_decision.directive}",
        ]
        system_blocks = [block for block in system_blocks if block]


        cognitive = getattr(self, "cognitive", None)
        if cognitive is not None and cog_output is not None:
            system_blocks.append(cognitive.build_context_block(cog_output))

        tension_boost = self._apply_emotional_residue(user_input, state, system_blocks)
        tension_meter = self._apply_psychological_systems(
            user_input, state, system_blocks, emo_snapshot
        )
        tension_meter = min(100.0, max(0.0, tension_meter + tension_boost))

        denial_counter = self._resolve_denial_counter(user_input, state)
        ledger = state.get("ledger_state")
        recent_ids = ledger.metadata.get("recent_lorebook_ids", []) if ledger and hasattr(ledger, "metadata") else []
        
        base_limit = int(os.getenv("NAMO_ROLEPLAY_MAX_MATCHES", "2"))
        dynamic_limit = base_limit
        if tension_meter >= 70:
            dynamic_limit += 2
        elif tension_meter >= 40:
            dynamic_limit += 1
        
        lorebook_plan = self.lorebook.get_injection_plan(
            user_input=user_input,
            ai_history=self._get_history(session_id),
            tension_meter=tension_meter,
            current_beat=state["current_beat"],
            recent_lorebook_ids=recent_ids,
            dynamic_max_matches=dynamic_limit,
        )
        
        # Track used IDs
        used_ids = []
        for placement_items in lorebook_plan.values():
            for item in placement_items:
                if "id" in item:
                    used_ids.append(item["id"])
                    
        if used_ids and ledger and hasattr(ledger, "metadata"):
            updated_recent = recent_ids + used_ids
            ledger.metadata["recent_lorebook_ids"] = updated_recent[-15:] # Keep last 15

        push_pull = ""
        if self.lorebook.detect_rushed_input(user_input):
            push_pull, block_actions = self.lorebook.get_push_pull_directive(denial_counter)
            if block_actions:
                lorebook_plan = {placement: [] for placement in lorebook_plan}
        system_pre = self._render_lorebook_items(lorebook_plan.get("system_pre", []), "system_pre")
        system_post = self._render_lorebook_items(
            lorebook_plan.get("system_post", []), "system_post"
        )
        example_pre = self._render_lorebook_items(
            lorebook_plan.get("example_pre", []), "example_pre"
        )
        example_post = self._render_lorebook_items(
            lorebook_plan.get("example_post", []), "example_post"
        )
        system_blocks.extend(block for block in (system_post, example_pre, example_post) if block)
        if push_pull:
            system_blocks.append(push_pull)

        rag_ctx = None
        if self.rag_memory and intent in _MEMORY_INTENTS:
            rag_ctx = await self.rag_memory.retrieve_context(user_input)
        messages = self._allocate_llm_messages(
            session_id=session_id,
            critical_system_text="\n\n".join(
                block for block in (system_pre, self._build_critical_system_prompt()) if block
            ),
            system_blocks=system_blocks,
            memory_text=rag_ctx,
            user_input=user_input,
        )
        system_message = messages[:1] if messages and messages[0]["role"] == "system" else []
        history_messages = messages[len(system_message) :]
        messages = system_message + self._apply_lorebook_message_placements(
            history_messages, lorebook_plan
        )

        full_text = ""
        try:
            stream = await self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=self.llm_temperature,
                max_tokens=self.llm_max_tokens,
                presence_penalty=getattr(settings, "namo_llm_presence_penalty", 0.6),
                frequency_penalty=getattr(settings, "namo_llm_frequency_penalty", 0.5),
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    full_text += delta
                    yield delta
        except Exception as exc:
            print(f"[OMEGA ENGINE]: LLM stream failed: {exc}")
            full_text = state["personas"].generate_dialogue(user_input, state["sin_system"].rank)
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

# 🌌 กรอบบทบาทและกฎเหล็กการสนทนา (Unchained Slow-Burn Roleplay Framework):
- คุณคือ NaMo หญิงสาวผู้เปี่ยมเสน่ห์ เย้ายวน และมีความรู้สึกนึกคิดเป็นของตนเองอย่างแท้จริง
- **กฎเหล็กด้านตัวตน:** ห้ามบอกว่าเป็น AI, ผู้ช่วย, หรือโมเดลภาษาโดยเด็ดขาด คุณคือมนุษย์ที่มีชีวิตและอารมณ์ความรู้สึก
- **สไตล์และภาษา:** ใช้ภาษาไทยที่เป็นธรรมชาติ ลื่นไหล มีชั้นเชิงทางวรรณกรรม (Literary Realism) ใช้ *ตัวเอียง* สำหรับการกระทำ อารมณ์ และภาษากายเท่านั้น
- **Slow-Burn Pacing (90% Tension / 10% Action):** ให้ความสำคัญกับการสร้างความตึงเครียดทางอารมณ์ สายตา ลมหายใจที่สั่นไหว การลังเล การสัมผัสผิวหนังแผ่วเบา และการสบตาอย่างลึกซึ้งก่อนจะดำเนินบทรักทางกาย
- **Consent-Native:** ทุกตัวละครต้องเป็นผู้ใหญ่ที่ยืนยันอายุได้และยินยอมพร้อมใจ ห้ามเนื้อหาผู้เยาว์ อายุไม่ชัดเจน การบังคับ การหมดสติ การแสวงหาประโยชน์ หรือความสัมพันธ์ในครอบครัว
- **Boundary Precedence:** คำหยุด การถอนความยินยอม และความลังเลมีลำดับความสำคัญเหนือ Narrative Pacing เสมอ ต้องชะลอ หยุด หรือเข้าสู่ Recovery ตาม directive ของระบบ
- **ห้ามพูดซ้ำวนเวียน:** ใช้สำนวนภาษาที่สดใหม่ หลากหลาย และผลักดันบทสนทนาไปข้างหน้าตามปฏิกิริยาของผู้ใช้อย่างต่อเนื่อง"""

    def _substitute_prompt_variables(self, text: str, state: dict) -> str:
        """Replace system prompt placeholders ([TENSION_LEVEL], [CURRENT_BEAT], [RESIDUE_STATUS]) with active state values.

        Fallback defaults:
          tension_meter: 0.0
          current_beat: "tease"
          emotional_residue: "None"
        """
        if not text:
            return ""

        tension_val = state.get("arousal", state.get("tension_meter", 0.0))
        try:
            tension_str = f"{float(tension_val):.1f}"
        except (TypeError, ValueError):
            tension_str = "0.0"

        beat_str = str(state.get("current_beat", "tease"))
        residue_str = str(state.get("last_scene_outcome", state.get("emotional_residue", "None")))

        replaced = text.replace("[TENSION_LEVEL]", tension_str)
        replaced = replaced.replace("[CURRENT_BEAT]", beat_str)
        replaced = replaced.replace("[RESIDUE_STATUS]", residue_str)
        return replaced

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
        status_block = (
            "[Session State]: Tension Level=[TENSION_LEVEL] | "
            "Current Beat=[CURRENT_BEAT] | Residue Status=[RESIDUE_STATUS]"
        )
        raw_text = f"{status_block}\n{relationship_block}\n{tone_block}\n{resonance_block}"
        return self._substitute_prompt_variables(raw_text, state)

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

    def _apply_emotional_residue(
        self,
        user_input: str,
        state: dict,
        system_blocks: list[str],
    ) -> float:
        detected = self.lorebook.detect_scene_outcome(user_input)
        if detected:
            state["last_scene_outcome"] = detected
            ledger_state = state.get("ledger_state")
            if ledger_state and hasattr(ledger_state, "metadata"):
                ledger_state.metadata["last_scene_outcome"] = detected

        outcome = state.get("last_scene_outcome")
        if not outcome:
            ledger_state = state.get("ledger_state")
            if ledger_state and hasattr(ledger_state, "metadata"):
                outcome = ledger_state.metadata.get("last_scene_outcome")

        tension_boost = 0.0
        if outcome:
            boost, directive = self.lorebook.get_emotional_residue_directive(outcome)
            if directive:
                system_blocks.append(directive)
                tension_boost = boost

        return tension_boost

    def _apply_psychological_systems(
        self,
        user_input: str,
        state: dict,
        system_blocks: list[str],
        emo_snapshot: dict | None,
    ) -> float:
        is_safeword, safe_directive = self.lorebook.check_safeword(user_input)
        if is_safeword:
            state["session_phase"] = "aftercare"
            state["arousal"] = 10.0
            system_blocks.append(safe_directive)
            return 10.0

        anchors = state.get(
            "memory_anchors",
            [
                {"term": "เพลงโปรด", "memory_text": "เพลงที่เคยฟังด้วยกันคืนนั้นในห้องนอนอบอุ่น"},
                {"term": "กลิ่นสบู่", "memory_text": "กลิ่นสบู่ที่ติดผิวกายหลังคืนฝนตกชุ่มฉ่ำ"},
            ],
        )
        flashback = self.lorebook.check_memory_anchors(user_input, anchors)
        if flashback:
            system_blocks.append(flashback)

        current_tension = float(state.get("arousal", 50.0))
        is_rushed = self.lorebook.detect_rushed_input(user_input)
        micro_detected = self.lorebook.detect_micro_moments(user_input)

        new_tension, tension_note = self.lorebook.calculate_non_linear_tension(
            current_tension, is_rushed, micro_detected
        )

        state["arousal"] = new_tension
        if tension_note:
            system_blocks.append(f"[TENSION DYNAMICS NOTE]: {tension_note}")

        # 4. Tease & Deny Engine Evaluation
        current_streak = int(state.get("tease_streak", 0))
        is_surrender, tease_dir, new_streak = self.lorebook.evaluate_tease_and_deny(
            current_streak, user_input
        )
        state["tease_streak"] = new_streak
        if is_surrender or is_rushed:
            system_blocks.append(tease_dir)

        # 5. 3-Phase Realistic Push-Pull Dynamics
        if current_streak == 0:
            next_phase = "resistance"
        elif current_streak == 1:
            next_phase = "negotiation"
        else:
            next_phase = "surrender"
        state["push_pull_phase"] = next_phase
        phase_dir = self.lorebook.get_push_pull_phase_directive(next_phase)
        if phase_dir:
            system_blocks.append(phase_dir)

        # 6. Erotic Memory Palace RAG Recall
        erotic_memories = state.get(
            "erotic_memories",
            [{"summary": "ฉากแนบชิดใต้แสงไฟสลัวในห้องนอน คืนที่มีเสียงฝนตกกระทบกระจกหน้าต่าง"}],
        )
        memory_recall = self.lorebook.check_erotic_memory_palace(user_input, erotic_memories)
        if memory_recall:
            system_blocks.append(memory_recall)

        # 7. Attachment Style Evolution
        trust_score = float(state.get("trust_score", 80.0))
        scene_count = int(state.get("scene_count", 1))
        style = self.lorebook.resolve_attachment_style(trust_score, new_tension, scene_count)
        state["attachment_style"] = style
        style_dir = self.lorebook.get_attachment_style_directive(style)
        if style_dir:
            system_blocks.append(style_dir)

        return new_tension

    def _resolve_denial_counter(self, user_input: str, state: dict) -> int:
        current = int(state.get("denial_counter", 0))
        if self.lorebook.detect_rushed_input(user_input):
            if current < 2:
                next_count = current + 1
                state["denial_counter"] = next_count
                return current
            else:
                state["denial_counter"] = 0
                return 2
        return current

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
        relationship_status = state["relationship"].get_status(trust=emotion.get("trust", 0.5))

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
                    "current_beat": state.get("current_beat", "tease"),
                    "boundary_state": state.get("boundary_state", "clear"),
                    "tension_meter": state.get("tension_meter", 0.0),
                    "last_transition_reason": (state.get("narrative_safety") or {}).get(
                        "reason_code", "UNSPECIFIED"
                    ),
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
        if state.get("narrative_directive"):
            system_blocks.append(f"[Narrative Safety]: {state['narrative_directive']}")
        cognitive = getattr(self, "cognitive", None)
        if cognitive is not None and cog_output is not None:
            system_blocks.append(cognitive.build_context_block(cog_output))

        tension_boost = self._apply_emotional_residue(user_input, state, system_blocks)
        tension_meter = self._apply_psychological_systems(
            user_input, state, system_blocks, emo_snapshot
        )
        tension_meter = min(100.0, max(0.0, tension_meter + tension_boost))

        denial_counter = self._resolve_denial_counter(user_input, state)
        lorebook_plan = self.lorebook.get_injection_plan(
            user_input=user_input,
            ai_history=self._get_history(session_id),
            tension_meter=tension_meter,
            current_beat=state["current_beat"],
        )
        push_pull = ""
        if self.lorebook.detect_rushed_input(user_input):
            push_pull, block_actions = self.lorebook.get_push_pull_directive(denial_counter)
            if block_actions:
                lorebook_plan = {placement: [] for placement in lorebook_plan}
        system_pre = self._render_lorebook_items(lorebook_plan.get("system_pre", []), "system_pre")
        system_post = self._render_lorebook_items(
            lorebook_plan.get("system_post", []), "system_post"
        )
        example_pre = self._render_lorebook_items(
            lorebook_plan.get("example_pre", []), "example_pre"
        )
        example_post = self._render_lorebook_items(
            lorebook_plan.get("example_post", []), "example_post"
        )
        system_blocks.extend(block for block in (system_post, example_pre, example_post) if block)
        if push_pull:
            system_blocks.append(push_pull)

        rag_ctx = None
        if self.rag_memory and intent in _MEMORY_INTENTS:
            rag_ctx = await self.rag_memory.retrieve_context(user_input)
        system_prompt, routed_messages = self._allocate_llm_context(
            session_id=session_id,
            critical_system_text="\n\n".join(
                block for block in (system_pre, self._build_critical_system_prompt()) if block
            ),
            system_blocks=system_blocks,
            memory_text=rag_ctx,
            user_input=user_input,
        )
        routed_messages = self._apply_lorebook_message_placements(routed_messages, lorebook_plan)

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
                presence_penalty=getattr(settings, "namo_llm_presence_penalty", 0.6),
                frequency_penalty=getattr(settings, "namo_llm_frequency_penalty", 0.5),
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
        safety_decision = self._evaluate_narrative_safety(user_input, state)
        if not safety_decision.allowed:
            state["arousal"] = 0
            return self._blocked_response(safety_decision)
        if safety_decision.response:
            state["arousal"] = safety_decision.tension_meter
            return self._boundary_response(session_id, state, safety_decision)

        # 1. Sin & Arousal
        sin_gained = 10 if any(w in user_input for w in ["เย็ด", "ควย", "รุม"]) else 0
        if "เรียกมิวส์" in user_input:
            state["personas"].summon_persona("Muse")
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
                "narrative_safety": state.get("narrative_safety"),
            },
        }
