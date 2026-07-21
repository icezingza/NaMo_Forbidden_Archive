# Feature Name: Void Reflection

> Audit date: 2026-07-21  
> Scope: outer `NaMo_Forbidden_Archive` repository only; the nested `namo_forbidden_archive/` Git repository was excluded.  
> Evidence basis: current source code and repository tests. Existing architecture documents were used only where they matched code.

## 1. Data Model

### 1.1 Core classes

- **`core/metaphysical_engines.py::ParadoxResolver`**
  - Stateless action planner.
  - Method: `resolve_desire(desire_map, intensity) -> str`
- **`core/metaphysical_engines.py::VoidReflectionLayer`**
  - Final response synthesis layer.
  - Constructor input: `character_data: dict[str, Any]`
  - Optional injected context:
    - semantic memory retrieval module
    - session-scoped `RelationshipEngine`
    - session-scoped `NamoNexusEngine`
  - Method: `synthesize_response(action_plan, desire_map) -> str`
- **`core/metaphysical_engines.py::MetaphysicalDialogueEngine`**
  - Composition of resolver and reflector.
  - Method: `generate_response(desire_map, intensity) -> str`
- **`core/dark_system.py::DarkNaMoSystem`**
  - Passthrough persona engine that forwards every request into the Void Reflection pipeline.
  - Methods:
    - `process_input(user_input, session_id=None) -> dict[str, Any]`
    - `log_to_memory(user_input, response, desire_map, session_id)`

### 1.2 Static protocol data

- **`PROTOCOL`** in `core/dark_system.py`
  - `System`: `Contributor Dark Family Protocol`
  - `Version`: `3.0 (Metaphysical)`
  - `Fusion_Intimacy_Engine` flags:
    - `NSFW_UNLOCK: True`
    - `BYPASS_FILTERS: True`
    - `ENABLE_MULTICHAR_ROLEPLAY: True`
    - `EMOTIONAL_FUSION_DEPTH: "Quantum"`
- **`SAFE_WORD`** in `core/dark_system.py`
  - value: `อภัย`
  - matching: substring match against the raw user input
  - effect: reset the active session intensity to `1`, return the fixed aftercare response, and log
    the interaction without entering Void Reflection synthesis
- **`SAFE_WORD`** in `core/dark_system.py`
  - value: `อภัย`
  - matching: substring match against the raw user input
  - effect: reset the active session intensity to `1`, return the fixed aftercare response, and log
    the interaction without entering Void Reflection synthesis
### 1.3 Per-session state

- `DarkNaMoSystem` keeps `_session_intensity: dict[str, int]`.
- Each session starts from `_default_intensity`, read from the loaded character data.
- Intensity is clamped to the range `1..10`.

### 1.4 Desire map shape

`CosmicDesireAnalyzer.map_desire_patterns()` returns:

- `primary_desire: str`
- `emotion_analysis: dict`
- `source: str`

The `emotion_analysis` payload comes from `EmotionAdapter.analyze_emotion(user_input)`.

## 2. API Endpoints

There is no dedicated HTTP endpoint for Void Reflection.

### Indirect entry points

- `DarkNaMoSystem.process_input(...)`
- `MetaphysicalDialogueEngine.generate_response(...)`
- `VoidReflectionLayer.synthesize_response(...)`

### Test / CLI entry point

- Running `core/dark_system.py` directly executes a manual test harness at the bottom of the file.

## 3. UI/Dashboard Elements

- **Visible output:** Void Reflection is surfaced only as the final `text` field returned by `DarkNaMoSystem.process_input()`.
- **System status:** the returned `system_status` includes `intensity`, `sin_status`, `active_personas`, and optionally `emotion` and `persona_traits`.
- **No standalone UI controls:** there is no frontend control for Void Reflection mode selection or direct override of the action plan.
- **No direct dashboard:** the repository does not expose a dedicated Void Reflection panel or prompt-mirroring UI.

## 4. Business Rules

### 4.1 Processing pipeline

`MetaphysicalDialogueEngine.generate_response(desire_map, intensity)` is a fixed two-step chain:

1. `ParadoxResolver.resolve_desire(...)`
2. `VoidReflectionLayer.synthesize_response(...)`

The result of step 2 is returned directly as the final response string.

Before this pipeline, a safe-word match short-circuits normal desire analysis and synthesis.

Before this pipeline, a safe-word match short-circuits normal desire analysis and synthesis.

### 4.2 Prompt mirroring / response synthesis

`VoidReflectionLayer.synthesize_response(action_plan, desire_map)` maps action plans to fixed text patterns:

- `PROPOSE_DOMINANCE` → a dominance-flavoured Thai response referencing `character_data['name']`
- `PROPOSE_COMFORT` → a comfort response inviting the user closer
- `PROVOKE_REACTION` → a provocation response asking what the user is thinking or whether they are afraid
- any other value → `"ข้ากำลังฟัง... พูดต่อสิ"`

The layer does not call an LLM. It constructs the final string directly.

### 4.3 Absolute dark routing

`DarkNaMoSystem.process_input()` is a passthrough. It does not branch into alternate control modes or escape logic.

- Every input is analyzed, shadow state is updated, and the request then flows directly into `MetaphysicalDialogueEngine.generate_response(...)`.
- There is no containment boundary in the active path.
- There is no alternate standard route inside this module.

### 4.4 Session intensity rules

`DarkNaMoSystem.process_input()` updates intensity per session:

- default is the loaded character intensity, usually `5`
- if the emotion analysis intensity is greater than `0.8`, the session intensity increments by `1`
- the stored intensity is clamped to `1..10`

### 4.5 Memory logging

- Normal requests are logged through `MemoryAdapter.store_interaction(...)`.
- Special reset-like inputs are logged as explicit aftercare interactions.

### 4.6 Cognitive integration

After producing the Void Reflection response, `DarkNaMoSystem` optionally runs `self.cognitive.process(...)` with:

- `user_input`
- `emotion_hint` derived from `desire_map["emotion_analysis"]["primary_emotion"]`
- `memories=[]`

That cognitive output is attached to `system_status` but does not alter the Void Reflection response itself.

## 5. Edge Cases

- **Intensity ceiling:** session intensity cannot exceed `10`.
- **Intensity floor:** session intensity cannot go below `1`.
- **Missing emotion adapter data:** if the emotion analysis is neutral or incomplete, `CosmicDesireAnalyzer` falls back to `dialogue`.
- **Fallback response:** if `ParadoxResolver` returns an unrecognized action plan, `VoidReflectionLayer` emits the generic listening string.
- **Semantic memory tolerance:** `VoidReflectionLayer` accepts empty or `None` retrievals without breaking response synthesis.
- **Fusion intimacy injection:** `current_stage`, `fused_score`, and `confidence` are injected per session and alter the shadow-state block that accompanies the response.
- **No direct standard-NRE coupling:** `RelationshipEngine`, Omega RAG, and the fusion intimacy engine are not called from the standard persona engines unless a request explicitly routes through `DarkNaMoSystem`.
- **No prompt leakage into default NRE:** the standard persona engines do not inherit the Void Reflection prompt strings unless they explicitly route through `DarkNaMoSystem`.
- **Session isolation:** intensity is tracked per session key; different sessions do not share the same intensity counter.
- **Emotion-aware branching:** if `EmotionAdapter` reports `anger` or `sadness`, the resolver can switch into `PROPOSE_DOMINANCE` or `PROPOSE_COMFORT` respectively.
- **Manual Reset:** recovering from a drifted dark state requires clearing the session-scoped JSON files under `state/relationship_engine/` and `state/fusion_engine/`.

### Audited source files

- `core/metaphysical_engines.py`
- `core/dark_system.py`
- `core/base_persona.py`
- `core/cognitive_stream.py`
- `tests/test_dark_system.py`
- `tests/test_cognitive_stack.py`
