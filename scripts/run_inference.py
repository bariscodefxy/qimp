#!/usr/bin/env python
import argparse

from qimp.inference import load_inference_config, run_inference


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="configs/inference.yaml")
    p.add_argument("--task", required=True)
    p.add_argument("--distro", default=None)
    p.add_argument("--context", default=None)
    args = p.parse_args()

    cfg = load_inference_config(args.config)
    output = run_inference(cfg, task=args.task, distro=args.distro, context=args.context)
    print(output)


if __name__ == "__main__":
    main()
