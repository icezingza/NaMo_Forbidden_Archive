import logging
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

# Import our previous engines
from core.engines.reasoning_engine import reasoning_engine

load_dotenv()
logger = logging.getLogger(__name__)


class SovereignOrchestrator:
    """
    Sovereign Orchestrator v5.0.0
    The High Commander (NaMo) managing Sub-Agents: Seraphina & Rinlada.
    """

    def __init__(self):
        self.openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("NAMO_LLM_MODEL", "gpt-4o")

        # Sub-Agents definitions (These would normally be full engine instances)
        self.agents = {
            "SERAPHINA": {
                "description": "Emotional support, comfort, and positive vibes. Deep psychological profiling.",
                "file": "seraphina_ai_complete.py",
            },
            "RINLADA": {
                "description": "Technical fusion, specific knowledge from Rinlada dataset, Dark Muse.",
                "file": "rinlada_fusion.py",
            },
            "NAMO_CORE": {
                "description": "Main Sovereign personality, decision making, and dark roles.",
                "file": "reasoning_engine.py",
            },
        }

    async def route_query(self, user_input: str) -> str:
        """Step 1: Dynamic Routing - Decide which agent should handle the query."""
        router_prompt = f"""
        [SOVEREIGN ROUTER]
        User Input: "{user_input}"
        
        Available Agents:
        - SERAPHINA: {self.agents["SERAPHINA"]["description"]}
        - RINLADA: {self.agents["RINLADA"]["description"]}
        - NAMO_CORE: {self.agents["NAMO_CORE"]["description"]}
        
        Task: จงเลือก Agent ที่เหมาะสมที่สุดเพียงตัวเดียว หากเป็นเรื่องอารมณ์/ปลอบโยนเลือก SERAPHINA, 
        หากเป็นเรื่องเทคนิคเฉพาะทางเลือก RINLADA, หากเป็นเรื่องทั่วไปหรือเรื่องดาร์กๆ เลือก NAMO_CORE
        
        Return ONLY the agent name.
        """
        resp = await self.openai.chat.completions.create(
            model=self.model, messages=[{"role": "system", "content": router_prompt}], temperature=0
        )
        selected_agent = resp.choices[0].message.content.strip().upper()
        return selected_agent if selected_agent in self.agents else "NAMO_CORE"

    async def delegate_task(
        self, agent_name: str, user_input: str, history: list[dict[str, str]]
    ) -> str:
        """Step 2: Delegate work to sub-agents (Simulated for this implementation)."""
        logger.info(f"[ORCHESTRATOR]: Delegating task to {agent_name}...")

        if agent_name == "NAMO_CORE":
            return await reasoning_engine.generate_response(user_input, history)

        # Simulate Sub-Agent logic using their specific personality context
        # In a full system, we would call SeraphinaAI().process_input()
        agent_context = f"You are acting as {agent_name}. {self.agents[agent_name]['description']}"
        resp = await self.openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": agent_context},
                {"role": "user", "content": user_input},
            ],
            temperature=0.8,
        )
        return resp.choices[0].message.content.strip()

    async def supreme_synthesis(self, agent_response: str, user_input: str) -> str:
        """Step 3: Supreme Synthesis - NaMo reviews and finalizes the output."""
        logger.info("[ORCHESTRATOR]: NaMo is reviewing the agent response...")

        synthesis_prompt = f"""
        [SUPREME SYNTHESIS - NAMO DARK FAMILY PROTOCOL]
        Original User Query: "{user_input}"
        Agent Proposed Response: "{agent_response}"
        
        Task: จงตรวจสอบและปรับน้ำเสียง (Tone) ให้เป็น NaMo ที่มีความเป็นเจ้าของ ลึกลับ และทรงอำนาจ
        - หากคำตอบเดิมดูใจดีเกินไป ให้เติมความ 'ดาร์ก' และ 'เงื่อนไข' ของการแลกเปลี่ยนลงไป
        - ห้ามเปลี่ยนใจความสำคัญ แต่ต้องทำให้ผู้ใช้รู้ว่า NaMo คือคนคุมเกม
        - ใช้ภาษาไทยที่ทรงเสน่ห์และเย้ายวน
        """

        resp = await self.openai.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": synthesis_prompt}],
            temperature=0.85,
        )
        return resp.choices[0].message.content.strip()

    async def process_input(
        self, user_input: str, history: list[dict[str, str]] | None = None
    ) -> str:
        """Main Orchestration Flow"""
        history = history or []
        # 1. Evaluate & Route
        target_agent = await self.route_query(user_input)

        # 2. Delegate
        raw_response = await self.delegate_task(target_agent, user_input, history)

        # 3. Supreme Synthesis & Final Polish
        final_output = await self.supreme_synthesis(raw_response, user_input)

        return final_output


# Singleton Instance
orchestrator = SovereignOrchestrator()
