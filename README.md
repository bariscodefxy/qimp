# Qimp — Türkçe Linux Asistanı

Qimp, Linux odaklı, güvenlik bilincine sahip bir teknik asistandır. LoRA/PEFT ile ince ayar yapılmıştır.

## Kapsam

- Linux yönetimi ve sorun giderme
- Güvenlik sağlamlaştırma ve güvenli işlemler
- Ağ, systemd/servisler, loglar, paket yönetimi
- Konteynerler ve performans triyajı
- Pardus, Debian, Ubuntu ve türevi dağıtımlar

## Hızlı başlangıç

```bash
pip install -r requirements.txt
python scripts/generate_dataset.py                    # DeepSeek API ile Türkçe dataset üret
python scripts/prepare_dataset.py --raw data/raw/tr_linux_instructions.jsonl --out data/processed/train.jsonl
python scripts/train_lora.py --config configs/train_lora.yaml
python scripts/run_inference.py --config configs/inference.yaml --görev "SSH servisi neden başlamıyor?" --dağıtım "pardus 24"
python scripts/evaluate.py --config configs/eval.yaml
```

## Güvenlik duruşu

Qimp, yıkıcı komutlardan önce uyarır, değişiklikten önce tanılamayı tercih eder, varsayımları belirtir ve gerektiğinde dağıtım farklılıklarını vurgular.
