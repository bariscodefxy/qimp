#!/usr/bin/env python
import argparse

from qimp.inference import load_inference_config, run_inference


def main() -> None:
    p = argparse.ArgumentParser(description="Qimp Türkçe Linux asistanı — çıkarım")
    p.add_argument("--config", default="configs/inference.yaml")
    p.add_argument("--görev", required=True, help="Yapılacak iş / sorulacak soru")
    p.add_argument("--dağıtım", default=None, help="Hedef dağıtım (pardus 24, debian 12, ...)")
    p.add_argument("--bağlam", default=None, help="Ek bağlam bilgisi")
    args = p.parse_args()

    cfg = load_inference_config(args.config)
    output = run_inference(cfg, task=args.görev, distro=args.dağıtım, context=args.bağlam)
    print(output)


if __name__ == "__main__":
    main()
