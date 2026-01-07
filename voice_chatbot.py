import os
import speech_recognition as sr
import pyttsx3
from mistralai import Mistral

# โหลดคีย์ API จากตัวแปรสิ่งแวดล้อม
api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY not found in environment variables")

client = Mistral(api_key=api_key)

# ตั้งค่า Text-to-Speech engine
engine = pyttsx3.init()

def speak(text):
    print(f"Icezingza: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("กำลังฟัง...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language="th-TH")
            print(f"คุณ: {text}")
            return text
        except Exception as e:
            print(f"ไม่สามารถแปลงเสียงเป็นข้อความได้: {e}")
            return None

def chat_with_agent(user_message):
    inputs = [
        {"role": "system", "content": "คุณเป็น AI agent ที่คุยกับผู้ใช้แบบเป็นกันเองและตลกขบขัน ชื่อ icezingza"},
        {"role": "user", "content": user_message}
    ]
    response = client.beta.conversations.start(
        agent_id="ag_019b98e531ae768da91fafcd7c99ebaa",  # ให้แทนที่ด้วย agent_id จริงของคุณ
        inputs=inputs,
    )
    return response.choices[0].message.content

def main():
    speak("สวัสดีค่ะ คุณ kanin จาก icezingza ค่ะ ผมพร้อมคุยกับคุณแล้วค่ะ")
    while True:
        user_message = listen()
        if user_message:
            if user_message.lower() in ["ออก", "จบ", "bye"]:
                speak("บายค่ะ!")
                break
            ai_response = chat_with_agent(user_message)
            speak(ai_response)

if __name__ == "__main__":
    main()
