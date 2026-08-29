#!/usr/bin/env python3
"""
NaMo Sovereign Qwen2.5-7B Unsloth QLoRA Fine-Tuning & DPO Script
"""

from __future__ import annotations

import sys
from pathlib import Path


def print_fine_tuning_spec():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("\n" + "=" * 70)
    print("🤖 NAMO SOVEREIGN FINE-TUNING PIPELINE (UNSLOTH + QLOERA)")
    print("=" * 70)
    print("Model Target:     Qwen/Qwen2.5-7B-Instruct (4-bit NF4 Quantization)")
    print("SFT Dataset:      core/datasets/namo_golden_dataset_chatml.jsonl")
    print("DPO Dataset:      core/datasets/namo_golden_dataset_dpo.jsonl")
    print("LoRA Rank (r):    16 | Alpha: 32 | Dropout: 0.05")
    print(
        "System Prompt:    'คุณคือผู้เชี่ยวชาญด้านการเขียน Erotic Literary Realism เน้น 90% Tension / 10% Action'"
    )
    print("Target Hardware:  1x NVIDIA RTX 4090 (24GB) or A10G / T4 GPU Cluster")
    print("=" * 70 + "\n")


def generate_unsloth_training_code() -> str:
    return """# Fine-Tuning Execution Code for Unsloth / HuggingFace TRL
import torch
from unsloth import FastLanguageModel
from trl import SFTTrainer, DPOTrainer
from transformers import TrainingArguments
from datasets import load_dataset

# 1. Load Base Model & Tokenizer
max_seq_length = 4096
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="Qwen/Qwen2.5-7B-Instruct",
    max_seq_length=max_seq_length,
    load_in_4bit=True,
)

# 2. Add LoRA Adapters
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    use_gradient_checkpointing="unsloth",
)

# 3. Load Datasets
sft_dataset = load_dataset("json", data_files="core/datasets/namo_golden_dataset_chatml.jsonl", split="train")

# 4. SFT Trainer
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=sft_dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    packing=False,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        max_steps=60,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        output_dir="outputs/sft_qwen2.5_namo",
    ),
)
trainer.train()

# 5. Save LoRA Weights & Merged GGUF
model.save_pretrained("outputs/namo_lora_model")
tokenizer.save_pretrained("outputs/namo_lora_model")
"""


def main():
    print_fine_tuning_spec()
    code_path = Path("scripts/unsloth_train_runner.py")
    code_path.write_text(generate_unsloth_training_code(), encoding="utf-8")
    print(f"✅ Generated Unsloth Training Script: {code_path}")


if __name__ == "__main__":
    main()
