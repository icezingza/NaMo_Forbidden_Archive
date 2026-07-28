# Model Routing

## 1. Data Model

- **Tables/Collections:** None. Provider registration and routing are process-local.
- **Fields & Types:** Immutable `ModelRequest`, `ModelResponse`, and `RouteMetadata` values;
  abstract `BaseProvider`; concrete OpenAI-compatible and explicit mock providers.
- **Relations & Constraints:** Provider names are normalized non-empty identifiers. Model names,
  system prompts, message roles, and message content are validated before network I/O. Messages are
  copied so providers cannot mutate caller-owned history.

## 2. API Endpoints

- **Endpoint:** No HTTP endpoint. Internal APIs are `ModelRouter.route(...)` for text compatibility
  and `ModelRouter.route_with_metadata(...)` for observable results.
- **Request Payload:** Provider name, model name, already-allocated system prompt, chronological
  messages, and supported generation parameters.
- **Response Payload:** `route()` returns response text. `route_with_metadata()` returns immutable
  text plus selected provider, model, latency, and fallback status.
- **Validation/Error Handling:** Invalid input raises `ModelRouterValidationError`; an unknown
  provider raises `ProviderNotFoundError`; transport, HTTP, and malformed provider responses have
  distinct typed failures.

## 3. UI/Dashboard Elements

- **Components:** None in this phase. `RouteMetadata` is the source for future latency, failure,
  and fallback dashboards.
- **User Actions:** None.
- **Triggered APIs:** None.

## 4. Business Rules

- The router does not allocate tokens, retrieve memory, alter shadow state, or rewrite prompts.
  Callers must pass output already processed by the context-allocation pipeline.
- Unknown provider names fail closed. Silent mock responses are forbidden because they hide broken
  deployment configuration.
- Fallback is opt-in per call and may target only a registered provider. Fallback activates only
  after a provider execution failure, never after request validation failure.
- OpenAI-compatible transport uses an injectable persistent HTTP session, bounded connect/read
  timeouts, explicit generation-parameter allowlisting, and strict response-shape validation.
- API keys and prompt/message content are never written to logs. Automatic retries are excluded:
  generation requests are not safely idempotent without provider-specific idempotency support.
- This phase is synchronous. Streaming integration requires a separate async/streaming provider
  contract and must not emulate streaming by buffering this interface.

## 5. Edge Cases

- **Empty States:** Empty `system_prompt` is valid; empty message lists are valid. `None` is invalid
  because allocator-side None tolerance must already have normalized the request.
- **Concurrency Handling:** Provider registration and lookup are guarded by a re-entrant lock;
  network calls occur after the lock is released. The injected HTTP session must itself be safe for
  the application's concurrency model.
- **Failbacks:** Missing credentials, timeouts, connection errors, non-success HTTP responses, and
  malformed response payloads raise typed errors unless an explicit fallback provider is supplied.
- Empty model output is accepted when the provider returns a valid string. Non-string or missing
  content is a malformed provider response.
- Duplicate system messages in `messages` are rejected; the dedicated `system_prompt` is the only
  system channel owned by this router.
