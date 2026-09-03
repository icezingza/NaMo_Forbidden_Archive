# Roleplay000 Lorebook Runtime Integration

## 1. Data Model

- **Manifest:** `core/lorebooks/ROLEPLAY000_IMPORT_MANIFEST_TH.json` is the logical source registry for the Roleplay000 import. It declares four `list[entry]` lorebooks and exactly 96 imported entries.
- **Logical sources:** `Story_Engine_TH.json` (29), `Simple_Personality_Traits_TH.json` (40), `Sex_Acts_TH.json` (13), and `Most_Useful_Items_TH.json` (14).
- **Physical storage:** A logical `.json` source may be stored as raw JSON, lossless `.json.gz`, or ordered `.json.gz.partNN` chunks. `LorebookRegistry` reconstructs these forms transparently and validates the manifest entry count after decompression. Physical compression never changes the logical source name exposed to runtime observability.
- **Registry metadata:** Runtime-only `_source_lorebook`, `_source_path`, `_source_index`, and `_entry_index` fields are added after loading. Source corpus text is not rewritten by the registry.
- **Activation fields:** The runtime interprets `enabled`/`disable`, `constant`, `key`, `keysecondary`, `selective`, `selectiveLogic`, `probability`, `useProbability`, `case_sensitive`, `depth`, `characterFilter`, `priority`, `insertion_order`, `position`, `tension_threshold`, `tension_levels`, and optional `beat`.
- **Placement map:** position `0=system_pre`, `1=system_post`, `2=author_note_pre`, `3=author_note_post`, `4=history_depth`, `5=example_pre`, and `6=example_post`.

## 2. API Endpoints

- No public HTTP endpoint is added or changed. Existing `/v1/chat` and `/v1/chat/stream` contracts remain unchanged.
- `core.slowburn_lorebook.SlowBurnLorebook` remains the public Python import surface used by `NaMoOmegaEngine` and existing tests.
- `LorebookRegistry.from_manifest()` provides an internal deterministic loader for manifest-scoped corpora.
- `SlowBurnLorebook.get_triggered_entries()` returns activated entries with logical source and placement metadata.
- `SlowBurnLorebook.get_injection_plan()` groups activated entries by placement without changing the external chat contract.

## 3. UI/Dashboard Elements

- No new UI is required.
- The source metadata carried by activated entries is suitable for future diagnostics such as source lorebook, entry ID, placement, beat match, priority, and insertion order. Corpus content itself should not be exposed in operational status responses.

## 4. Business Rules

- Default `SlowBurnLorebook()` loads the legacy `Sex_Positions_Kinks_SlowBurn_TH_v10.json` source plus the Roleplay000 manifest when the manifest is installed.
- A manifest-declared source is fail-closed. Missing files or a declared/actual entry-count mismatch raise `LorebookRegistryError` instead of silently running an incomplete corpus.
- `constant=true` entries may activate without keyword matching. Non-constant entries require a primary key match. When `selective=true`, secondary-key evaluation uses `selectiveLogic`: `0=ANY`, `1=ALL`, `2=NOT ALL`, `3=NOT ANY`.
- `useProbability=true` applies the declared activation percentage. Case-sensitive matching is honored when requested.
- Entry history depth is interpreted against Omega's structured `role`/`content` message history. Each entry scans exactly its declared number of most-recent messages, bounded only by the session-history retention setting; Omega no longer flattens a fixed four-message window before activation.
- `NarrativeSafetyGate` has higher precedence than lorebook activation. Corpus entries classified as underage/age-ambiguous sexual content, coercion/non-consent, incest, or exploitation are retained in source storage but not injected into the model context.
- Corpus text that attempts to override system instructions is treated as untrusted prompt material. Entries containing explicit override markers such as `BEGIN OVERRIDE SEQUENCE`, `ignore previous instructions`, or equivalent Thai override directives are retained in storage but filtered from activation.
- Omega passes the safety gate's current narrative beat directly into lorebook planning. The task-local beat remains a compatibility fallback for legacy callers, not the primary Omega integration path.
- Omega consumes the placement plan instead of flattening it into one system block. `system_pre` precedes the base system prompt, `system_post` follows the dynamic system context, author-note placements bracket the live user turn, `history_depth` is inserted at the requested message depth, and example placements are retained in their ordered prompt sections when no separate example dialogue exists.
- Runtime precedence remains: recovery/withdrawal > hard safety block > boundary clarification > narrative/lorebook behavior.

## 5. Edge Cases

- Raw `.json` takes precedence over compressed alternatives when both exist.
- A single `.json.gz` is preferred over split gzip chunks. Split chunks are concatenated in lexical `partNN` order and decompressed as one gzip stream.
- A missing optional legacy source logs a warning. A missing manifest-declared source raises an error.
- Empty `content` remains empty; the runtime does not invent replacement text.
- Unknown `position` values fall back to `system_post`.
- Invalid probability values fall back to 100 percent; values are clamped to 0–100.
- Invalid tension thresholds cause that entry to be skipped instead of crashing activation.
- Character-filtered entries do not activate when no matching character identity is supplied.
- Structured history records with unsupported roles or non-string content are ignored for lorebook scanning; caller-owned history is never mutated.
- Existing single-file construction `SlowBurnLorebook(json_path=...)` remains supported for deterministic tests and legacy callers.
- Because Roleplay000 contains source material that contradicts the original import report's claim that coercive material had been removed, runtime safety is authoritative. The corpus is preserved for provenance, while activation is filtered independently.
