from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import torch
import yaml
from datasets import load_dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer


@dataclass
class TrainConfig:
    base_model: str
    train_file: str
    output_dir: str
    max_seq_length: int
    lora_r: int
    lora_alpha: int
    lora_dropout: float
    learning_rate: float
    num_train_epochs: float
    per_device_train_batch_size: int
    gradient_accumulation_steps: int
    logging_steps: int
    save_steps: int


def load_train_config(path: Path) -> TrainConfig:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return TrainConfig(**raw)


def run_train(config: TrainConfig) -> None:
    use_cuda = torch.cuda.is_available()
    device_map = "auto" if use_cuda else "cpu"

    if use_cuda:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        quantization_config = bnb_config
    else:
        quantization_config = None
        print("CUDA yok, CPU'da çalışıyor (yavaş olabilir)")

    tokenizer = AutoTokenizer.from_pretrained(config.base_model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        config.base_model,
        quantization_config=quantization_config,
        device_map=device_map,
        trust_remote_code=True,
        dtype=torch.bfloat16 if use_cuda else torch.float32,
        attn_implementation="eager",
    )

    dataset = load_dataset("json", data_files={"train": config.train_file})["train"]

    peft_config = LoraConfig(
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )

    sft_config = SFTConfig(
        output_dir=config.output_dir,
        learning_rate=config.learning_rate,
        num_train_epochs=config.num_train_epochs,
        per_device_train_batch_size=config.per_device_train_batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        logging_steps=config.logging_steps,
        save_steps=config.save_steps,
        max_length=config.max_seq_length,
        bf16=use_cuda,
        fp16=False,
        report_to="none",
        dataset_text_field="text",
    )

    def to_text(record: dict) -> dict:
        msgs = record["messages"]
        text = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)
        return {"text": text}

    train_ds = dataset.map(to_text, remove_columns=dataset.column_names)

    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=train_ds,
        peft_config=peft_config,
        args=sft_config,
    )
    trainer.train()
    trainer.model.save_pretrained(config.output_dir)
    tokenizer.save_pretrained(config.output_dir)
