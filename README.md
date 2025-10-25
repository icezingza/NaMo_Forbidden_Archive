# NaMo Forbidden Archive

The NaMo Forbidden Archive is a sophisticated dialogue system designed to explore complex emotional and thematic interactions. It features a unique "arousal detection" mechanic, a persistent memory service, and a set of special "dark modes" that alter the nature of the conversation. This project serves as a framework for building advanced, context-aware conversational AI.

## 🎯 Purpose and Goals

The primary goal of this project is to provide a robust and extensible framework for creating nuanced and emotionally intelligent conversational AI. It is designed to be a tool for developers and researchers who are interested in exploring the boundaries of human-computer interaction.

The key objectives of the project are:

*   **To create a flexible and modular architecture**: The project is designed to be easily extensible, allowing developers to add new features and functionality with minimal effort.
*   **To explore the use of emotional intelligence in conversational AI**: The project includes a unique "arousal detection" mechanic that allows the AI to adapt its responses based on the user's emotional state.
*   **To provide a persistent memory service**: The project includes a standalone FastAPI service that allows the AI to store and retrieve conversation history, enabling it to maintain long-term context.
*   **To explore the use of "dark modes" in conversational AI**: The project includes a set of special "dark modes" that can be activated with commands, allowing the AI to shift the conversational theme and explore more complex and challenging topics.

## ✨ Features

- **Integrated Dialogue Engine**: A core engine that processes user input, manages session state, and generates responses.
- **Arousal Detection**: A simplified model for analyzing text to gauge emotional intensity and adapt responses accordingly.
- **Persistent Memory**: A standalone FastAPI service (`memory_service.py`) that stores and retrieves conversation history, allowing for long-term context.
- **Special Command Modes**: A set of "dark modes" that can be activated with commands (e.g., `!omega`, `!parasite`) to shift the conversational theme.
- **Thematic Re-mapping**: A system for translating conceptual tags into a "dark erotic" framework.
- **Dual-Mode Operation**: Can be run in an all-in-one integrated mode (`app.py`) or as separate components (running `memory_service.py` as a background service).

## 🗺️ Architecture

The project is composed of three main parts:

- **`app.py` (Integrated Mode)**: The main entry point for running the application as a single, interactive console program. It initializes the `DarkDialogueEngine` and connects to the `memory_service`.
- **`memory_service.py` (Memory Service)**: A standalone FastAPI application that provides a REST API for storing and recalling memories. It uses a JSON file (`memory_protocol.json`) for persistence.
- **`Core_Scripts/` (Core Logic)**: This directory contains the essential modules of the application:
    - `dark_dialogue_engine.py`: Orchestrates the main dialogue flow, integrating arousal detection and memory.
    - `arousal_detector.py`: Analyzes user input to determine an "arousal" score.
    - `forbidden_behavior_core.py`: Handles the special command modes.

## 🚀 Quickstart

### 1. Prerequisites

- Python 3.11+
- `pip` for package management

### 2. Installation

Clone the repository and install the required dependencies:

```bash
# Clone the repository (if you haven't already)
git clone <repository-url>
cd <repository-directory>

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Running the Application

You can run the application in two ways:

#### Option A: Integrated Mode

This is the simplest way to run the application. First, start the memory service in the background, then run the main application.

**Step 1: Start the Memory Service**

Open a terminal and run the following command:

```bash
uvicorn memory_service:app --host 0.0.0.0 --port 8081
```

**Step 2: Run the Main App**

Open a *second* terminal, activate the virtual environment, and run:

```bash
python app.py
```

You can now interact with the dialogue system in the console.

#### Option B: Standalone Components

This approach is for development and demonstrates the service-oriented architecture. The `memory_service.py` can be run independently and accessed via its API.

- **To run the memory service:**
  ```bash
  uvicorn memory_service:app --host 0.0.0.0 --port 8081 --reload
  ```
- You can then interact with the service's API endpoints using tools like `curl` or Postman.

## ⚙️ Memory Service API

The memory service runs on `http://localhost:8081` by default and exposes the following endpoints:

- **`POST /store`**: Stores a new memory record.
  - **Body**: A JSON object with `content`, `type`, `session_id`, etc.
- **`POST /recall`**: Recalls memory records based on a query.
  - **Body**: A JSON object with a `query` string and other filters.
- **`GET /health`**: A health check endpoint that returns the service status and record count.

## 🔮 Dark Modes

The application includes several "dark modes" that can be activated with special commands. These modes change the theme of the interaction and are logged as special events in the memory service.

| Command       | Mode Description                                                 |
|---------------|------------------------------------------------------------------|
| `!omega`      | Enters Forbidden Omega Mode.                                     |
| `!parasite`   | Activates Emotion Parasite mode.                                 |
| `!astral`     | Engages Astral Plane Degradation.                                |
| `!sadist`     | Activates Merciless Sadist Mode.                                 |
| `!gentle`     | Enters Soft Domination Mode.                                     |
| `!loop`       | Initiates an Infinite Pleasure Loop.                             |
| `!multiverse` | Initiates a Multiverse Orgy.                                     |
| `!mindbreak`  | Engages the Mindbreak protocol.                                  |

## 🧪 Tests

To run the test suite, use `pytest`:

```bash
pytest
```

## 🤝 Contributing

Please read `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` before contributing. Ensure you have pre-commit hooks installed (`pre-commit install`) to maintain code quality.