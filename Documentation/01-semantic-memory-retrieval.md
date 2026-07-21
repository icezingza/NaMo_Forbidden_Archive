# Feature Name: Semantic Memory Retrieval

> Audit date: 2026-07-21  
> Scope: outer `NaMo_Forbidden_Archive` repository only; the nested `namo_forbidden_archive/` Git repository was excluded.  
> Evidence basis: current source code and repository artifacts. Existing architecture documents were used only for orientation where confirmed by code.

## 1. Data Model

### 1.1 Local FAISS knowledge index

- **Storage:** `vector_db/knowledge.index`, written and read as a FAISS index.
- **Index type:** `faiss.IndexFlatL2`.
- **Vector type:** embeddings are converted to NumPy `float32` arrays before indexing and querying.
- **Embedding model:** `text-embedding-3-large` for both `learn_from_set.py` and `core/rag_memory_system.py`/`query_learned_knowledge.py` queries.
- **Source input:** `learning_set/set.zip`. `learn_from_set.py` deletes and recreates `vector_db/extracted/`, extracts the ZIP, and walks every extracted file. Files are first decoded as UTF-8, then Latin-1; unreadable files are skipped.
- **Builder chunking:** `learn_from_set.py` splits by Python string character offsets, not tokenizer tokens: size `800`, overlap `200`, and stride `600`.
- **Loader behavior:** `NaMoInfiniteMemory.ingest_data()` now only loads the persisted FAISS artifacts. The runtime path does not build in-memory fallback chunks, does not generate mock memories, and does not update the index.
- **Current artifact state:** no files were present under `vector_db/` at audit time. The committed source therefore contains index-building and retrieval logic but no locally available FAISS index or metadata artifact in this checkout.

### 1.2 Local FAISS metadata

- **Storage:** `vector_db/meta.json`, a JSON array whose order is expected to match FAISS vector positions.
- **Fields per builder-produced item:**
  - `file`: source basename (`str`).
  - `chunk_id`: zero-based chunk number within the source file (`int`).
  - `snippet`: first 160 characters of the indexed chunk (`str`).
  - `path`: source path relative to `vector_db/extracted/` (`str`).
- **Runtime output:** `NaMoInfiniteMemory._vector_search()` returns only `"{file}#{chunk_id}: {snippet}"`; it does not return `path` or the full indexed chunk.
- **Standalone query mutation:** `query_knowledge()` adds `score` (`float`, raw L2 distance) directly to each selected metadata dictionary before returning it.
- **Relations and constraints:** FAISS result index `i` is valid only when `0 <= i < len(meta)`. There is no code that verifies index vector count, embedding dimension, model identity, or metadata length against each other when loading.

### 1.3 Qdrant semantic collection

- **Collection:** `namo_cognitive_mesh`.
- **Vector configuration:** size `1536`, cosine distance.
- **Embedding model:** `text-embedding-3-small` in both `IngestionPipeline` and `NaMoReasoningEngine._get_working_memory()`.
- **Point ID:** random UUID string generated per chunk.
- **Payload fields:**
  - `text`: full chunk (`str`).
  - `source`: source basename (`str`).
  - `domain`: caller-supplied domain (`str`).
  - `chunk_index`: zero-based index within the source file (`int`).
- **Chunking:** character-based size `500`, overlap `50`, stride `450`.
- **Graph relation created during the same ingestion pass:** `(Identity {name})-[:HAS_KNOWLEDGE]->(Knowledge {chunk_id})`. The `Knowledge` node stores `source`, `domain`, and the first 100 characters as `snippet`.
- **Current remote state:** not determinable from repository source. The audit did not query external Qdrant or Neo4j services.

## 2. API Endpoints

There is no dedicated HTTP endpoint for building or directly querying the semantic index.

### `POST /chat`

- **Request payload:** `text: str`, optional `session_id: str`, optional `engine: str`.
- **Default engine:** `omega` from `Settings.default_engine`.
- **Retrieval path:** when the active engine is `omega`, `NaMoOmegaEngine.process_input()` classifies the text and may call FAISS-backed `retrieve_context()` before LLM generation.
- **Response:** includes `response`, `session_id`, `media`, `status`, and engine class name. Retrieved memory is not exposed as a separate response field or citation.
- **Validation/error handling:** FastAPI/Pydantic validates the request shape. Retrieval embedding failures are swallowed inside `_vector_search()` and fall through to runtime memory fallback. Exceptions from `retrieve_context()` itself are not caught around the Omega call.

### `POST /v1/chat`

- **Request and retrieval behavior:** same engine payload and Omega retrieval path as `/chat`.
- **Additional controls:** IP rate limiting; API-key validation is enforced only when configured API keys exist.
- **Response:** same semantic-memory visibility as `/chat`; includes an additional `plan` field.

### `POST /v1/chat/stream`

- **Request payload:** same `ChatInput` model.
- **Retrieval path:** `NaMoOmegaEngine.stream_input()` performs the same intent-gated retrieval before starting the LLM stream.
- **Response:** Server-Sent Events containing generated text chunks and completion metadata. Retrieved context is not emitted separately.
- **Error handling:** the stream wrapper emits an SSE error object when an exception escapes engine streaming, then still emits the final completion event.

### Non-HTTP entry points

- `python learn_from_set.py`: builds `knowledge.index` and `meta.json`; requires `learning_set/set.zip`, FAISS, NumPy, and a working OpenAI embedding client.
- `python query_learned_knowledge.py`: prompts for a question, queries top 3 by default, and prints `file`, `chunk_id`, and `snippet`.
- `IngestionPipeline.run(...)`: programmatic/CLI ingestion into Qdrant and Neo4j; it is not wired to a FastAPI route in the audited code.
- `SovereignOrchestrator`: routes `NAMO_CORE` requests to `NaMoReasoningEngine.generate_response()`, which queries Qdrant/Neo4j working memory. No call from `server.py` to this orchestrator was found in the audited path.

## 3. UI/Dashboard Elements

- **Components:** the main static client exposes a chat input, streaming toggle, engine selector, session state, and generated response area. It has no semantic-memory search form, result list, score display, source citation, index status, or ingestion control.
- **User actions:** selecting the Omega engine and sending a message can indirectly trigger retrieval. The user cannot explicitly force retrieval or select `top_k`/threshold from the UI.
- **Triggered APIs:** non-streaming chat calls `POST /chat`; streaming chat calls `POST /v1/chat/stream`. Both send `text`, `session_id`, and the selected `engine`.
- **Visibility:** retrieved context is inserted as an internal system message (`[Memory]: ...`) before LLM generation. The UI receives only the generated answer, not the memory hit or its distance.

## 4. Business Rules

### 4.1 Omega FAISS retrieval

1. `NaMoInfiniteMemory` is constructed during Omega engine initialization even when FAISS is disabled. `AsyncOpenAI()` is also constructed at that time.
2. FAISS import occurs only when the process environment contains `NAMO_RAG_ENABLED=1`. This flag is read at module import time.
3. The FAISS index loads only when both `vector_db/meta.json` and `vector_db/knowledge.index` exist and FAISS imported successfully.
4. The first `retrieve_context()` call acquires an async load lock and runs `ingest_data()` through `asyncio.to_thread()` when `is_loaded` is false. Concurrent first calls serialize on the same lock.
5. `ingest_data()` is now a deterministic loader only. It reads the persisted FAISS artifacts, marks the instance as loaded, and does not create runtime fallback memories.
6. Runtime retrieval is gated by intent. Omega requests semantic memory only for `comfort`, `nostalgia`, or `affection`; other intents, including `neutral` and `lust`, skip it.
7. Query embeddings use up to 3 attempts. Backoff waits are `1.0` then `2.0` seconds before the final attempt; the final failure is converted to no vector hit.
8. FAISS searches exactly one nearest neighbor in the Omega runtime path, and the search call itself is executed via `asyncio.to_thread()` so the event loop is not blocked.
9. The raw L2 distance must be less than or equal to `0.45`; a larger value is rejected.
10. A valid hit becomes a single text fragment containing metadata filename, chunk ID, and the stored 160-character snippet.
11. When no accepted vector hit exists, retrieval returns `None`. No random chunk, mock string, or placeholder is generated.
12. Only a non-empty retrieved hit is injected into the LLM prompt as `[Memory]: {result}`.

### 4.2 Standalone FAISS query

- `query_knowledge(question, top_k=3)` requires both FAISS and metadata files or raises `FileNotFoundError`.
- It returns up to `top_k` raw nearest results without applying the Omega runtime threshold of `0.45`.
- Results remain ordered as returned by FAISS and expose raw L2 distance as `score`.

### 4.3 Qdrant/Neo4j working memory

- Retrieval runs only when both an OpenAI-compatible client and Qdrant client were initialized.
- It embeds the query with `text-embedding-3-small`, searches `namo_cognitive_mesh`, and requests 3 results with no score threshold or payload filter.
- Semantic context is the newline join of each result payload's `text`; a missing `text` value contributes an empty string.
- Neo4j is queried independently using the first 20 characters of the raw query. It matches `Knowledge.domain` or `Knowledge.snippet` with case-sensitive Cypher `CONTAINS`, returning at most 2 records.
- Vector or graph retrieval exceptions are logged and converted to an empty section. The returned working-memory string always contains both section headings.
- The Qdrant/Neo4j path and the local FAISS/Omega path are separate implementations with different models, dimensions, chunk sizes, distance metrics, and consumers.

## 5. Edge Cases

- **Missing local index:** with no FAISS artifacts, `_vector_search()` returns `None`. In this checkout that remains the deterministic local state when the built index files are absent.
- **RAG disabled:** when `NAMO_RAG_ENABLED` is not exactly `1`, FAISS is not imported and index loading is skipped; retrieval still returns `None` instead of any generated fallback.
- **No source files or invalid artifacts:** `ingest_data()` now only attempts to load persisted FAISS artifacts. It no longer installs hard-coded memories, and `is_loaded` still becomes `True` after the load attempt completes.
- **Source files but no semantic match:** retrieval returns `None`. There is no random selection from runtime chunks and no placeholder string such as `"..."`.
- **Embedding failure:** Omega logs the error and returns no vector hit. The standalone builder/query retries and then propagates the final exception.
- **Distance boundary:** Omega accepts a hit when distance equals `0.45` and rejects only values greater than `0.45`.
- **Invalid FAISS index value:** negative/out-of-range result indices produce no vector hit; standalone `query_knowledge()` checks only `i < len(meta)`, so a negative index would index from the end of the Python list.
- **Metadata mutation:** standalone queries add `score` to dictionaries loaded from JSON in memory; the JSON file is not rewritten.
- **Chunk semantics:** all three ingestion/chunking implementations use Python character counts despite comments/docstrings referring to tokens in the runtime RAG class.
- **Model/index compatibility:** no guard prevents querying an existing FAISS index built with a different embedding dimension/model; FAISS/OpenAI may fail at runtime.
- **Concurrency:** the Omega FAISS index and metadata are shared on one engine instance and guarded by an async initialization lock. First-call loading is serialized, and the filesystem load runs off the event loop via `asyncio.to_thread()`.
- **Blocking behavior:** first retrieval no longer blocks the event loop with synchronous filesystem scanning, because the load path is offloaded to a worker thread.
- **Prompt provenance:** retrieved snippets have no trust classification, sanitization, or prompt-injection boundary beyond the `[Memory]` label.
- **Qdrant unavailability:** reasoning continues with an empty semantic section after logging the exception.
- **Qdrant API compatibility:** the implementation calls `AsyncQdrantClient.search`; behavior depends on the installed `qdrant-client` version, which is not pinned in the inspected dependency declaration.
- **Graph credentials:** Neo4j initialization receives `NEO4J_PASSWORD` even when unset; initialization/query failure is logged and graph context remains empty.
- **Resource cleanup:** `NaMoReasoningEngine.close()` unconditionally calls `.close()` on Qdrant and Neo4j members even though either can be `None`.
- **Legacy caller mismatch:** `NaMoGenerativeBrain.think_and_reply()` now awaits async `retrieve_context()` before generating its response. No server route was found using this class.

### Audited source files

- `core/rag_memory_system.py`
- `learn_from_set.py`
- `query_learned_knowledge.py`
- `core/namo_omega_engine.py` (RAG construction, intent gate, prompt injection, and status path only)
- `core/intent_analyzer.py` (intent classification used by the RAG gate)
- `core/memory/ingestion_pipeline.py`
- `core/engines/reasoning_engine.py` (working-memory retrieval path only)
- `core/orchestration/orchestrator_engine.py` (reasoning-engine caller only)
- `core/generative_brain.py` (legacy retrieval caller only)
- `server.py` (chat request/response integration only)
- `web/app.js`, `web/index.html`, and `web/chat-cloud.html` (chat controls and API calls only)
- `tests/test_rag_memory.py` and the intent-aware RAG section of `tests/test_omega_engine.py`
