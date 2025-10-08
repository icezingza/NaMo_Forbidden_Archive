import os
import sys
import uuid
import requests

# Add Core_Scripts to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Core_Scripts'))

from dark_dialogue_engine import DarkDialogueEngine
from forbidden_behavior_core import handle_input as handle_command

def main():
    """
    Runs the NaMo Forbidden Arch application in integrated mode.

    This function initializes the dialogue engine, checks the connection to the
    memory service, and enters a loop to process user input. It handles both
    regular dialogue and special commands (prefixed with '!'). The session is
    managed with a unique session ID.
    """
    print("--- NaMo Forbidden Arch (Integrated Mode) ---")
    
    # Health check for Memory Service
    try:
        response = requests.get("http://localhost:8081/health", timeout=2)
        if response.status_code == 200:
            print("[INFO] Memory Service is connected.")
        else:
            print(f"[WARNING] Memory Service returned status {response.status_code}. It may not be functioning correctly.")
    except requests.exceptions.RequestException:
        print("[FATAL] Could not connect to Memory Service at http://localhost:8081.")
        print("Please ensure the memory_service.py is running in the background.")
        return

    try:
        engine = DarkDialogueEngine()
        session_id = str(uuid.uuid4())
        print(f"[INFO] Session started. ID: {session_id}")
    except Exception as e:
        print(f"Failed to initialize engine: {e}")
        return

    print(f"Engine Ready. Type 'exit' to quit.")
    print(f"Safe word is: {engine.safe_word}")
    print("-" * 20)

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                break
            
            if user_input.startswith("!"):
                # It's a command, let the command handler process it
                handle_command(user_input, session_id)
                # The handler prints its own response, so we just continue
                continue

            # It's dialogue, process it through the main engine
            result = engine.process_input(user_input, session_id)
            
            print("\nNaMo:")
            print(f"> {result.get('response', '(No response)')}")
            print(f"[Debug: Arousal={result.get('arousal_level', 0):.2f}, Intensity='{result.get('intensity_category', 'N/A')}']\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()