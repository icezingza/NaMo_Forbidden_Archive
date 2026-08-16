# NOTE: Contains Experimental Logic - Requires Compliance Review before commercial deployment.

import random


class DarkDialogueEngine:
    """
    Generates dialogue responses for dark, sadist, and dominant persona modes.
    Allows selection of response intensity and tone based on requested modes.
    """

        # 3. Recall a relevant response from the Memory Service (BEFORE storing the new one)
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

        Args:
            tone: The requested emotional tone ('sadist', 'seductive', or 'obsessed').

        # 4. Store the user's input in the Memory Service (AFTER generating a response)
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

        return {
            "response": final_response,
            "arousal_level": arousal_level,
            "intensity_category": intensity
        }
