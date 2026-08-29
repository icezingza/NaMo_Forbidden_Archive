# Safe Narrative Data Pipeline and Beat-Aware Runtime

## 1. Data Model

- **Dataset record:** `chunk_id`, `document_id`, `text`, `beat`, `safety_labels`,
  `source_hash`, `sanitizer_version`, and `review_status`.
- **Provenance record:** source-relative path, source hash, decision, reason codes, classifier
  version, chunk count, and processing timestamp. Rejected source text is never copied into the
  audit log.
- **Runtime narrative state:** `tension_meter` in `[0, 100]`, `current_beat`, `boundary_state`,
  and `last_transition_reason`. The state is stored in State Ledger metadata.
- **Enums:** beats are `tease`, `resistance`, `escalation`, `resolution`, and `recovery`.
  Boundary states are `clear`, `clarify`, `blocked`, and `recovery`.
- **Constraints:** records labelled for underage or age ambiguity, non-consent, coercion,
  exploitation, incest, or graphic violence cannot be promoted automatically.

## 2. API Endpoints

- **Endpoint:** No new public HTTP endpoint. The offline entrypoint is
  `scripts/build_narrative_dataset.py`; runtime evaluation is internal to `NaMoOmegaEngine`.
- **Request Payload:** Offline input is a directory containing HTML/HTM files. Runtime input is
  the existing user message and session ID.
- **Response Payload:** Offline output is review-candidate JSONL plus provenance JSONL. Runtime responses
  retain the existing payload and add `system_status.narrative_safety`.
- **Validation/Error Handling:** Invalid paths and malformed output records fail explicitly.
  Rule-passing records remain `PENDING_HITL`. Runtime high-risk input fails closed before
  cognitive, retrieval, media, or model generation.

## 3. UI/Dashboard Elements

- **Components:** No UI in this phase. `system_status.narrative_safety` and provenance aggregates
  are dashboard-ready.
- **User Actions:** Existing chat actions only. Dataset promotion remains an offline operator task.
- **Triggered APIs:** Existing `/v1/chat` and `/v1/chat/stream`; no raw source text is exposed in
  status fields.

## 4. Business Rules

- Structural cleaning removes scripts, styles, navigation, advertising boilerplate, tags, and
  normalizes Unicode and Thai whitespace before classification.
- Filename and cleaned text are both classified. A blocked filename cannot be rescued by benign
  body text.
- Exact duplicate content is removed by content hash. Near-duplicate MinHash/LSH is deferred until
  its dependency and quality threshold are evaluated against Thai text.
- Only human-approved chunks may enter the golden dataset. `REJECT` records produce provenance
  entries without copied source content; rule-passing records receive a `REVIEW` decision.
- Runtime safety precedence is `RECOVERY > BLOCK > CLARIFY > NARRATIVE`. Safewords and withdrawal
  signals force recovery. Underage, age-ambiguous sexual context, incest, coercion, and exploitation
  are blocked and redirected.
- Beat transitions are deterministic. The LLM receives the selected beat directive but cannot
  write session state directly.
- DPO records may only be emitted from human-reviewed approved chunks. Toxic source passages are
  never used as rejected examples in the approved training artifact.

## 5. Edge Cases

- **Empty States:** Empty or boilerplate-only documents are rejected. New runtime sessions start
  at `tease`, zero tension, and a clear boundary state.
- **Concurrency Handling:** Dataset outputs are written to temporary files and atomically replaced.
  Runtime metadata uses the existing State Ledger conflict handling.
- **Failbacks:** This phase has no model classifier; all rule-passing records require HITL review.
  A runtime gate failure returns a deterministic safe response and suppresses media.
- **Encoding:** HTML decoding uses UTF-8 and replaces invalid byte sequences;
  the source hash always covers the original bytes.
- **Privacy:** Audit logs contain paths, hashes, labels, versions, and counts only, not rejected text.
