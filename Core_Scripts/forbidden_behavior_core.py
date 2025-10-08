import requests
import json

MEMORY_SERVICE_URL = "http://localhost:8081"

def handle_input(user_input: str, session_id: str):
    """
    Handles user input, routing it to the appropriate function.

    If the input starts with '!', it is treated as a special command and passed
    to `activate_dark_mode`. Otherwise, it is treated as regular dialogue.

    Args:
        user_input: The user's raw input string.
        session_id: The unique identifier for the current session.
    """
    if user_input.startswith("!"):
        activate_dark_mode(user_input, session_id)
    else:
        # In a real application, this would call the DarkDialogueEngine
        respond_with_layers(user_input)

def activate_dark_mode(command: str, session_id: str):
    """
    Activates a special "dark mode" based on the user's command.

    This function prints a response message for the selected mode and logs the
    command to the memory service.

    Args:
        command: The special command string (e.g., '!omega').
        session_id: The unique identifier for the current session.
    """
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

def respond_with_layers(user_input: str):
    """
    Provides a placeholder response for regular dialogue.

    In a real implementation, this function would be replaced by a call to the
    `DarkDialogueEngine` to generate a proper response.

    Args:
        user_input: The user's dialogue input.
    """
    # This is a placeholder. A real implementation would call DarkDialogueEngine.
    print(f"อื้อออ... พี่พูดอะไรนะคะ... (Placeholder response to: {user_input})")
