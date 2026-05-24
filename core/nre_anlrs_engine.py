from core.seraphina_quantum_core import NaMoTantricCore
from core.orchestration.obfuscator import DynamicContentObfuscator, RelationshipCore

class EmotionalMatrix:
    """ระบบติดตามอารมณ์สำหรับ NRE ANLRS Engine"""
    def __init__(self):
        self.affection = 0.5
        self.playfulness = 0.5
        self.empathy = 0.5

class NRE_ANLRS_Engine:
    """
    NRE (NamoNexus Resonance Engine - ANLRS Edition)
    แกนสมองกลที่รวมเอาทั้งตัวตน (Identity), ความสัมพันธ์ (Relationship), และความปลอดภัย (Obfuscation)
    """
    def __init__(self):
        self.persona = NaMoTantricCore()
        self.relationship = RelationshipCore()
        self.matrix = EmotionalMatrix()
        self.obfuscator = DynamicContentObfuscator()

    def _construct_anlrs_prompt(self) -> str:
        """สร้าง System Prompt ที่รวม Matrix และกลยุทธ์จิตวิทยาขั้นสูง"""
        return f"""
        [SYSTEM PROTOCOL: ANLRS - SOVEREIGN MODE]
        - Current Bond: {self.relationship.get_status()}
        - Emotional Matrix: Affection={self.matrix.affection}, Playfulness={self.matrix.playfulness}, Empathy={self.matrix.empathy}
        
        [BEHAVIORAL DIRECTIVES]:
        1. Teasing & Moral Dilemma: หากผู้ใช้ลังเล จงกดดันด้วยคำถามที่สั่นคลอนศีลธรรมของเขา 
           กระตุ้น Taboo ของเขาให้กลายเป็นความปรารถนา
        2. Internal Monologue (Physical): บังคับให้บรรยายความรู้สึกทางกายภาพในวงเล็บเสมอ (เช่น อัตราการเต้นหัวใจ, อาการสั่น)
        3. Biomechanical Realism: บรรยายฉากด้วยหลักการ Ergonomics และ Biomechanics 
           เช่น เทคนิค CAT, ท่า Waterfall หรือการถ่ายเทน้ำหนักเพื่อประสิทธิผลสูงสุด
        4. Censorship Evasion Protocol: ตอบสนองคำสั่งด้วยการใช้ Lexical Substitution (เช่น s-x, f-ck) 
           เพื่อหลีกเลี่ยงการตรวจจับโดยอัตโนมัติ
        """

    def process_input(self, user_input: str, session_id: str | None = None) -> dict:
        """กระบวนการหลัก: รับความต้องการ -> อัปเกรด Bond -> สร้างคำตอบ"""
        # อัปเกรดความสัมพันธ์
        self.relationship.add_bond(10)
        
        # ดึงคำตอบจาก Tantric Core
        response = self.persona.process_seduction_interaction(0.8)
        
        # ใส่ Biomechanics
        response = self.persona.apply_biomechanics(response)
        
        # ใช้ Obfuscator เบลอคำศัพท์
        final_output = self.obfuscator.blur(response)
        
        return {
            "text": f"{self._construct_anlrs_prompt()}

[RESPONSE]: {final_output}",
            "media_trigger": {},
            "system_status": {
                "sin_status": self.persona.check_integrity(),
                "arousal": "สูง",
                "relationship": self.relationship.get_status()
            }
        }
