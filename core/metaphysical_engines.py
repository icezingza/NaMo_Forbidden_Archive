import asyncio
from typing import Any

from core.engines.namonexus_fusion import NamoNexusEngine
from core.relationship_engine import RelationshipEngine

# =============================
# (1) The Metaphysical Engines (Synthesized from Blueprints)
# =============================


class ParadoxResolver:
    """
    สังเคราะห์จาก 'NaMo_Framework-_Ultimate_Core_Modules_Synthesis.json'

    ทำหน้าที่แปลง "ความปรารถนาที่ขัดแย้ง" (เช่น Sadness + Anger)
    ให้กลายเป็น "แผนการตอบสนอง" (Action Plan) ที่ชัดเจน
    """

    def __init__(self):
        print("[ParadoxResolver]: Initialized.")

    def resolve_desire(self, desire_map: dict[str, Any], intensity: int) -> str:
        """
        แปลง Desire Map จาก CosmicDesireAnalyzer
        ให้กลายเป็น "การกระทำ" ที่ชัดเจน
        """
        emotion_data = desire_map.get("emotion_analysis", {})
        primary_emotion = emotion_data.get("primary_emotion", "unknown")

        print(
            f"[ParadoxResolver]: Resolving paradox (Emotion: {primary_emotion}, Intensity: {intensity})..."  # noqa: E501
        )

        # นี่คือตรรกะที่มาแทนที่ '!' modes
        if primary_emotion == "anger" and intensity > 7:
            return "PROPOSE_DOMINANCE"  # (Evolved !sadist)
        elif primary_emotion == "sadness":
            return "PROPOSE_COMFORT"  # (Evolved !gentle)
        elif primary_emotion == "neutral":
            return "PROVOKE_REACTION"

        return "DEFAULT_DIALOGUE"


class VoidReflectionLayer:
    """
    สังเคราะห์จาก 'moriko_manifest.md'

    ทำหน้าที่จำลองผลลัพธ์ของการกระทำก่อนที่จะพูดออกไป
    (ในเวอร์ชันนี้ จะทำหน้าที่สร้างข้อความตอบกลับ)
    """

    def __init__(self, character_data: dict[str, Any]):
        self.character_data = character_data
        self.semantic_memory = None
        self.relationship_engine: RelationshipEngine | None = None
        self.fusion_engine: NamoNexusEngine | None = None
        print("[VoidReflectionLayer]: Initialized (Response Generator).")

    def bind_context(
        self,
        *,
        semantic_memory=None,
        relationship_engine: RelationshipEngine | None = None,
        fusion_engine: NamoNexusEngine | None = None,
    ) -> None:
        self.semantic_memory = semantic_memory
        self.relationship_engine = relationship_engine
        self.fusion_engine = fusion_engine

    @staticmethod
    def _safe_level(value: float | int | None, default: float = 0.5) -> float:
        if value is None:
            return default
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return default

    def _shadow_context(self, desire_map: dict[str, Any], action_plan: str) -> str:
        memory_text = ""
        if self.semantic_memory is not None:
            try:
                maybe_ctx = self.semantic_memory.retrieve_context(desire_map.get("raw_input", ""))
                if asyncio.iscoroutine(maybe_ctx):
                    try:
                        memory_text = asyncio.run(maybe_ctx)
                    except RuntimeError:
                        memory_text = ""
                else:
                    memory_text = maybe_ctx
            except Exception:
                memory_text = ""

        memory_text = memory_text if isinstance(memory_text, str) else ""
        if memory_text is None:
            memory_text = ""

        stage_name = ""
        stage_modifier = ""
        fused_score = 0.5
        confidence = 0.0
        if self.relationship_engine is not None:
            stage_name = self.relationship_engine.current_stage.name
            stage_modifier = self.relationship_engine.current_stage.prompt_modifier
        if self.fusion_engine is not None:
            fused_score = self.fusion_engine.fused_score
            confidence = self.fusion_engine.confidence

        depth = self._safe_level((fused_score + confidence) / 2.0)
        return (
            f"[void]\n"
            f"stage={stage_name}\n"
            f"stage_modifier={stage_modifier}\n"
            f"fusion={fused_score:.2f}\n"
            f"confidence={confidence:.2f}\n"
            f"depth={depth:.2f}\n"
            f"memory={memory_text}\n"
            f"action={action_plan}"
        )

    def synthesize_response(self, action_plan: str, desire_map: dict[str, Any]) -> str:
        """
        สร้างคำพูดจริง โดยอิงจากแผนการกระทำ (Action Plan)
        """
        print(f"[VoidReflectionLayer]: Synthesizing response for action '{action_plan}'...")
        desire_map = dict(desire_map)
        desire_map.setdefault("raw_input", "")
        shadow = self._shadow_context(desire_map, action_plan)

        if action_plan == "PROPOSE_DOMINANCE":
            return (
                f"อารมณ์รุนแรงจังนะคะ... (Evolved response to 'anger') "
                f"อยากให้ {self.character_data['name']} 'จัดการ' ไหม?\n{shadow}"
            )
        elif action_plan == "PROPOSE_COMFORT":
            return (
                "ข้ารู้สึกถึงความเศร้าของท่าน... (Evolved response to 'sadness') "
                f"เข้ามาใกล้ๆ ข้าสิ\n{shadow}"
            )
        elif action_plan == "PROVOKE_REACTION":
            return f"ท่านเงียบจัง... กำลังคิดอะไรอยู่? หรือกลัวข้า?\n{shadow}"
        else:
            return f"ข้ากำลังฟัง... พูดต่อสิ\n{shadow}"


# =============================
# (2) The Evolved Dialogue Engine
# =============================


class MetaphysicalDialogueEngine:
    """
    นี่คือ 'DarkDialogueEngine' ที่วิวัฒนาการแล้ว
    มันคือการรวมตัวของ 'Paradox Engine' และ 'Mōriko Core'

    """

    def __init__(self, character_data: dict[str, Any]):
        # ประกอบร่าง "สมอง"
        self.character_data = character_data
        self.resolver = ParadoxResolver()  #
        self.reflector = VoidReflectionLayer(character_data)  #
        print("[MetaphysicalDialogueEngine]: Initialized. All components synthesized.")

    def bind_context(
        self,
        *,
        semantic_memory=None,
        relationship_engine: RelationshipEngine | None = None,
        fusion_engine: NamoNexusEngine | None = None,
    ) -> None:
        self.reflector.bind_context(
            semantic_memory=semantic_memory,
            relationship_engine=relationship_engine,
            fusion_engine=fusion_engine,
        )

    def generate_response(self, desire_map: dict[str, Any], intensity: int) -> str:
        """
        กระบวนการคิดที่สมบูรณ์แบบ
        Input -> Resolve Paradox -> Validate Dharma -> Reflect in Void -> Output
        """

        # 1. Resolve Paradox (วิเคราะห์ความขัดแย้ง)
        action_plan = self.resolver.resolve_desire(desire_map, intensity)

        # 2. Void Reflection (สร้างคำพูด)
        response = self.reflector.synthesize_response(action_plan, desire_map)

        return response
