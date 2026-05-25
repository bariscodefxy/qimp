from __future__ import annotations

from dataclasses import dataclass

import torch
import yaml
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from qimp.prompts import QIMP_SYSTEM_PROMPT, build_user_prompt
from qimp.safety import assess_commands


@dataclass
class InferenceConfig:
    base_model: str
    adapter_path: str
    max_new_tokens: int
    temperature: float
    top_p: float


def load_inference_config(path: str) -> InferenceConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return InferenceConfig(**raw)


def run_inference(config: InferenceConfig, task: str, distro: str | None = None, context: str | None = None) -> str:
    tokenizer = AutoTokenizer.from_pretrained(config.base_model, use_fast=True)
    base = AutoModelForCausalLM.from_pretrained(
        config.base_model,
        device_map="auto",
        dtype=torch.bfloat16,
        trust_remote_code=True,
        attn_implementation="eager",
    )
    model = PeftModel.from_pretrained(base, config.adapter_path)

    messages = [
        {"role": "system", "content": QIMP_SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(task=task, context=context, distro=distro)},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=config.max_new_tokens,
            temperature=config.temperature,
            top_p=config.top_p,
            do_sample=True,
        )

    decoded = tokenizer.decode(out[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
    findings = assess_commands(decoded)
    if findings:
        warnings = "\n".join([f"[RİSK:{f.risk}] {f.command} ({f.reason})" for f in findings])
        return decoded.strip() + "\n\nGüvenlik uyarıları:\n" + warnings
    return decoded.strip()
