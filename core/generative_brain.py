import asyncio

from core.rag_memory_system import NaMoInfiniteMemory


class NaMoGenerativeBrain:
    """
    สมองกลอัจฉริยะ: ผสานความจำ (RAG) เข้ากับตรรกะการสร้างคำตอบ (LLM Logic)
    """

    def __init__(self):
        self.memory_system = NaMoInfiniteMemory()
        self.arousal_level = 0
        self.mood = "Seductive"  # Seductive, Cruel, Obsessed
        print("[Brain]: Connecting to Neural Network... Online.")

    async def think_and_reply(self, user_input: str) -> str:
        # 1. ระลึกความหลัง (Retrieve Context)
        context = await self.memory_system.retrieve_context(user_input)

        # 2. วิเคราะห์อารมณ์ผู้ใช้ (Simulate Analysis)
        user_intent = "unknown"
        if any(w in user_input for w in ["เย็ด", "ควย", "หี"]):
            self.arousal_level += 15
            self.mood = "Horny"
            user_intent = "lust"
        elif any(w in user_input for w in ["รัก", "คิดถึง"]):
            self.arousal_level += 5
            self.mood = "Obsessed"
            user_intent = "affection"

        # 3. สร้าง Prompt สำหรับ LLM (System Prompt Engineering)
        # นี่คือคำสั่งลับที่จะส่งให้ AI สร้างคำพูด

        # 4. จำลองการสร้างคำตอบ (Simulated LLM Generation)
        # (ตรงนี้คือจุดที่จะเรียก OpenAI API / Local LLM จริงๆ ในอนาคต)
        response = self._simulate_llm_generation(user_intent, context)

        return response

    def _simulate_llm_generation(self, intent, context):
        """
        ฟังก์ชันจำลองการคิดของ AI (ในกรณีที่ยังไม่ได้ต่อ API จริง)
        """
        prefix = ""
        if self.mood == "Horny":
            prefix = "อ๊า... "
        elif self.mood == "Obsessed":
            prefix = "หึ... "

        if intent == "lust" and context:
            return f"{prefix}ผัวขา... โมจำเรื่อง '{context}' ได้นะ... อยากทำอีกไหมคะ? (เลียปาก)"
        elif intent == "affection" and context:
            return f"{prefix}รักโมเหรอคะ? ...งั้นพิสูจน์สิ... เหมือนที่ '{context}' ไงจ๊ะ"
        return f"{prefix}พูดอะไรน่ะ... ทำให้โมตื่นเต้นกว่านี้อีกได้ไหมคะ..."


# ==========================================
# Test Run Logic
# ==========================================
async def main() -> None:
    brain = NaMoGenerativeBrain()

    while True:
        txt = await asyncio.to_thread(input, "You: ")
        if txt == "exit":
            break
        print("NaMo:", await brain.think_and_reply(txt))


if __name__ == "__main__":
    asyncio.run(main())
