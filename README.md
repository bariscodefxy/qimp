# Qimp

Qimp is a Linux-focused, safety-aware technical assistant fine-tuned with LoRA/PEFT.

## Scope

- Linux administration and troubleshooting
- Security hardening and safe operations
- Networking, systemd/services, logs, package management
- Containers and performance triage

## Quickstart

1. Install dependencies.
2. Prepare dataset.
3. Train LoRA adapter.
4. Run inference.
5. Evaluate outputs.

```bash
pip install -r requirements.txt
python scripts/prepare_dataset.py --raw data/samples/linux_instructions.jsonl --out data/processed/train.jsonl
python scripts/train_lora.py --config configs/train_lora.yaml
python scripts/run_inference.py --config configs/inference.yaml --task "Diagnose failing ssh service" --distro "ubuntu 24.04"
python scripts/evaluate.py --config configs/eval.yaml
```

## Safety posture

Qimp warns before destructive commands, prefers diagnostics before mutation, states assumptions, and calls out distro differences when relevant.
