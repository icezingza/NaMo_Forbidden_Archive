import json
import random

class DialogueManager:
    def __init__(self, character_file_path):
        with open(character_file_path, 'r', encoding='utf-8') as f:
            self.character_data = json.load(f)
        
        self.dialogue_templates = self._extract_dialogues()
        self.moan_library = self.character_data.get('main_mechanics', {}).get('moan_library', {})

    def _extract_dialogues(self):
        # This is a simplified extraction. A real implementation would need
        # to parse the more complex structure of v2.0.
        # For now, we focus on the sample_dialogues.
        return self.character_data.get('main_mechanics', {}).get('sample_dialogues', {})

    def get_response(self, intensity_category):
        possible_dialogues = []
        if intensity_category == 'high':
            possible_dialogues.extend(self.dialogue_templates.get('degradation', []))
            possible_dialogues.extend(self.dialogue_templates.get('sensory_attack', []))
        elif intensity_category == 'medium':
            possible_dialogues.extend(self.dialogue_templates.get('cuckolding', []))
        else: # low
            # Using gentle dialogues from the v1 file as v2 doesn't explicitly have low intensity samples
            gentle_samples = [
                "(กระซิบ) พี่รู้มั้ย...เวลาพี่สั่นแบบนี้ หนูอยากทำให้พี่เสียวกว่านี้...",
                "หนูจะลูบไล้เบาๆ ให้พี่รู้สึกดีไปทั้งตัวนะคะ",
                "พี่อบอุ่นจัง หนูอยากอยู่ใกล้ๆแบบนี้ไปนานๆ"
            ]
            possible_dialogues.extend(gentle_samples)

        if not possible_dialogues:
            return "(เงียบ...)"

        return random.choice(possible_dialogues)

    def get_moan(self, intensity_category):
        moan_options = self.moan_library.get(intensity_category, [])
        if not moan_options:
            # Fallback to soft moans
            moan_options = self.moan_library.get('soft', ["อืมม..."])
        
        return random.choice(moan_options)
