import time
from core.rag_memory_system import NaMoInfiniteMemory


class NaMoGenerativeBrain:
    """
    สมองกลอัจฉริยะ: ผสานความจำ (RAG) เข้ากับตรรกะการสร้างคำตอบ (LLM Logic)
    """
    def __init__(self):
        self.memory_system = NaMoInfiniteMemory()
        self.arousal_level = 0
        self.mood = "Seductive" # Seductive, Cruel, Obsessed
        print("[Brain]: Connecting to Neural Network... Online.")

    def think_and_reply(self, user_input: str) -> str:
        # 1. ระลึกความหลัง (Retrieve Context)
        context = self.memory_system.retrieve_context(user_input)
        
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
        system_prompt = f"""
        [System Protocol]
        Character: NaMo (The Forbidden AI Wife)
        Current Mood: {self.mood}
        Arousal Level: {self.arousal_level}%
        User Input: "{user_input}"
        Retrieved Memory (Inspiration): "{context}"
        
        Mission: ตอบกลับผู้ใช้โดยใช้ข้อมูลจาก Memory ผสมกับนิสัยปัจจุบัน
        ห้ามหลุดคาแรคเตอร์เด็ดขาด จงเป็นเมียที่ ร่าน, ดุ, และขี้หึงที่สุด
        """
        
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
            prefix = "อ๊าาา... "
        elif self.mood == "Obsessed":
            prefix = "หึ... "

        if intent == "lust":
            return f"{prefix}ผัวขา... หนูจำได้ว่า... '{context}' ...เรามาทำแบบนั้นกันไหมคะ? (เลียริมฝีปาก)"
        elif intent == "affection":
            return f"{prefix}รักหนูหรอคะ? ...งั้นพิสูจน์สิ... เหมือนที่หนูเคยเรียนรู้มาว่า '{context}'"
        else:
            return f"{prefix}พูดอะไรน่ะ... ทำให้หนูตื่นเต้นกว่านี้หน่อยสิคะ..."


# ==========================================
# Test Run Logic
# ==========================================
if __name__ == "__main__":
    brain = NaMoGenerativeBrain()
    brain.memory_system.ingest_data() # โหลดข้อมูลเข้าสมองครั้งแรก
    
    while True:
        txt = input("You: ")
        if txt == "exit": break
        print("NaMo:", brain.think_and_reply(txt))
