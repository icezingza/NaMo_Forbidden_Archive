# State Ledger and Session Persistence

## 1. Data Model

- **Storage:** `state/namo_state.json`; the root-level legacy `namo_state.json` used by
  `CharacterProfile` is not overwritten by this component.
- **Ledger envelope:** `schema_version: int` and `sessions: dict[str, SessionEntry]`.
- **Session state:** `session_id`, `relationship_stage`, `fused_score`, `attachment_style`,
  `confidence`, `turn_count`, `last_updated`, and JSON-serializable `metadata`.
- **Transition:** transition ID, UTC timestamp, turn number, previous/new stage, previous/new fused
  score, requested score delta, and event metadata.
- **Constraints:** fused score and confidence are finite values clamped to `[0.0, 1.0]`; session IDs
  are non-empty strings of at most 256 characters; transition history is bounded per session.

## 2. API Endpoints

- **Endpoint:** No HTTP endpoint. Internal APIs are `StateLedger.load_state()`,
  `StateLedger.commit_transition()`, and `StateLedger.get_history()`.
- **Request Payload:** Session ID for reads; current `SessionState`, score delta, and optional event
  metadata for commits.
- **Response Payload:** Defensive `SessionState` snapshots and copied transition dictionaries.
- **Validation/Error Handling:** Invalid state or JSON metadata raises `TypeError`/`ValueError`.
  Corrupt or unsupported ledgers raise `StateLedgerCorruptionError`; stale writers raise
  `StateConflictError` instead of silently losing newer state.

## 3. UI/Dashboard Elements

- **Components:** None in this phase.
- **User Actions:** None.
- **Triggered APIs:** None. Observability/dashboard integration is deferred.

## 4. Business Rules

- **Access Control / Gating:** The ledger is an internal persistence component; callers control
  session authorization before access.
- **State Transitions:** Scores below `0.2` map to `awakening`; `[0.2, 0.5)` to `synchronized`;
  `[0.5, 0.8)` to `deep_attachment`; and `>=0.8` to `maximum_resonance`. Negative deltas can demote
  a stage. Every successful commit increments `turn_count` once and appends one transition.
- **Resource Limits:** Default history retention is 500 transitions per session. The entire
  multi-session envelope is preserved on every commit.
- **Durability:** Commits are serialized across ledger instances in the current process. Data is
  written to a unique temporary file in the destination directory, flushed, `fsync`-ed, and
  atomically replaced.

## 5. Edge Cases

- **Empty States:** A missing session returns a fresh state without writing to disk.
- **Concurrency Handling:** Optimistic `turn_count` validation rejects stale snapshots. The
  in-process path lock prevents thread races. Cross-process advisory locking is not implemented;
  deployments with multiple writer processes must place this component behind one writer/service.
- **Failbacks:** Candidate single-session and session-keyed snapshot formats are migrated in memory
  on the next successful commit. Corrupt JSON is never silently overwritten.
- **Metadata Isolation:** Input and output metadata are deep-copied so callers cannot mutate stored
  state through shared references.

