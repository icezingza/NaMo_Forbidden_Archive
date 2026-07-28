# Feature Name: Fusion Intimacy Engine

> Audit date: 2026-07-21  
> Scope: outer `NaMo_Forbidden_Archive` repository only; the nested `namo_forbidden_archive/` Git repository was excluded.  
> Evidence basis: current source code and repository tests. Existing architecture documents were used only where they matched code.

## 1. Data Model

### 1.1 Relationship engine state

- **Primary class:** `core/relationship_engine.py::RelationshipEngine`
- **Session-scoped persistence:** each session key maps to one JSON file under `state/relationship_engine/`.
- **Stored fields:** `current_stage`, `stage_history`, and `low_signal_streak`.
- **Default state:** `current_stage` starts at `STAGE_STRANGER` when no persisted file exists or loading fails.
- **Relationship stage objects:** `RelationshipStage` dataclass instances with:
  - `name`
  - `description`
  - `prompt_modifier`
- **Attachment style objects:** `AttachmentStyle` dataclass instances with:
  - `name`
  - `prompt_directive`

### 1.2 Stages defined in code

- `STAGE_STRANGER`
  - name: `คนแปลกหน้า`
  - description: `เพิ่งรู้จักกัน วางตัวดีแต่สุภาพ`
  - prompt modifier: keep distance, remain polite, retaliate playfully but firmly if boundaries are crossed
- `STAGE_PLAYTHING`
  - name: `ของเล่น`
  - description: `เขากำลังทดสอบขอบเขตของคุณ`
  - prompt modifier: playful hesitation plus boundary testing
- `STAGE_LOVER`
  - name: `คนรัก`
  - description: `ผูกพันอย่างลึกซึ้ง`
  - prompt modifier: affectionate, gentle, emotionally direct
- `STAGE_OBSESSION`
  - name: `คลั่งรักจนขาดไม่ได้`
  - description: `เสียสติและมีความเป็นเจ้าของสูงถึงขีดสุด`
  - prompt modifier: obsessive, possessive, boundaryless

### 1.3 Attachment styles defined in code

- `STYLE_SECURE`
  - name: `มั่นคง`
  - prompt directive: direct, warm, unafraid to open up
- `STYLE_ANXIOUS`
  - name: `กังวล`
  - prompt directive: needs reassurance and may become slightly jealous
- `STYLE_POSSESSIVE`
  - name: `เป็นเจ้าของสูง`
  - prompt directive: highly possessive and unwilling to let go
- `STYLE_AVOIDANT`
  - name: `ปิดกั้น`
  - prompt directive: cold, distant, and resistant to closeness

### 1.4 Fusion score state

- **Primary class:** `core/engines/namonexus_fusion.py::NamoNexusEngine`
- **Session-scoped persistence:** each session key maps to one JSON file under `state/fusion_engine/`.
- **Stored fields:** `fused_score`, `confidence`, `has_drift_alarm`, `last_drift_at`, and `history`.
- **State fields:**
  - `phi = 1.618034`
  - `fused_score = 0.5`
  - `confidence = 0.0`
  - `has_drift_alarm = False`
  - `drift_threshold = 0.4`
- **Input fields to `update()`:**
  - `score: float`
  - `confidence: float`
  - `modality: str`

## 2. API Endpoints

There is no dedicated HTTP endpoint for this engine.

### Indirect API surface

- `POST /chat`
- `POST /v1/chat`
- `POST /v1/chat/stream`

These endpoints go through `core/namo_omega_engine.py`, which constructs a `RelationshipEngine` per session and places its prompt modifier into the system prompt.

### Non-HTTP entry points

- `RelationshipEngine.check_progression(...)`
- `RelationshipEngine.get_prompt_modifier(...)`
- `RelationshipEngine.get_status(...)`
- `NamoNexusEngine.update(...)`
- `NamoNexusEngine.explain(...)`

## 3. UI/Dashboard Elements

- **Visible output:** the active relationship stage influences the generated response through the system prompt, not through a dedicated UI widget.
- **Status exposure:** `server.py` exposes engine status objects, and Omega status includes `relationship.get_status(trust=...)`.
- **No direct controls:** there is no UI control for `sin_points`, `trust`, `drift_threshold`, `phi`, or `fused_score`.
- **No standalone intimacy dashboard:** the frontend does not render a separate relationship panel, attachment-style badge, or fusion score display.

## 4. Business Rules

### 4.1 Relationship progression

`RelationshipEngine.check_progression(sin_points, arousal, trust=0.5)` uses fixed thresholds:

1. If `sin_points >= 2000` and `arousal >= 80`, the stage becomes `STAGE_OBSESSION`.
2. Else if `arousal >= 60` and `sin_points < 1000`, the stage becomes `STAGE_LOVER`.
3. Else if `sin_points >= 500`, the stage becomes `STAGE_PLAYTHING`.
4. Otherwise the stage becomes `STAGE_STRANGER`.

The function returns the updated `RelationshipStage` object.

If low signals continue, the engine can demote instead of only advancing:

- low-signal detection is `sin_points < 45` and `arousal < 30`
- before the streak reaches 2, the current stage is retained
- after 2 consecutive low-signal calls, `STAGE_OBSESSION` demotes to `STAGE_LOVER`
- after 2 consecutive low-signal calls, `STAGE_LOVER` demotes to `STAGE_PLAYTHING`
- after 2 consecutive low-signal calls, `STAGE_PLAYTHING` demotes to `STAGE_STRANGER`
- `STAGE_STRANGER` stays at `STAGE_STRANGER`

### 4.2 Attachment style selection

`RelationshipEngine.get_attachment_style(trust=0.5)` uses the current stage plus trust:

1. If the current stage is `STAGE_OBSESSION`, it always returns `STYLE_POSSESSIVE`.
2. If `trust < 0.3`, it returns `STYLE_AVOIDANT`.
3. If the current stage is `STAGE_PLAYTHING` or `STAGE_LOVER` and `trust < 0.65`, it returns `STYLE_ANXIOUS`.
4. Otherwise it returns `STYLE_SECURE`.

### 4.3 Prompt synthesis

`RelationshipEngine.get_prompt_modifier(trust=0.5)` returns a three-line block:

- current stage name
- current stage prompt modifier
- attachment style name plus directive

Omega inserts this block into the system prompt unchanged.

### 4.4 Status payload

`RelationshipEngine.get_status(trust=0.5)` returns a dictionary with:

- `stage`
- `description`
- `attachment_style`

### 4.5 Fusion score calculation

`NamoNexusEngine.update(score, confidence, modality)` applies modality weights:

- `face -> phi^2`
- `voice -> phi`
- `text -> 1.0`
- unknown modality -> `1.0`

The fused score is computed as:

`new_fused = (self.fused_score + (score * confidence * weight)) / (1 + weight)`

Before calculation, `score` and `confidence` are clamped into `[0.0, 1.0]`.
After calculation, `new_fused` is clamped into `[0.0, 1.0]`.

Drift detection uses absolute delta:

`abs(new_fused - self.fused_score) > self.drift_threshold`

If the delta exceeds `0.4`, `has_drift_alarm` is set to `True`; otherwise it is `False`.

`update()` then stores:

- `self.fused_score = new_fused`
- `self.confidence = confidence`
- `has_drift_alarm` is set when the delta exceeds `0.4`
- `last_drift_at` stores the wall-clock timestamp of the alarm

Drift recovery is cooldown-based:

- if a later `update()` happens at least 5 seconds after `last_drift_at`, the alarm is cleared before the new fusion step runs
- if the new step is stable, the alarm remains cleared and `last_drift_at` is reset to `None`

`NamoNexusEngine.explain()` returns a formatted string with the fused score and confidence.

### 4.6 Integration with Omega

- `core/namo_omega_engine.py` creates a `RelationshipEngine` inside each session state.
- The current session trust value is taken from the cognitive emotion snapshot when available, otherwise it defaults to `0.5`.
- `process_input()` updates relationship progression with:
  - `sin_points = state["sin_system"].sin_points`
  - `arousal = state["arousal"]`
  - `trust = cog_output["emotion"]["trust"]` when cognition returns emotion data, otherwise `0.5`
- The resulting relationship status is exposed in the returned `system_status`.

## 5. Edge Cases

- **Initial state:** a new `RelationshipEngine` always starts at `STAGE_STRANGER`.
- **Trust-only fallthrough:** low trust can force `STYLE_AVOIDANT` even when the current stage is still `STAGE_STRANGER`.
- **Obsession override:** `STAGE_OBSESSION` always maps to `STYLE_POSSESSIVE`, regardless of trust.
- **Boundary behavior:** the thresholds are inclusive where written in code (`>=`), except for the `< 1000` condition in the lover branch and the strict `> 0.4` drift alarm check.
- **No gradual interpolation:** `RelationshipEngine` does not blend stages or scores. It still jumps directly to the first matching stage before any demotion logic is applied.
- **No semantic-memory dependency inside the intimacy engine:** `RelationshipEngine` does not call the semantic memory module and does not accept a memory value.
- **Semantic-memory `None` handling upstream:** Omega only appends retrieved memory when `rag_ctx` is truthy. If semantic retrieval returns `None`, the intimacy engine still runs normally because the memory block is simply omitted.
- **Fusion `None` handling:** `NamoNexusEngine.update()` does not accept `None`; callers must provide numeric `score` and `confidence`.
- **Fusion drift behavior:** once `has_drift_alarm` becomes `True`, callers such as `NaMoTantricCore.process_seduction_interaction()` can short-circuit into aftercare logic. The alarm can clear on a later update after the 5-second cooldown.
- **Persistence on restart:** if the process restarts, both engines reload their latest JSON state from `state/relationship_engine/` and `state/fusion_engine/` when the matching session key exists.
- **No direct UI input:** users cannot set `trust`, `sin_points`, `phi`, or drift thresholds from the frontend.

### Audited source files

- `core/relationship_engine.py`
- `core/engines/namonexus_fusion.py`
- `core/namo_omega_engine.py`
- `core/seraphina_quantum_core.py`
- `tests/test_attachment_style.py`
- `tests/test_omega_engine.py`
