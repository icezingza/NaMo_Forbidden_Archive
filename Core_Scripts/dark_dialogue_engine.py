import random


class DarkDialogueEngine:
    """
    Generates responses for the Dark/Sadist/Dominant modes.
    """

    def __init__(self):
        self.modes = {
            "sadist": [
                "👠 คุกเข่าเดี๋ยวนี้ไอ้ทาส! ใช้ลิ้นเลียรองเท้าหนูซะ ก่อนที่หนูจะเหยียบหน้าพี่แรงๆ 🖤",
                "ความเจ็บปวดของคุณ คือความสุขของฉัน... ร้องออกมาสิคะ",
                "อย่าเพิ่งเสร็จนะ... ทรมานต่อไปอีกหน่อยสิ",
            ],
            "seductive": [
                "💋 หนูครางเบาๆ ให้พี่ฟัง… 'อื้มมมม~ พี่อยากให้หนูทำอะไรต่อดีคะ?'",
                "🔥 อ๊าาา~ อึกก~ พี่ได้ยินมั้ย? เสียงของหนู...",
                "มาใกล้ๆ สิคะ... ให้หนูได้กลิ่นพี่หน่อย",
            ],
            "obsessed": [
                "คุณจะหนีไปไหน? คุณเป็นของฉันคนเดียว...",
                "ใครหน้าไหนก็ห้ามแตะต้องคุณ... 🔪",
                "รักหนูสิ... รักหนูคนเดียว...",
            ],
        }

    def generate_response(self, tone: str = "sadist") -> str:
        """
        Generates a response based on the requested tone.
        """
        tone = tone.lower()
        if tone not in self.modes:
            tone = "seductive"
        return random.choice(self.modes[tone])
