# 🤖 NaMo Model Fine-Tuning & Alignment Roadmap (Week 4 Plan)
## SFT (Supervised Fine-Tuning) & DPO (Direct Preference Optimization)

This document outlines the technical fine-tuning execution plan for training the proprietary **NaMo Sovereign Narrative Model** using the Golden Dataset exported from the HITL Data Pipeline.

---

## 🎯 1. Base Model Selection & Rationale

| Model Candidate | Parameter Count | Strengths | Context Window | Target Framework |
|---|---|---|---|---|
| **Qwen2.5-7B-Instruct** *(Recommended)* | 7.6B | Exceptional Thai language fluency, strong instruction following, dense literary tone. | 32k / 128k | Unsloth (4-bit QLoRA) |
| **Llama-3.1-8B-Instruct** | 8.0B | Strong reasoning, broad open-weights ecosystem, great DPO alignment response. | 128k | Axolotl / Unsloth |

---

## 🛠️ 2. Training Architecture & Stack

- **Tooling:** **Unsloth AI** (Faster 2x LoRA fine-tuning with 60% memory reduction).
- **Quantization:** 4-bit NormalFloat (NF4) base model quantization.
- **LoRA Parameters:**
  - `r = 16` (Rank)
  - `lora_alpha = 32`
  - `target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]`
  - `lora_dropout = 0.05`

---

## 📋 3. Two-Stage Training Pipeline

### Stage 1: SFT (Supervised Fine-Tuning)
- **Input File:** `core/datasets/namo_golden_dataset_chatml.jsonl`
- **System Prompt:** `"คุณคือผู้เชี่ยวชาญด้านการเขียน Erotic Literary Realism เน้น 90% Tension / 10% Action"`
- **Hyperparameters:**
  - `learning_rate = 2e-4`
  - `epochs = 3`
  - `batch_size = 4` (with gradient accumulation steps = 4)
  - `lr_scheduler_type = "cosine"`

### Stage 2: DPO (Direct Preference Optimization)
- **Input File:** `core/datasets/namo_golden_dataset_dpo.jsonl`
- **Goal:** Align model to prefer slow-burn tension, micro-sensory details, and consent over rushed/uncensored crude text.
- **Hyperparameters:**
  - `beta = 0.1`
  - `learning_rate = 5e-5`
  - `epochs = 1`

---

## 🛡️ 4. Fallback Strategy
If fine-tuned weights exhibit style drift or pacing degeneration during validation:
1. **RAG-First Hybrid Fallback:** Revert to base model with Dynamic Lorebook RAG injection (`namo_golden_dataset.jsonl`).
2. **Few-Shot Prompt Engineering:** Prepend 3 high-quality golden ChatML examples directly into system context.
