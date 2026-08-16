# Unified Omega Engine

## 1. Data Model

- **Tables/Collections:** Uses the versioned State Ledger at `state/namo_state.json`; conversation
  history remains process-local and session-scoped.
- **Fields & Types:** Each runtime session owns arousal, sin/persona/relationship engines, the
  latest immutable `SessionState`, context-allocation metadata, route metadata, and ledger commit
  metadata.
- **Relations & Constraints:** A normalized session ID is the shared key across runtime state,
  history, and State Ledger. Prompt allocation precedes every provider call. A ledger transition
  is committed only after a non-empty response has been produced.

## 2. API Endpoints

- **Endpoint:** Existing `/v1/chat` and `/v1/chat/stream` contracts remain unchanged. Internal
  entrypoints remain `NaMoOmegaEngine.process_input()` and `stream_input()`.
- **Request Payload:** User input and optional session ID. Memory is retrieved only for configured
  memory-relevant intents.
- **Response Payload:** Existing text/media/system-status payload plus `state_ledger` and
  `model_route` observability. Prompt or memory content is never included in observability.
- **Validation/Error Handling:** Allocator and router validation errors remain typed internally.
  Provider failure uses the existing persona fallback. Ledger failures do not erase an already
  generated response; the failure class is exposed in status and logged without state content.

## 3. UI/Dashboard Elements

- **Components:** No new UI. `system_status.context_allocation`, `system_status.model_route`, and
  `system_status.state_ledger` are dashboard-ready fields.
- **User Actions:** Existing chat and streaming actions only.
- **Triggered APIs:** Existing chat endpoints. No new public endpoint is introduced.

## 4. Business Rules

- The engine loads ledger state before prompt synthesis, injects a read-only resonance block into
  dynamic system context, allocates the full prompt, routes generation, then commits one state
  transition after successful output.
- Resonance is signal-driven, not a fixed per-turn increment. Target score is `0.5 * trust + 0.3 *
  desire + 0.2 * arousal`; the transition moves 20 percent toward that target, scaled by signal
  confidence. Cognitive output has confidence `0.75`; missing cognitive output has confidence
  `0.25` and uses neutral defaults.
- A stale ledger commit is retried once from the latest snapshot using the same target signal.
  Other ledger errors are surfaced through observability and are never silently converted into a
  successful commit.
- The synchronous Model Router runs through `asyncio.to_thread()` so it cannot block the event
  loop. Streaming keeps the native async OpenAI-compatible client until a streaming provider
  contract exists.
- Router and ledger dependencies are injectable for deterministic tests and alternate deployment
  wiring. Default provider configuration uses `NAMO_LLM_PROVIDER`, `NAMO_LLM_MODEL`,
  `NAMO_LLM_BASE_URL`, and `OPENAI_API_KEY`.
- Context allocation owns truncation. Router and ledger code must not rewrite prompt, memory, or
  history content.

## 5. Edge Cases

- **Empty States:** Missing sessions load an unwritten fresh ledger state. Missing memory is an
  empty allocation section. `None` session IDs use the existing `default` session.
- **Concurrency Handling:** Per-session runtime maps are process-local. State Ledger performs
  optimistic turn checking; one stale-write retry is allowed. Cross-process single-writer limits
  from the State Ledger specification still apply.
- **Failbacks:** Provider failure returns the existing deterministic persona response and still
  commits the completed conversational turn. An empty stream with no fallback output does not
  commit a ledger transition. TTS failure does not roll back text or ledger state.
- **Compatibility:** Existing output keys, local fallback, RAG selection, cognitive processing,
  history trimming, TTS, and SSE behavior are retained. The candidate's destructive engine
  replacement is explicitly rejected.
- **Observability isolation:** Route and ledger status contain identifiers, numeric metrics, and
  error class names only; no API keys, prompts, memory fragments, or response text.
