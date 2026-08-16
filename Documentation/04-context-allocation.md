# Context Allocation

## 1. Data Model

- **Tables/Collections:** None. Allocation is stateless and performed in memory.
- **Fields & Types:** Frozen `AllocatorConfig`; immutable `ContextMessage`; optional critical-system
  text; dynamic-system text; allocation output containing content, usage metrics, and truncation
  metadata.
- **Relations & Constraints:** Prompt ratios must be finite values in `[0.0, 1.0]` and sum to
  `1.0`. `context_window` must exceed `response_reserve`. A caller may inject the model's exact
  token counter; otherwise a conservative multilingual estimator is used.

## 2. API Endpoints

- **Endpoint:** No HTTP endpoint. Internal API: `ContextAllocator.allocate(...)`.
- **Request Payload:** Critical system text, optional memory text, and chronological history as
  message mappings or `ContextMessage` values.
- **Response Payload:** Truncated system and memory text, role-preserving copied history messages,
  exact/estimated usage metrics, and explicit truncation/drop counters.
- **Validation/Error Handling:** Invalid configuration, message roles/content, and non-string text
  raise `TypeError` or `ValueError` before allocation.
- **Omega integration:** Both `NaMoOmegaEngine.stream_input()` and non-streaming generation call
  one prompt-allocation helper. Allocation metadata is stored per session and contains no prompt,
  memory, or history content.
- **API visibility:** Non-streaming Omega responses expose allocation metadata under
  `status.context_allocation`. The final `/v1/chat/stream` completion event exposes the same
  metadata under `context_allocation` when supported by the selected engine.
- **Usage logging:** `/v1/chat` and `/v1/chat/stream` usage events include allocation metadata when
  the selected engine provides it. Logged metadata never includes prompt content.

## 3. UI/Dashboard Elements

- **Components:** None.
- **User Actions:** None.
- **Triggered APIs:** None.

## 4. Business Rules

- **Access Control / Gating:** None; this is an internal utility.
- **State Transitions:** None; `allocate()` does not mutate conversational state or caller-owned
  message mappings.
- **Resource Limits:** Response tokens are reserved before prompt allocation. System, memory, and
  history receive soft caps; unused system and memory capacity is redistributed to history.
  System and memory keep their leading content. Oversized newest history content keeps its tail.
  Every truncation uses the configured token counter and a binary search, not a character ratio.
- **Priority:** Critical persona/rule text is allocated before dynamic status, relationship,
  cognitive, memory, and history content. Critical text may borrow the full prompt budget; if it
  alone exceeds that budget, truncation is reported as `critical_system=true`.
- **Configuration:** `NAMO_LLM_CONTEXT_WINDOW` defaults to `8192`; `NAMO_LLM_MAX_TOKENS` is used as
  the response reserve. Omega uses the conservative Unicode estimator until a model tokenizer is
  explicitly injected.
- **Tokenizer selection:** Official OpenAI endpoints use `tiktoken.encoding_for_model()` when the
  configured model is recognized and the optional package is available. Custom OpenAI-compatible
  endpoints and unknown models use the conservative Unicode estimator. Local counts cover plain
  text and configured message overhead; they are not provider-authoritative counts for tools,
  images, files, reasoning tokens, or model-specific server behavior.

## 5. Edge Cases

- **Empty States:** Empty system, memory, or history values produce empty allocated sections.
- **Concurrency Handling:** Configuration and normalized message values are immutable. Allocation
  keeps all mutable state local to the call.
- **Failbacks:** Without an injected model tokenizer, the allocator uses a conservative Unicode
  estimator and exposes `estimation_method="conservative_unicode"`; this is not an exact model
  token count. Message/protocol overhead is reserved per included history message.
- **Current-user preservation:** The current user message is appended as the newest history item.
  If oversized, its tail is retained rather than dropping the entire message.
- **Dependency failure:** Missing `tiktoken`, an unknown model encoding, or a custom provider is a
  normal fallback condition and does not prevent Omega startup.
