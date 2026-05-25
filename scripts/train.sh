#!/usr/bin/env bash
set -euo pipefail

echo "=== Qimp Türkçe Linux Asistanı - Eğitim ==="
echo ""

# 1. Ortam
source .venv/bin/activate

# 2. Dataset hazırlık
echo "[1/3] Dataset hazırlanıyor..."
python scripts/prepare_dataset.py \
  --raw data/raw/tr_linux_instructions.jsonl \
  --out data/processed/train.jsonl

# 3. Eğitim
echo "[2/3] QLoRA eğitimi başlıyor..."
echo "    Model: Qwen/Qwen2.5-1.5B-Instruct"
echo "    Örnek sayısı: $(wc -l < data/processed/train.jsonl)"
echo ""

python scripts/train_lora.py --config configs/train_lora.yaml

echo ""
echo "[3/3] Eğitim tamamlandı!"
echo "    Adapter: outputs/qimp-lora/"

# 4. Merge + GGUF için bilgi
echo ""
echo "=== Sonraki adımlar ==="
echo ""
echo "1. Adapter'ı base modele göm:"
echo "   python scripts/merge_adapter.py \\"
echo "     --base-model Qwen/Qwen2.5-1.5B-Instruct \\"
echo "     --adapter outputs/qimp-lora \\"
echo "     --out outputs/qimp-merged"
echo ""
echo "2. GGUF'a çevir:"
echo "   git clone https://github.com/ggerganov/llama.cpp"
echo "   cd llama.cpp && make"
echo "   python convert_hf_to_gguf.py ../qimp/outputs/qimp-merged \\"
echo "     --outfile ../qimp/outputs/qimp-tr.gguf"
echo ""
echo "3. Ollama'ya yükle:"
echo "   ollama create qimp-tr -f Modelfile.qimp"
echo "   ollama run qimp-tr"
