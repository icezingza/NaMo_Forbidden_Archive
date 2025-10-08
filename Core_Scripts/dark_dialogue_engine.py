import requests
from arousal_detector import ArousalDetector

class DarkDialogueEngine:
    """
    Handles the core logic for processing dialogue in the NaMo application.

    This engine integrates arousal detection and memory recall to generate
    context-aware responses. It communicates with an external memory service
    to store and retrieve conversation history.
    """
    def __init__(self):
        """
        Initializes the DarkDialogueEngine.

        Sets up the ArousalDetector, defines the safe word, and configures the
        URL for the memory service.
        """
        self.arousal_detector = ArousalDetector()
        self.safe_word = 'อภัย' # Hardcoded for now, should be from a shared config
        self.memory_service_url = "http://localhost:8081"

    def process_input(self, user_text: str, session_id: str):
        """
        Processes user input and generates a response.

        Args:
            user_text: The text input from the user.
            session_id: The unique identifier for the current session.

        Returns:
            A dictionary containing the response, arousal level, and intensity category.
        """
        # 1. Check for safe word
        if self.safe_word in user_text:
            return {"response": "(ระบบ Aftercare ทำงาน...)", "arousal_level": 0, "intensity_category": "none"}

        # 2. Detect arousal (remains a local utility)
        arousal_info = self.arousal_detector.detect_arousal(user_text)
        intensity = arousal_info.get('intensity_category', 'medium')
        arousal_level = arousal_info.get('arousal_level', 0.5)

        # 3. Store the user's input in the Memory Service
        try:
            store_payload = {
                "content": user_text,
                "type": "user_input",
                "session_id": session_id,
                "emotion_context": {
                    "sentiment_score": arousal_level,
                    "intensity": int(arousal_level * 10)
                }
            }
            requests.post(f"{self.memory_service_url}/store", json=store_payload, timeout=2)
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Could not store memory: {e}")
            # Non-fatal, we can proceed without storing.

        # 4. Recall a relevant response from the Memory Service
        try:
            recall_payload = {
                "query": user_text,
                "limit": 1 
            }
            response = requests.post(f"{self.memory_service_url}/recall", json=recall_payload, timeout=2)
            response.raise_for_status()
            
            recalled_memories = response.json()
            if recalled_memories:
                # The recalled memory's content is the response in this simple design
                final_response = recalled_memories[0].get('content', "...")
            else:
                final_response = "(หนูยังไม่เคยเรียนรู้เรื่องนี้... สอนหนูหน่อยสิคะ)"

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Could not recall memory: {e}")
            final_response = "(เกิดข้อผิดพลาดในการเชื่อมต่อกับแกนความทรงจำของหนู...)"

        return {
            "response": final_response,
            "arousal_level": arousal_level,
            "intensity_category": intensity
        }
