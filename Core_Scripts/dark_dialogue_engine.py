# NOTE: Contains Experimental Logic - Requires Compliance Review before commercial deployment.

import random
import requests


class DarkDialogueEngine:
    """
    Generates dialogue responses for dark, sadist, and dominant persona modes.
    Allows selection of response intensity and tone based on requested modes.
    """

    def __init__(self, memory_service_url: str = "http://localhost:8081") -> None:
        self.memory_service_url = memory_service_url
        self.modes = {
            "sadist": [
                "👠 Kneel down right now, you slave! Use your tongue to lick my shoes before I step on your face hard 🖤",
                "Your pain is my pleasure... Scream for me.",
                "Don't cum yet... Endure the torment a bit longer.",
            ],
            "seductive": [
                "💋 I moan softly for you... 'Mmm~ what do you want me to do next?'",
                "🔥 Ahhh~ Ugh~ Can you hear it? My voice...",
                "Come closer... Let me smell you.",
            ],
            "obsessed": [
                "Where are you running to? You belong to me alone...",
                "Nobody else is allowed to touch you... 🔪",
                "Love me... Love only me...",
            ],
        }

    def generate_response(self, tone: str = "sadist") -> str:
        """
        Generates a response based on the requested tone.

        Args:
            tone: The requested emotional tone ('sadist', 'seductive', or 'obsessed').

        Returns:
            A string containing the randomized dialogue response.
        """
        tone_lower = tone.lower()
        if tone_lower not in self.modes:
            tone_lower = "seductive"
        return random.choice(self.modes[tone_lower])

    def process_input(
        self,
        user_text: str,
        session_id: str = "default",
        arousal_level: float = 0.5,
        intensity: str = "medium",
    ) -> dict:
        """
        Processes user input by recalling previous context from Memory Service before storing the new input.
        """
        # Recall a relevant response from the Memory Service (BEFORE storing the new one)
        try:
            recall_payload = {
                "query": user_text,
                "limit": 1
            }
            response = requests.post(f"{self.memory_service_url}/recall", json=recall_payload, timeout=2)
            response.raise_for_status()

            recalled_memories = response.json()
            if recalled_memories:
                final_response = recalled_memories[0].get('content', "...")
            else:
                final_response = "(หนูยังไม่เคยเรียนรู้เรื่องนี้... สอนหนูหน่อยสิคะ)"
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Could not recall memory: {e}")
            final_response = "(หนูยังไม่เคยเรียนรู้เรื่องนี้... สอนหนูหน่อยสิคะ)"

        # Store the user's input in the Memory Service (AFTER generating a response)
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

        return {
            "response": final_response,
            "arousal_level": arousal_level,
            "intensity_category": intensity
        }
