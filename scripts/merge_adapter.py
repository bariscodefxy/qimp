#!/usr/bin/env python
from pathlib import Path
import argparse

from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--base-model", required=True)
    p.add_argument("--adapter", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    base = AutoModelForCausalLM.from_pretrained(args.base_model, device_map="auto")
    model = PeftModel.from_pretrained(base, args.adapter)
    merged = model.merge_and_unload()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(out_dir)
    tok = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
    tok.save_pretrained(out_dir)

    print(f"Merged model written to {out_dir}")


if __name__ == "__main__":
    main()
