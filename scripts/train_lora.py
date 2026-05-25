#!/usr/bin/env python
from pathlib import Path
import argparse

from qimp.train import load_train_config, run_train


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="configs/train_lora.yaml")
    args = p.parse_args()

    cfg = load_train_config(Path(args.config))
    run_train(cfg)


if __name__ == "__main__":
    main()
