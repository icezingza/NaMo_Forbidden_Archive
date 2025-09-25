import json

class ArousalDetector:
    def __init__(self):
        self.base_intensity = 0.5
        self.adaptation_rate = 0.1

    def analyze_text_intensity(self, text):
        # Placeholder for a more sophisticated text analysis model
        # For now, we'll do a simple keyword-based analysis
        intensity_score = 0
        low_intensity_words = ['อ่อนโยน', 'เบาๆ']
        medium_intensity_words = ['ร้อนแรง', 'มากขึ้น']
        high_intensity_words = ['รุนแรง', 'สุดๆ', 'ทนไม่ไหว']

        if any(word in text for word in high_intensity_words):
            intensity_score = 0.8
        elif any(word in text for word in medium_intensity_words):
            intensity_score = 0.5
        elif any(word in text for word in low_intensity_words):
            intensity_score = 0.2
            
        return intensity_score

    def detect_arousal(self, user_input, historical_patterns=None):
        # In a real implementation, user_input would be a complex object
        # containing text, audio, and metadata.
        # For now, we assume user_input is just a text string.
        
        textual_arousal = self.analyze_text_intensity(user_input)
        
        # Placeholders for audio and behavioral analysis
        vocal_arousal = 0  # Placeholder: self.analyze_vocal_patterns(user_input.audio)
        behavioral_arousal = 0 # Placeholder: self.analyze_interaction_patterns(user_input.metadata)

        # Placeholder for temporal weighting
        temporal_weight = 1 # Placeholder: self.calculate_temporal_decay(historical_patterns)

        # Composite arousal score (0.0 - 1.0)
        composite_arousal = (
            textual_arousal * 0.6 +  # Increased weight for text in this simplified version
            vocal_arousal * 0.25 +
            behavioral_arousal * 0.15
        ) * temporal_weight
        
        # Simple categorization
        intensity_category = "low"
        if composite_arousal >= 0.7:
            intensity_category = "high"
        elif composite_arousal >= 0.3:
            intensity_category = "medium"

        return {
            "arousal_level": composite_arousal,
            "intensity_category": intensity_category,
        }
