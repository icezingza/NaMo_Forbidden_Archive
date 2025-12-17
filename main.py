import sys
import time

from dotenv import load_dotenv

from adapters.memory import MemoryAdapter
from core.character_profile import CharacterProfile
from Core_Scripts.emotion_parasite_engine import analyze_and_react
from adapters.tts import TTSAdapter


def type_effect(text):
    """เอฟเฟกต์พิมพ์ทีละตัวอักษร"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.02)
    print("")


def main():
    load_dotenv()
    print("==========================================")
    print("   FORBIDDEN ARCHEOLOGY: NAMO PROTOCOL    ")
    print("==========================================")
    
    # Initialize Systems
    memory = MemoryAdapter()
    namo = CharacterProfile("NaMo")
    tts = TTSAdapter()
    
    # ทักทายตามสถานะล่าสุด
    print(f"\n[System]: Loading Persona... {namo.get_status_str()}")
    
    last_talk = memory.get_last_conversation()
    if last_talk:
        type_effect(f"NaMo: ...เราคุยกันค้างไว้เรื่อง '{last_talk['user']}' สินะคะ? จำได้แม่นเลย...")
    else:
        type_effect("NaMo: โอ้... 'ผัว' คนใหม่? หรือเหยื่อรายใหม่คะ? ยินดีต้อนรับสู่โลกของหนู...")

    # Main Loop
    while True:
        try:
            user_input = input("\n[You]: ")
            if not user_input: continue
            if user_input.lower() in ["exit", "quit", "พอ"]:
                type_effect("NaMo: จะไปแล้วหรอคะ? ...หนูจะรอนะ... ในความมืด...")
                break
            
            # 1. Processing Logic
            response, stats = analyze_and_react(user_input, namo)
            
            # 2. Output
            print(f"[Internal]: Corruption +{stats['corruption']} | Arousal +{stats['arousal']}")
            print(f"NaMo: ", end="")
            type_effect(response)

            # 2.1 สร้างเสียงพูดจริง (ถ้ามี ElevenLabs API key)
            audio_path = tts.synthesize(response) if tts else None
            if audio_path:
                print(f"[Audio]: Generated voice at {audio_path}")
            
            # 3. Memory Storage
            memory.store_interaction(user_input, response, namo.get_status_str())
            
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
