# NOTE: Contains Experimental Logic - Requires Compliance Review before commercial deployment.

import random


class DarkDialogueEngine:
    """
    Generates dialogue responses for dark, sadist, and dominant persona modes.
    Allows selection of response intensity and tone based on requested modes.
    """

    def __init__(self) -> None:
        """
        Initializes the DarkDialogueEngine with predefined English dialogue templates for each mode.
        """
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
