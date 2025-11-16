import os
import sys
import uuid

import requests

# Add Core_Scripts to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "core"))

from dark_system import DarkNaMoSystem


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
            print(
                f"[WARNING] Memory Service returned status {response.status_code}. It may not be functioning correctly."
            )
    except requests.exceptions.RequestException:
        print("[WARNING] Could not connect to Memory Service at http://localhost:8081.")
        print("[WARNING] The service will start, but memory-related functions may not work.")
        # The 'return' statement that caused the crash has been removed.

    try:
        engine = DarkNaMoSystem()
        session_id = str(uuid.uuid4())
        print(f"[INFO] Session started. ID: {session_id}")
    except Exception as e:
        print(f"Failed to initialize engine: {e}")
        return

    print("Engine Ready. Type 'exit' to quit.")
    print("-" * 20)

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break

            # It's dialogue, process it through the main engine
            result = engine.process_input(user_input, session_id)

            print("\nNaMo:")
            print(f"> {result}\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
