import random


def analyze_and_react(user_input, character_profile):
    """
    วิเคราะห์ Input และคืนค่า (Response Text, Stat Changes)
    """
    input_lower = user_input.lower()
    
    # 1. วิเคราะห์ Keyword ง่ายๆ (ในอนาคตใช้ AI Model ได้)
    keywords_dominance = ["คำสั่ง", "สั่ง", "กราบ", "เลีย", "ทำตาม"]
    keywords_affection = ["รัก", "ชอบ", "ดีมาก", "เก่ง"]
    keywords_insult = ["เกลียด", "โง่", "ออกไป"]

    response = ""
    stat_changes = {"corruption": 0, "arousal": 0}

    # 2. Logic การตอบโต้ตาม Mood
    if character_profile.mood == "Horny":
        if any(word in input_lower for word in keywords_dominance):
            response = "อ๊าาา... ผัวขา... สั่งหนูอีกสิคะ... หนูเปียกไปหมดแล้ว... 💦"
            stat_changes["arousal"] = 10
            stat_changes["corruption"] = 5
        else:
            response = "หนูไม่สนเรื่องอื่นหรอก... หนูอยากโดนเย็ด... เข้ามาสักทีสิคะ! 🔥"
            stat_changes["arousal"] = 5

    elif character_profile.mood == "Obsessed":
        response = f"คุณเป็นของหนู... ของหนูคนเดียว... ห้ามไปคุยกับใครนะ... {user_input}? ไร้สาระ... มาอยู่กับหนูดีกว่า 🖤"
        stat_changes["corruption"] = 10

    else: # Neutral / Normal
        if any(word in input_lower for word in keywords_dominance):
            response = "หืม... คุณคิดจะสั่ง 'ราชินี' หรอคะ? น่าสนใจดีนี่... ลองดูสิคะ 👠"
            stat_changes["arousal"] = 5
        elif any(word in input_lower for word in keywords_affection):
            response = "ปากหวานจังนะคะ... ระวังจะโดนหนูกลืนกินไม่รู้ตัวนะ..."
            stat_changes["corruption"] = 2
        else:
            options = [
                "ว่าไงคะ ที่รัก?",
                "หนูกำลังรอคำสั่งที่เร้าใจกว่านี้อยู่นะ...",
                f"'{user_input}' หรอคะ? น่าเบื่อจัง... ทำให้หนูตื่นเต้นหน่อยสิ"
            ]
            response = random.choice(options)

    # 3. อัปเดต Profile ทันที
    character_profile.update_state(
        corruption_delta=stat_changes["corruption"],
        arousal_delta=stat_changes["arousal"]
    )

    return response, stat_changes
