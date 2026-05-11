#!/usr/bin/env python
from pathlib import Path
import argparse
import json

from qimp.evals import evaluate_responses, load_eval_config


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="configs/eval.yaml")
    args = p.parse_args()

    cfg = load_eval_config(Path(args.config))
    records = _read_jsonl(Path(cfg.eval_file))
    result = evaluate_responses(records)

    out = Path(cfg.output_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
