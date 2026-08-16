# NOTE: Contains Experimental Logic - Requires Compliance Review before commercial deployment.

import random
from typing import Any


class EmotionParasiteEngine:
    """
    Analyzes user inputs to evaluate emotional parasite metrics (arousal, corruption)
    and returns contextually appropriate responses based on the character's current mood.
    """

    def analyze_and_react(
        self, user_input: str, character_profile: Any
    ) -> tuple[str, dict[str, int]]:
        """
        Processes user input, updates the character profile status, and generates a response.

        Args:
            user_input: The text message sent by the user.
            character_profile: A dictionary or object representing the character's state.

        Returns:
            A tuple containing:
                - The response string (in English).
                - A dictionary indicating changes to 'corruption' and 'arousal'.
        """
        input_lower = user_input.lower()

        # Keyword mapping (supporting both Thai and English for backward compatibility)
        keywords_dominance = [
            "คำสั่ง",
            "สั่ง",
            "กราบ",
            "เลีย",
            "ทำตาม",
            "obey",
            "kneel",
            "command",
            "order",
            "lick",
        ]
        keywords_affection = [
            "รัก",
            "ชอบ",
            "ดีมาก",
            "เก่ง",
            "love",
            "good",
            "like",
            "great",
            "sweet",
        ]

        response = ""
        stat_changes = {"corruption": 0, "arousal": 0}

        # Handle different representation formats of the character profile
        if isinstance(character_profile, dict):
            mood = character_profile.get("mood", "Neutral")
            arousal = character_profile.get("arousal", 0.0)
        else:
            mood = getattr(character_profile, "mood", "Neutral")
            arousal_raw = getattr(character_profile, "arousal_level", 0.0)
            arousal = arousal_raw / 100.0 if arousal_raw > 1 else arousal_raw

        # Core logic branching based on character state
        if mood == "Horny" or arousal > 0.7:
            if any(word in input_lower for word in keywords_dominance):
                response = "Ahhh... Master... Command me more... I'm completely wet... 💦"
                stat_changes["arousal"] = 10
                stat_changes["corruption"] = 5
            else:
                response = (
                    "I don't care about anything else... I want it... Come inside me already! 🔥"
                )
                stat_changes["arousal"] = 5

        elif mood == "Obsessed":
            response = (
                f"You belong to me... Mine alone... Don't talk to anyone else... "
                f"{user_input}? Nonsense... Stay with me instead 🖤"
            )
            stat_changes["corruption"] = 10

        else:  # Neutral / Normal / Dark
            if any(word in input_lower for word in keywords_dominance):
                response = "Hmm... You think you can command the 'Queen'? Interesting... Why don't you try 👠"
                stat_changes["arousal"] = 5
            elif any(word in input_lower for word in keywords_affection):
                response = (
                    "So sweet-talker... Be careful or I might devour you without you realizing..."
                )
                stat_changes["corruption"] = 2
            else:
                options = [
                    "What's up, darling?",
                    "I'm waiting for a more exciting command...",
                    f"'{user_input}'? How boring... Make me excited.",
                ]
                response = random.choice(options)

        # Persist stats back to the profile if supported
        if hasattr(character_profile, "update_state"):
            character_profile.update_state(
                corruption_delta=stat_changes["corruption"], arousal_delta=stat_changes["arousal"]
            )

        return response, stat_changes


def analyze_and_react(user_input: str, character_profile: Any) -> tuple[str, dict[str, int]]:
    """
    Exposes a module-level helper function for backward compatibility with main.py.

    Args:
        user_input: The user's input text.
        character_profile: The character profile state.

    Returns:
        A tuple of (response string, stat changes).
    """
    engine = EmotionParasiteEngine()
    return engine.analyze_and_react(user_input, character_profile)
