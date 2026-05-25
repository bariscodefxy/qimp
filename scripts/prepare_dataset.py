#!/usr/bin/env python
from pathlib import Path
import argparse

from qimp.data import prepare_dataset
from qimp.prompts import QIMP_SYSTEM_PROMPT


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--raw", required=True, help="Path to raw JSONL")
    p.add_argument("--out", required=True, help="Path to processed JSONL")
    args = p.parse_args()

    count = prepare_dataset(Path(args.raw), Path(args.out), QIMP_SYSTEM_PROMPT)
    print(f"Prepared {count} examples -> {args.out}")


if __name__ == "__main__":
    main()
