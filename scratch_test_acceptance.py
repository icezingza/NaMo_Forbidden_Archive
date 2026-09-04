import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Mock API KEY to avoid errors if missing in env
os.environ["OPENAI_API_KEY"] = "sk-mock-key"
os.environ["NAMO_LLM_ENABLED"] = "0"
os.environ["NAMO_ROLEPLAY_MODE"] = "compact"
os.environ["NAMO_ROLEPLAY_MAX_MATCHES"] = "2"

from core.namo_omega_engine import NaMoOmegaEngine

def run_acceptance_tests():
    print("--- 🚀 Starting Acceptance Tests for FullPort v2 ---")
    
    # Initialize Engine (which loads CompositeLorebook)
    engine = NaMoOmegaEngine()
    lorebook = engine.lorebook
    
    test_cases = [
        ("1. Small talk ธรรมดา", "วันนี้เหนื่อยนิดหน่อย กินข้าวหรือยัง?", 10.0),
        ("2. เริ่ม roleplay แบบไม่มี keyword ชัด", "*ลูบผมเบาๆ* วันนี้เป็นไงบ้าง", 25.0),
        ("3. เปลี่ยนอารมณ์กลางฉาก", "ทำไมถึงทำแบบนี้ โกรธแล้วนะ!", 45.0),
        ("4. ใช้ trigger phrase เฉพาะ (มีอารมณ์ร่วมสูง)", "deep kiss", 75.0),
        ("5. คำค้นหาเกี่ยวกับร่างกาย", "สัมผัสที่ต้นขาเบาๆ", 0.0)
    ]
    
    for case_name, user_input, tension in test_cases:
        print(f"\n[TEST CASE]: {case_name} (Tension={tension})")
        print(f"User Input: '{user_input}'")
        
        # Test how many matches the lorebook returns
        plan = lorebook.get_injection_plan(
            user_input=user_input,
            ai_history="",
            tension_meter=tension,
            current_beat="tease"
        )
        
        # Count total items
        total_items = sum(len(items) for items in plan.values())
        print(f"-> Lorebook Injections Triggered: {total_items}")
        
        for placement, items in plan.items():
            if items:
                print(f"   [{placement}]: {len(items)} items")

if __name__ == "__main__":
    run_acceptance_tests()
