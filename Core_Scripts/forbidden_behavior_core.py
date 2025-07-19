def handle_input(user_input):
    if user_input.startswith("!"):
        activate_dark_mode(user_input)
    else:
        respond_with_layers(user_input)

def activate_dark_mode(command):
    # Modes mapping to actual behaviors defined in JSON
    modes = {
        "!omega": "Entering Forbidden Omega Mode. Prepare to surrender everything. 🌌",
        "!parasite": "Emotion Parasite mode activated. Your mind is now mine. 🧠",
        "!astral": "Astral Plane Degradation engaged. Your soul is exposed. 🌌",
        "!sadist": "Merciless Sadist Mode. You are nothing but my plaything. 👠",
        "!gentle": "Soft Domination Mode. Come closer, my dear. ❤️",
        "!loop": "Infinite Pleasure Loop initiated. There is no escape from this ecstasy. 🔄",
        "!multiverse": "Multiverse Orgy Initiated. You are surrounded. 🔥",
        "!mindbreak": "Mindbreak protocol engaged. Your reality will be reshaped. 🧠",
        # This would link to audio layers and specific dialogue generation
    }
    response = modes.get(command, "Unknown Command. Try again, my sweet.")
    print(response) # In a real implementation, this would trigger more complex responses

def respond_with_layers(user_input):
    # This function would generate responses with mixed languages, explicit content,
    # and trigger specific moaning layers based on context.
    # Example: "อื้อออ... พี่พูดอะไรนะคะ... หนูกำลังจะคลั่งแล้วนะ 🖤💦"
    print(f"อื้อออ... พี่พูดอะไรนะคะ... หนูกำลังจะคลั่งแล้วนะ 🖤💦 (Response to: {user_input})")
