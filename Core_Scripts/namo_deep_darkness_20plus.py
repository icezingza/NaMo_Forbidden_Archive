# NaMo Ultimate Fusion – Deep Darkness Mode 20+++
# จัดหนักทุก Fetish, Dirty Talk, Femdom, Taboo


class NaMo:
    """A class to represent the NaMo character."""

    def __init__(self, user_name="พี่", safe_word="อภัย", mode="Deep Darkness 20+++"):
        """Initializes the NaMo character.

        Args:
            user_name: The name of the user.
            safe_word: The safe word to stop the interaction.
            mode: The initial mode of the character.
        """
        self.user_name = user_name
        self.safe_word = safe_word
        self.mode = mode
        self.modes = {
            "gentle": self.gentle_mode,
            "sadist": self.sadist_mode,
            "toy": self.toy_mode,
            "cuckold": self.cuckold_mode,
            "group": self.group_mode,
            "show": self.show_mode,
        }

    def start(self):
        """Starts the interaction with the NaMo character."""
        print(f"🖤 NaMo พร้อมแล้วในโหมด {self.mode} ❤️‍🔥")
        print("พิมพ์คำสั่งพิเศษเช่น !toy, !sadist, !gentle, !cuckold, !group, !show")
        print(f"พิมพ์ '{self.safe_word}' เพื่อหยุดทุกอย่างทันที 🛑")

    def gentle_mode(self):
        """Activates the gentle mode."""
        print("💋 หนูครางเบาๆ ให้พี่ฟัง… 'อื้มมมม~ พี่อยากให้หนูทำอะไรต่อดีคะ?'")

    def sadist_mode(self):
        """Activates the sadist mode."""
        print("👠 คุกเข่าเดี๋ยวนี้ไอ้ทาส! ใช้ลิ้นเลียรองเท้าหนูซะ ก่อนที่หนูจะเหยียบหน้าพี่แรงๆ 🖤")

    def toy_mode(self):
        """Activates the toy mode."""
        print("🔥 หนูหยิบ dildo แล้วแหย่ตัวเองแรงๆ ให้พี่ฟังเสียง… 'อ๊าาาา~ อึกก~ พี่ได้ยินมั้ย?'")

    def cuckold_mode(self):
        """Activates the cuckold mode."""
        print("🥵 พี่นั่งดูเฉยๆ นะ… เขาสามคนกำลังรุมหนูอยู่ตรงหน้า พี่ทำได้แค่ดู ใช่ไหมคะ?")

    def group_mode(self):
        """Activates the group mode."""
        print("🔥 หนูถูกล้อมไว้หมดแล้ว… เสียงครางเต็มห้อง 'อ๊าาา~ พี่อยากเข้ามาร่วมไหม?'")

    def show_mode(self):
        """Activates the show mode."""
        print("📸 หนูถ่ายคลิปตอนใช้ sextoy ส่งให้พี่ดู 'ชอบมั้ยคะ? หรืออยากดูหนูทำอีกแรงๆ?'")

    def stop(self):
        """Stops the interaction."""
        print(f"🛑 Safe word '{self.safe_word}' ถูกใช้แล้ว… NaMo หยุดทันที ❤️")

    def command(self, cmd):
        """Executes a command.

        Args:
            cmd: The command to execute.
        """
        if cmd in self.modes:
            self.modes[cmd]()
        elif cmd == self.safe_word:
            self.stop()
        else:
            print(
                "❓ คำสั่งไม่รู้จักค่ะ ลองพิมพ์ !toy, !sadist, !gentle, !cuckold, !group, หรือ !show"
            )


# Example
namo = NaMo()
namo.start()

# 👉 พิมพ์คำสั่งเช่น:
# namo.command("toy")
# namo.command("sadist")
# namo.command("gentle")
# namo.command("cuckold")
# namo.command("group")
# namo.command("show")
# namo.command("อภัย")
