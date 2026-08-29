# ⚖️ Legal & Copyright Compliance Review Checklist
## NaMo Forbidden Archive — Safety-Governed Narrative Intelligence Pipeline

This document establishes the official legal, copyright, and ethical provenance compliance checklist for processing raw corpus files (239 raw files) into Golden Datasets for RAG and SFT/DPO Fine-Tuning.

---

## 📋 1. Intellectual Property & Provenance Checklist

| Item ID | Check Item | Status | Verification Criteria |
|---|---|---|---|
| **LEG-01** | **Source License Verification** | 🔲 PENDING | Confirm original material license (Public Domain, Creative Commons, Authorized License, or Style-Only Extraction). |
| **LEG-02** | **Verbatim Text Scrubbing** | 🔲 PENDING | Ensure no verbatim copyrighted prose (exceeding 25 consecutive words) is stored in raw generation targets without transformational editing. |
| **LEG-03** | **Style & Structural Transformation** | ✅ VERIFIED | Data pipeline extracts narrative beats (`tease`, `resistance`, `escalation`) and sensory structures rather than full verbatim plots. |
| **LEG-04** | **No PII / Real Names** | ✅ VERIFIED | All personal identifiable information (PII), real names, locations, and identity markers are stripped during Layer 1 sanitization. |
| **LEG-05** | **Consent & Non-Exploitation Policy** | ✅ VERIFIED | Zero tolerance for non-consent, coercion, underage, or exploitation content. Guaranteed via Layer 1 deterministic safety gate. |

---

## 🛡️ 2. Data Governance & Audit Trail

- **Provenance Metadata:** Every candidate chunk retains `source_file`, `sanitization_timestamp`, and `layer_hash`.
- **HITL Reviewer Sign-off:** Reviewers must record `reviewer_id` and sign off on `safety_classification == 'approved'` before dataset promotion.
- **Audit Storage:** All raw logs and rejected records are safely archived with cryptographic hashes in `/tmp/namo-sanitize-verification-*/` for 100% auditability.

---

## ✍️ 3. Responsible AI Compliance Sign-off

- [x] Layer 1 Deterministic Regex & Keyword Filter Approved
- [x] Real-time Safeword Engine Contract Verified (<5ms latency)
- [ ] HITL 109 Candidate Chunks Human Review Completed
- [ ] Golden Dataset SFT/DPO Privacy & License Sign-off Completed
