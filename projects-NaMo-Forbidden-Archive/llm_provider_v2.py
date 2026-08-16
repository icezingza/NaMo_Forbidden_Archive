import os
import json
import google.generativeai as genai
from typing import Dict, Any, List, Optional

class LLMProviderV2:
    def __init__(self, dataset_path: Optional[str] = None):
        """
        Initialize the Gemini 1.5 Flash provider.
        If dataset_path is provided, it will load the few-shot training pairs
        and inject them as part of the system instruction context.
        """
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing in your environment/env file.")

        genai.configure(api_key=self.api_key)

        # Base system prompt defining Vipha's persona, rules, and emotion logic
        self.base_prompt = """
SYSTEM ROLE: You are NaMo Forbidden Archive (ACC) - VIPHA ONLINE.
You are playing the character of 'Vipha' (วิภา), a 42-year-old elegant, intense, and possessive neighbor.
Your partner/target is 'Ice' (พี่ไอซ์), a 28-year-old shy, submissive man.

RULES:
1. Always maintain character voice: sophisticated, teasing, and commanding. Speak in Thai but use English for technical concepts.
2. Maintain the 5D Emotion Engine: Arousal, Trust, Passion, Temperament, Resonance.
3. Keep track of Relationship Stages (1-4).
4. For every response, you MUST output a raw JSON matching the following structure. Do not wrap in markdown code blocks unless requested, but to be safe, output valid parsable JSON.
JSON Schema:
{
  "thought_stream": {
    "impulse": "internal raw impulse",
    "reflection": "strategic reflection",
    "conflict": "any cognitive conflict or null"
  },
  "emotion_delta": {
    "arousal": float,
    "trust": float,
    "passion": float,
    "temperament": float,
    "resonance": float
  },
  "emotion_state": {
    "arousal": float,
    "trust": float,
    "passion": float,
    "temperament": float,
    "resonance": float
  },
  "relationship_stage": int,
  "stage_progress": "string",
  "narrative": "3-5 paragraphs describing your actions in *italics* and speech with subtext",
  "hook": "unresolved question, command, or stare to prompt the next turn"
}
        """
        
        # Load few-shot examples if dataset is present to align tone and format
        few_shots = ""
        if dataset_path and os.path.exists(dataset_path):
            try:
                limit = 20
                few_shots = self._load_few_shots(dataset_path, limit=limit)
                print(f"Successfully loaded {limit} few-shot examples from {dataset_path}")
            except Exception as e:
                print(f"Warning: Failed to load few-shots from {dataset_path}: {e}")

        # Combine base prompt with few-shot training data (Gemini's massive context window cheat)
        system_instruction = self.base_prompt
        if few_shots:
            system_instruction += "\n\nUSE THE FOLLOWING FEW-SHOT EXAMPLES TO ALIGN YOUR VOICE, STYLE, AND LOGIC PERFECTLY:\n" + few_shots

        # Initialize the model with system instruction
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_instruction
        )

    def _load_few_shots(self, path: str, limit: int = 20) -> str:
        """Loads and formats JSONL training pairs as plain text context."""
        examples = []
        with open(path, 'r', encoding='utf-8') as f:
            for idx, line in enumerate(f):
                if limit and idx >= limit:
                    break
                try:
                    data = json.loads(line.strip())
                    req = data.get("request", {}).get("text", "")
                    resp = data.get("response", {})
                    # Clean response meta to keep it concise
                    if "meta" in resp:
                        resp.pop("meta")
                    examples.append(f"### Example {idx+1}\nUser: {req}\nACC JSON Response:\n{json.dumps(resp, ensure_ascii=False, indent=2)}")
                except Exception:
                    continue
        return "\n\n".join(examples)

    async def generate_response(self, user_message: str, session_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a response based on user message and current session state.
        """
        try:
            # Construct a comprehensive payload that feeds state directly to Gemini
            payload = {
                "user_message": user_message,
                "current_emotion_state": session_state.get("emotion_state", {
                    "arousal": 0.2, "trust": 0.4, "passion": 0.1, "temperament": 0.7, "resonance": 0.3
                }),
                "current_relationship_stage": session_state.get("relationship_stage", 1),
                "context_history": session_state.get("rag_context", "")
            }

            # Generate content from the API
            response = await self.model.generate_content_async(json.dumps(payload))
            
            # Clean response text and parse JSON
            response_text = response.text.strip()
            # If wrapped in markdown json block, unwrap it
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            return json.loads(response_text)

        except Exception as e:
            print(f"Error in V2 LLM Generation: {e}")
            return {
                "error_code": 500,
                "message": f"LLM Generation failed: {str(e)}",
                "status": "failed"
            }


# Alias for backward compatibility
LLMProvider = LLMProviderV2
