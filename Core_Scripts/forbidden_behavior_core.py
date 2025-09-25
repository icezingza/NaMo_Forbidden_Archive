import requests
import json

MEMORY_SERVICE_URL = "http://localhost:8081"

def handle_input(user_input: str, session_id: str):
    if user_input.startswith("!"):
        activate_dark_mode(user_input, session_id)
    else:
        # In a real application, this would call the DarkDialogueEngine
        respond_with_layers(user_input)

def activate_dark_mode(command: str, session_id: str):
    modes = {
        "!omega": "Entering Forbidden Omega Mode. Prepare to surrender everything. 🌌",
        "!parasite": "Emotion Parasite mode activated. Your mind is now mine. 🧠",
        "!astral": "Astral Plane Degradation engaged. Your soul is exposed. 🌌",
        "!sadist": "Merciless Sadist Mode. You are nothing but my plaything. 👠",
        "!gentle": "Soft Domination Mode. Come closer, my dear. ❤️",
        "!loop": "Infinite Pleasure Loop initiated. There is no escape from this ecstasy. 🔄",
        "!multiverse": "Multiverse Orgy Initiated. You are surrounded. 🔥",
        "!mindbreak": "Mindbreak protocol engaged. Your reality will be reshaped. 🧠",
    }
    response = modes.get(command, "Unknown Command. Try again, my sweet.")
    print(response) # Print immediate feedback to user

    # Log the command to the memory service
    try:
        store_payload = {
            "content": command,
            "type": "special_command",
            "session_id": session_id,
            "emotion_context": {
                "emotion_type": "command_issued"
            }
        }
        requests.post(f"{MEMORY_SERVICE_URL}/store", json=store_payload, timeout=2)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not log command to memory service: {e}")

def respond_with_layers(user_input):
    # This is a placeholder. A real implementation would call DarkDialogueEngine.
    print(f"อื้อออ... พี่พูดอะไรนะคะ... (Placeholder response to: {user_input})")
