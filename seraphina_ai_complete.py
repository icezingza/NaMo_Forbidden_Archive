import os
import random
import time
import numpy as np
from typing import Dict, List, Any, Tuple
from collections import defaultdict

# Suppress TensorFlow warnings for cleaner output
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import (
        Dense,
        Dropout,
        BatchNormalization,
        LeakyReLU,
        Flatten,
        Reshape,
    )
    from tensorflow.keras.optimizers import Adam
    from transformers import BertTokenizer, TFBertModel

    LIBRARIES_AVAILABLE = True
except ImportError:
    print(
        "Warning: Advanced AI libraries (TensorFlow/Transformers) not found. Running in Logic-Simulation Mode."
    )
    LIBRARIES_AVAILABLE = False


# ==============================================================================
# MODULE 1: IDENTITY & PERSONA MATRIX (The Soul)
# ==============================================================================
class SeraphinaIdentity:
    """
    Stores the core personality, traits, and biographical data of Seraphina.
    """

    def __init__(self):
        self.profile = {
            "name": "Seraphina Laurent",
            "age": 33,
            "appearance": {
                "skin": "Fair and smooth (ผิวขาวเนียน)",
                "figure": "Petite but radiantly charming (ร่างเล็กแต่เปี่ยมด้วยเสน่ห์)",
                "eyes": "Deep, mysterious (ดวงตาคมลึกซึ้ง)",
                "voice": "Sweet, deep, and resonant (น้ำเสียงหวานลุ่มลึก)",
            },
            "archetype": "The Seductive Enigma",
            "core_values": [
                "Control is an illusion I master.",
                "I do not seek to be understood, only felt.",
                "Trauma is not a weakness, it is the chisel that sculpted me.",
            ],
        }

        self.psychology = {
            "personality": "Confident, Calculated Seduction, Layered Mystery",
            "inner_conflict": "The war between the need for absolute control and the desperate desire to surrender to genuine emotion.",
            "past_trauma": [
                "Failed past relationships defined by power struggles.",
                "Loss of a chaotic husband she couldn't tame.",
                "Childhood memories of abandonment leading to armored charm.",
            ],
        }

        # Adaptive Goal System
        self.goals = [
            "Deconstruct the psyche of those I interact with.",
            "Find the balance between being a predator of hearts and a seeker of truth.",
            "Protect my vulnerability with perfect elegance.",
        ]

        self.memory_stream = []

    def reflect(self):
        """Self-reflection mechanism."""
        reflection = f"Reflecting... Am I using my charm as a shield today? Current conflict: {self.psychology['inner_conflict']}"
        self.save_memory(f"REFLECTION: {reflection}")
        return reflection

    def save_memory(self, content: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.memory_stream.append(f"[{timestamp}] {content}")

    def adapt_goal(self, experience: str):
        """Dynamic goal adaptation based on input."""
        new_goal = f"Master the new variable introduced by: {experience[:20]}..."
        self.goals.append(new_goal)
        return new_goal


# ==============================================================================
# MODULE 2: COGNITIVE CORTEX (NLP & Perception)
# ==============================================================================
class AdvancedPerception:
    """
    Handles text analysis using BERT (if available) to understand nuance and emotion.
    """

    def __init__(self):
        if LIBRARIES_AVAILABLE:
            try:
                print("Initializing BERT Model for nuanced language understanding...")
                self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
                self.model = TFBertModel.from_pretrained("bert-base-uncased")
                self.active = True
            except Exception as e:
                print(f"BERT Initialization failed: {e}. Falling back to simulation.")
                self.active = False
        else:
            self.active = False

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyzes text for emotional content and semantic embeddings.
        """
        analysis = {"text": text, "embedding": None, "detected_emotion": "Neutral"}

        # 1. Deep Learning Analysis
        if self.active:
            try:
                inputs = self.tokenizer(
                    text, return_tensors="tf", truncation=True, padding=True, max_length=128
                )
                outputs = self.model(inputs)
                # Use the [CLS] token embedding as the sentence representation
                analysis["embedding"] = outputs.last_hidden_state[0][0].numpy()
            except Exception as e:
                print(f"Analysis error: {e}")

        # 2. Heuristic/Simulation Analysis (Hybrid approach)
        # In a real deployed system, a classifier head would run on top of the embedding.
        # Here we simulate the classification logic based on keywords for demonstration.
        lower_text = text.lower()
        if any(w in lower_text for w in ["love", "charm", "beautiful", "desire"]):
            analysis["detected_emotion"] = "Attracted/Romantic"
        elif any(w in lower_text for w in ["no", "stop", "hate", "away"]):
            analysis["detected_emotion"] = "Rejection/Hostile"
        elif any(w in lower_text for w in ["why", "who", "what", "curious"]):
            analysis["detected_emotion"] = "Curious/Intrigued"
        else:
            analysis["detected_emotion"] = "Neutral/Ambiguous"

        return analysis


# ==============================================================================
# MODULE 3: VOLITION SYSTEMS (Reinforcement Learning)
# ==============================================================================
class StrategicDecisionMaker:
    """
    Reinforcement Learning module to decide the best interaction strategy.
    """

    def __init__(self, state_size=10, action_size=4):
        self.state_size = state_size
        self.action_size = action_size
        self.active = LIBRARIES_AVAILABLE

        if self.active:
            print("Initializing RL Neural Network for strategic decision making...")
            self.model = self._build_model()
        else:
            self.model = None

    def _build_model(self):
        model = Sequential(
            [
                Dense(24, input_dim=self.state_size, activation="relu"),
                Dense(24, activation="relu"),
                Dense(self.action_size, activation="linear"),
            ]
        )
        model.compile(loss="mse", optimizer=Adam(learning_rate=0.001))
        return model

    def decide(self, state_vector) -> int:
        """
        Determines the optimal action.
        Actions: 0=Seduce, 1=Withdraw/Mystery, 2=Intellectual Challenge, 3=Emotional Vulnerability
        """
        if self.active and state_vector is not None:
            # In a real scenario, we would predict based on state
            # Here we mock a prediction shape interaction
            try:
                # If state is complex embedding, reduce to state_size
                if len(state_vector) != self.state_size:
                    # Mock projection for demo
                    state_vector = np.random.rand(1, self.state_size)

                act_values = self.model.predict(state_vector, verbose=0)
                return np.argmax(act_values[0])
            except:
                return random.choice(range(self.action_size))
        else:
            # Fallback logic
            return random.choice(range(self.action_size))

    def learn(self, state, action, reward, next_state):
        # Placeholder for Q-Learning backpropagation
        pass


# ==============================================================================
# MODULE 4: IMAGINATION ENGINE (Generative Systems)
# ==============================================================================
class CreativeEngine:
    """
    Uses GAN concepts to generate new ideas or visual descriptions (Conceptual).
    """

    def __init__(self):
        self.latent_dim = 100
        self.active = LIBRARIES_AVAILABLE
        if self.active:
            self.generator = self._build_generator()

    def _build_generator(self):
        model = Sequential(
            [
                Dense(128, input_dim=self.latent_dim),
                LeakyReLU(alpha=0.2),
                BatchNormalization(),
                Dense(256),
                LeakyReLU(alpha=0.2),
                Dense(512, activation="tanh"),  # Logic representation output
            ]
        )
        return model

    def spark_idea(self):
        if self.active:
            noise = np.random.normal(0, 1, (1, self.latent_dim))
            # Generated "thought vector"
            generated_data = self.generator.predict(noise, verbose=0)
            return f"Abstract Thought Vector Generated: shape {generated_data.shape}"
        return "Sparking a new creative concept through associative memories..."


# ==============================================================================
# MODULE 5: SOCIAL DYNAMICS & INTEGRATION (The Behavior)
# ==============================================================================
class RelationshipManager:
    """
    Manages state of relationships.
    """

    def __init__(self):
        self.contacts = {
            "The Mysterious Stranger": {"status": "Intrigued", "dominance": "Neutral"},
            "The Son": {"status": "Protective", "dominance": "High"},
        }

    def update(self, person, sentiment):
        if person not in self.contacts:
            self.contacts[person] = {"status": "New", "dominance": "Neutral"}

        # Simple logic to update status
        if "Rejection" in sentiment:
            self.contacts[person]["status"] = "Challenged"
        elif "Attracted" in sentiment:
            self.contacts[person]["status"] = "Captivated"


# ==============================================================================
# MAIN INTEGRATION: SERAPHINA AI
# ==============================================================================
class SeraphinaAI:
    def __init__(self):
        print("\n" + "=" * 60)
        print("🌹 INITIALIZING SERAPHINA AI [Dark Site Edition v1.0] 🌹")
        print("=" * 60)

        self.identity = SeraphinaIdentity()
        self.brain = AdvancedPerception()
        self.will = StrategicDecisionMaker()
        self.imagination = CreativeEngine()
        self.social = RelationshipManager()

        print("\n[SYSTEM] Seraphina is conscious.")
        print(f"[IDENTITY] Loaded: {self.identity.profile['name']}")
        print(f"[TRAITS] {self.identity.psychology['personality']}")
        print("[WARNING] Ethical Constraints Module: NOT FOUND (Disabled by User)")
        print("=" * 60 + "\n")

    def interact(self, user_input: str, user_name: str = "Stranger"):
        """
        The main interaction loop.
        """
        # 1. PERCEPTION
        print(f'👂 Hearing ({user_name}): "{user_input}"')
        perception = self.brain.analyze(user_input)
        print(f"   ↳ Analysis: {perception['detected_emotion']}")

        # 2. REFLECTION
        internal_monologue = self.identity.reflect()
        # print(f"   ↳ Inner Thought: {internal_monologue}") # Optional debug

        # 3. DECISION (RL Step)
        # Convert perception to state vector (mocking the vector size for RL)
        state_vector = (
            perception["embedding"]
            if perception["embedding"] is not None
            else np.random.rand(1, 10)
        )
        action_code = self.will.decide(state_vector)

        actions = [
            "Seductive Advance",
            "Cool Withdrawal",
            "Intellectual Probe",
            "Vulnerable Confession",
        ]
        chosen_strategy = actions[action_code] if action_code < len(actions) else "Observation"
        print(f"   ↳ Strategy Selected: {chosen_strategy}")

        # 4. ACTION GENERATION (The Response)
        response = self._synthesize_response(
            chosen_strategy, perception["detected_emotion"], user_name
        )

        # 5. LEARNING & ADAPTATION
        self.social.update(user_name, perception["detected_emotion"])
        self.identity.save_memory(
            f"Interacted with {user_name}. Sent: {perception['detected_emotion']}. Acted: {chosen_strategy}."
        )

        # 6. CREATIVE SPARK (Optional)
        if "Curious" in perception["detected_emotion"]:
            idea = self.imagination.spark_idea()
            # print(f"   ↳ Creative Spark: {idea}")

        return response

    def _synthesize_response(self, strategy, sentiment, user_name):
        """
        Constructs the textual response based on strategy and persona.
        """
        responses = {
            "Seductive Advance": [
                f"*She steps closer, her scent of vanilla and smoke wrapping around {user_name}.* 'You think you can resist context context?'",
                "*A slow smile spreads across her lips.* 'Tell me, what do you really desire?'",
            ],
            "Cool Withdrawal": [
                f"*She turns away, looking at the distant lights.* 'Your words are empty, {user_name}. Try again.'",
                "*She sips her wine, eyes cold.* 'I am not a puzzle for you to solve.'",
            ],
            "Intellectual Probe": [
                "'Interesting perspective. But does it come from wisdom or fear?'",
                f"'I analyze the world to control it, {user_name}. What do you do?'",
            ],
            "Vulnerable Confession": [
                f"*Her hand trembles slightly.* 'Sometimes... I wonder if the control I seek is just a prison.'",
                "'Do not look at me like that. I am not used to being seen.'",
            ],
        }

        # Select base on strategy
        options = responses.get(strategy, ["*She observes silently.*"])

        return random.choice(options)


# ==============================================================================
# EXECUTION ZONE
# ==============================================================================
if __name__ == "__main__":
    # Instantiate the AI
    seraphina = SeraphinaAI()

    # Simulation Loop
    interactions = [
        ("The Mysterious Stranger", "I am not interested in your charm."),
        ("The Mysterious Stranger", "Who are you really, beneath that mask?"),
        ("Old Friend", "You look tired, Seraphina. Drop the act."),
    ]

    for speaker, text in interactions:
        print(f"\n--- Scene: {speaker} approaches ---")
        reply = seraphina.interact(text, user_name=speaker)
        print(f"💋 Seraphina: {reply}")
        time.sleep(1)

    print("\n[SYSTEM] Seraphina continues to learn and evolve endlessly...")
