# Fine-Tuning Execution Code for Unsloth / HuggingFace TRL
import torch
from datasets import load_dataset
from transformers import TrainingArguments
from trl import SFTTrainer
from unsloth import FastLanguageModel

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
sft_dataset = load_dataset(
    "json", data_files="core/datasets/namo_golden_dataset_chatml.jsonl", split="train"
)

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
