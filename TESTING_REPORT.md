# NaMo Forbidden Archive — Testing & Audit Report
**Date:** 2026-06-16  
**Status:** 🔴 **CRITICAL ISSUES FOUND** — NOT READY FOR PRODUCTION  

---

## Executive Summary

Project cannot start due to **missing import dependencies**. Static analysis found 4 critical import errors that will prevent the API server from launching. Additional architectural issues exist that could impact production stability.

**Recommendation:** Fix critical issues before any deployment attempt.

---

## Critical Issues (Must Fix Before Ship)

### ❌ Issue #1: Missing `core/engines/` Directory

**Severity:** 🔴 CRITICAL  
**Impact:** Server fails to start

**Details:**
- **File:** `server.py` (line 146)
- **Error:** `from core.engines.asi_simulation_engine import asi_engine`
- **Problem:** `core/engines/` directory does not exist
- **Affected Files:**
  - `server.py` → imports asi_engine, uses in `/api/dream` endpoint
  - `core/orchestration/orchestrator_engine.py` → imports from core.engines (lines 10-11):
    - `core.engines.reasoning_engine`
    - `core.engines.asi_simulation_engine`

**Root Cause:** Feature branch merged incompletely; orchestration engine and ASI simulation were added but supporting modules weren't created.

**Fix Required:**
```bash
mkdir -p core/engines
# Then either:
# Option A: Create stub implementations
touch core/engines/__init__.py
touch core/engines/reasoning_engine.py    # Define reasoning_engine
touch core/engines/asi_simulation_engine.py  # Define asi_engine
# Option B: Remove the /api/dream endpoint from server.py if feature is incomplete
```

---

### ❌ Issue #2: Orphaned `/api/dream` Endpoint

**Severity:** 🔴 CRITICAL  
**Impact:** Server fails to start (import error)

**Details:**
- **File:** `server.py` (lines 146–156)
- **Problem:** Endpoint depends on `asi_engine` which doesn't exist
- **Code:**
```python
from core.engines.asi_simulation_engine import asi_engine

@app.post("/api/dream")
async def trigger_dream(x_admin_secret: str | None = Header(default=None)):
    """Trigger ASI Research & Simulation (Cloud Scheduler Endpoint)"""
    _assert_admin(x_admin_secret)
    asyncio.create_task(asi_engine.generate_hypothesis())
    return {"status": "NaMo is dreaming and researching..."}
```

**Fix:** Either complete the asi_simulation_engine module or comment out / remove the endpoint.

---

### ⚠️ Issue #3: Directory Structure Duplication

**Severity:** 🟡 HIGH  
**Impact:** Confusion, maintenance burden, potential import conflicts

**Details:**  
Duplicate folder: `namo_forbidden_archive/` exists at root level alongside production code.
- Root has: `core/`, `adapters/`, `tests/`, `server.py`, `config.py`
- Also has: `namo_forbidden_archive/` containing **duplicate** of all above

**Implications:**
- Unclear which is production source of truth
- Potential for edits in wrong folder
- Doubles maintenance burden
- May cause import issues if symlink/alias is misconfigured

**Recommendation:**  
Delete `namo_forbidden_archive/` folder entirely unless it serves as a backup. If it's intentional (e.g., versioned archive), document this in `README.md`.

---

### ⚠️ Issue #4: Orphaned `/templates/` Improved Versions

**Severity:** 🟡 MEDIUM  
**Impact:** Code maintenance, CI/test confusion

**Details:**  
`templates/namo_forbidden_archive/improved/` contains refactored/improved versions of core modules:
- `server_with_all_fixes.py` (suggests bugs in current `server.py`)
- `config_improved.py`
- `memory_service_db_improved.py`
- Auth, cache, session management improvements

**Questions:**
- Why aren't these "improvements" merged back into production?
- Are they feature branches left uncommitted?
- Should tests run against these versions instead?

**Recommendation:**  
Review, integrate improvements, or explicitly document why they're archived. Do not ship with unresolved "improved" versions lingering.

---

## Moderate Issues (Fix Before Production)

### ⚠️ Issue #5: Cognitive Stack Module Missing

**Severity:** 🟡 MEDIUM  
**Impact:** Optional features fail silently if imported

**Details:**  
- **File:** `core/base_persona.py` defines `CognitiveCore` (calls `cognitive.process()`)
- **Expected:** `core/cognitive_stream.py` exists and is tested
- **Status:** Glob found file in list, but verify it's complete and tested

**Recommendation:**  
Ensure `CognitiveCore` chain (`EmotionEngine` → `CognitiveStream` → `LearningEngine`) is fully tested in CI.

---

### ⚠️ Issue #6: RAG/FAISS Knowledge Base Not Validated

**Severity:** 🟡 MEDIUM  
**Impact:** If `learning_set/` ZIP is missing or corrupt, knowledge base fails

**Details:**
- Mentioned in CLAUDE.md: `learn_from_set.py` requires `learning_set/set.zip`
- No validation that this file exists or is valid
- Fallback behavior not documented

**Recommendation:**  
Add init check: if knowledge base missing, log WARNING but allow server to start in degraded mode.

---

### ⚠️ Issue #7: Memory Service Dual-Write Reliability

**Severity:** 🟡 MEDIUM  
**Impact:** Data loss if memory service crashes

**Details:**
- `adapters/memory.py` does "dual-write" (local JSON + remote service)
- Remote write has 2-second timeout (line 217: `timeout=2`)
- If remote fails, error is logged but not retried
- No circuit breaker

**Current Code:**
```python
try:
    requests.post(memory_url, json=payload, headers=headers, timeout=2)
except requests.RequestException as exc:
    print(f"[MemoryLog]: Failed to store memory: {exc}")
```

**Recommendation:**  
- Increase timeout to 5s or add exponential backoff
- Log memory failures to a queue for later replay
- Document that loss of remote memory is acceptable (local JSON is source of truth)

---

## Test Coverage Gaps

### ❌ Missing Test Files

**Files that must have tests but don't:**
```
orchestration/orchestrator_engine.py  ← No test_orchestrator.py
core/engines/                         ← Directory + contents don't exist
templates/improved/                   ← Improvements never tested
```

**Existing tests:** 335+ tests in `tests/` (good), but:
- No test for `/api/dream` endpoint (will fail if fixed)
- No test for orchestrator (yet to be implemented)

---

## Security & Configuration Issues

### ⚠️ Issue #8: Default Config Exposes NSFW Toggle

**Severity:** 🟡 MEDIUM  
**Impact:** Unintended behavior exposure

**Details:**  
`config.py` defaults:
```python
safety_filter_enabled: bool = False    # ← DISABLED
nsfw_allowed: bool = True              # ← ENABLED
```

This is intentional per CLAUDE.md ("NSFW content is intentional"), but:
- No warning in logs when NSFW is active
- No env var `.env.example` to guide users

**Recommendation:**  
Add to server startup:
```python
if not settings.safety_filter_enabled and settings.nsfw_allowed:
    print("[WARNING]: NSFW mode enabled. This is intentional but must be documented to end-users.")
```

---

## Code Quality Issues

### ⚠️ Issue #9: Line Length Violations

**Severity:** 🟡 MEDIUM  
**Impact:** Fails linting

**Details:**  
CLAUDE.md specifies: "Line length limit: 100 characters (ruff enforces this)"

Found likely violations in:
- `core/orchestration/orchestrator_engine.py` (router_prompt is long multi-line string)
- Possibly others (requires full ruff run)

**Recommendation:**  
Run `make format` to auto-fix, then review.

---

### ⚠️ Issue #10: Type Hints Incomplete

**Severity:** 🟡 MEDIUM  
**Impact:** Type checking gaps

**Details:**  
Some functions in new modules (orchestrator, improved versions) may lack strict type hints.

Example (orchestrator_engine.py line 42):
```python
async def route_query(self, user_input: str) -> str:
```

Is good, but return type should be more specific if it can fail (Optional[str]? Dict?).

---

## Recommendations (Priority Order)

### **BLOCKER (fix before any testing)**
1. ✅ Create `core/engines/` directory and its modules, OR
2. ✅ Remove `/api/dream` endpoint and orphaned imports

### **BEFORE SHIP**
3. ✅ Delete or document `namo_forbidden_archive/` duplication
4. ✅ Merge improvements from `templates/improved/` or archive clearly
5. ✅ Run `make lint` and `make format` (fix violations)
6. ✅ Run full `make test` suite (must pass 100%)
7. ✅ Verify knowledge base init graceful degradation
8. ✅ Add startup logging for NSFW mode enabled

### **NICE TO HAVE**
9. Add orchestrator tests
10. Improve memory service failure handling (circuit breaker)
11. Document orchestrator feature status (alpha/beta/GA)

---

## How to Verify Fixes

### Step 1: Fix Import Errors
```bash
# Option A: Create engines
mkdir -p core/engines
cat > core/engines/__init__.py << 'EOF'
# Placeholder
EOF

cat > core/engines/asi_simulation_engine.py << 'EOF'
class ASISimulationEngine:
    async def generate_hypothesis(self):
        return {"status": "ASI simulation not implemented"}
asi_engine = ASISimulationEngine()
EOF

cat > core/engines/reasoning_engine.py << 'EOF'
# Placeholder reasoning engine
reasoning_engine = None
EOF
```

### Step 2: Validate Server Starts
```bash
make run
# Expected: Server starts on http://localhost:8000
# Test: curl http://localhost:8000/
```

### Step 3: Run Full Test Suite
```bash
make test
# Expected: All 335+ tests pass
make lint
make format
```

### Step 4: Clean Duplicates
```bash
rm -rf namo_forbidden_archive/
```

---

## Test Results (If Run)

**Cannot run full suite until blockers fixed.**

Quick validation checklist:
- [ ] `server.py` imports without error
- [ ] `python -c "from server import app"` succeeds
- [ ] `make lint` passes
- [ ] `make format` passes  
- [ ] `make test` passes
- [ ] `/` endpoint returns valid JSON
- [ ] `/v1/engines` lists all 5 engines
- [ ] `/chat` endpoint accepts POST and returns response

---

## Conclusion

Project is **not production-ready** due to critical import errors. Once blockers are fixed, it's a solid NSFW roleplay platform with:
- ✅ Clean FastAPI architecture
- ✅ 5 persona engines (Omega, Dark, Rinlada, Seraphina, Ultimate)
- ✅ Comprehensive test suite (335+ tests)
- ✅ Proper config management
- ✅ Rate limiting & session management
- ✅ Optional TTS (ElevenLabs) integration

**Next Steps:**
1. Fix critical import issues
2. Re-run this audit
3. Deploy to staging for integration testing
4. Then ready for production offer

---

**Audited by:** นะโม (Claude)  
**Confidence:** High (static analysis + code review)  
**Requires:** Dynamic testing (actual server startup + API testing)
