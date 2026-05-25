#!/usr/bin/env python
"""Türkçe Pardus/Linux Q&A dataset'i üret — DeepSeek API ile."""

import json
import os
import re
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("DEEPSEEK_API_KEY")
if not API_KEY:
    raise SystemExit("DEEPSEEK_API_KEY .env içinde tanımlı değil.")

API_URL = "https://api.deepseek.com/v1/chat/completions"

TOPICS = [
    "apt paket kurulumu, güncelleme ve kaldırma",
    "apt repository ekleme ve yönetme",
    "dpkg ile .deb paket kurulumu",
    "Pardus paket yöneticisi kullanımı",
    "systemd servisleri başlatma, durdurma ve etkinleştirme",
    "systemctl ile servis durumu sorgulama",
    "journalctl ile log okuma ve filtreleme",
    "Linux dosya izinleri (chmod, chown, chgrp)",
    "disk kullanımı sorgulama (df, du, lsblk)",
    "disk bölümleme ve mount işlemleri",
    "ağ yapılandırması (ip, nmcli, netplan)",
    "SSH bağlantısı ve güvenliği",
    "firewall yönetimi (ufw, iptables, nftables)",
    "kullanıcı ekleme, silme ve yönetme",
    "sudo ve yetki yönetimi",
    "grup oluşturma ve kullanıcı atama",
    "güvenlik güncellemeleri ve yamalama",
    "log denetimi ve güvenlik taraması",
    "dosya bütünlüğü kontrolü (aide, tripwire)",
    "LUKS ile disk şifreleme",
    "sistem performans sorunlarını teşhis etme",
    "ağ bağlantı sorunlarını giderme",
    "servis çökme sorunlarını analiz etme",
    "kernel logları ve hata ayıklama",
    "Docker kurulumu ve temel komutlar",
    "Docker Compose ile çoklu konteyner yönetimi",
    "konteyner logları ve sorun giderme",
    "bash betik yazma temelleri",
    "grep, sed, awk ile metin işleme",
    "cron ile görev zamanlama",
    "Pardus 24 kurulum sonrası yapılacaklar",
    "Pardus'ta varsayılan uygulamalar",
    "Pardus güncelleme politikası",
    "Pardus depoları ve paket kaynakları",
    "Pardus'ta donanım sürücüsü kurulumu",
    "Pardus MATE/ XFCE masaüstü özelleştirme",
]

SYSTEM_PROMPT = """Sen bir Linux uzmanısın. Türkçe soru-cevap çiftleri üretiyorsun.

Her bir çift JSON formatında olmalı:
{
  "instruction": "Kullanıcının sorduğu soru veya yapmak istediği işlem (Türkçe)",
  "response": "Adım adım açıklama, komutlar ve uyarılar (Türkçe)",
  "context": "Gerekli bağlam bilgisi (opsiyonel)",
  "distro": "Hedef dağıtım (pardus 24, debian 12, ubuntu 24.04, genel)",
  "risk_level": "low | medium | high",
  "tags": ["etiket1", "etiket2"],
  "commands": [
    {"cmd": "komut", "destructive": false, "requires_confirmation": false}
  ]
}

Kurallar:
- Yanıtlar mutlaka Türkçe olmalı.
- Riskli komutlar (rm -rf, chmod 777, userdel, mkfs, firewall disable) için mutlaka uyarı ekle.
- Önce salt-okunur tanılama komutları öner, sonra değişiklik yapan komutları.
- Varsayımlarını belirt (dağıtım, sürüm bilinmiyorsa "varsayalım" de).
- JSON dışında hiçbir şey yazma, sadece geçerli bir JSON dizisi döndür."""


def extract_json_objects(text: str) -> list[dict]:
    """Metin içinden geçerli JSON objelerini ayıkla."""
    results = []
    # Önce tüm içeriği bir JSON dizisi olarak dene
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned.split("```json", 1)[1]
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 1)[1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    cleaned = cleaned.strip()

    # Tamamı geçerli bir JSON dizisi mi?
    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
    except json.JSONDecodeError:
        pass

    # Tek tek süslü parantez bloklarını dene
    depth = 0
    start = -1
    for i, ch in enumerate(cleaned):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                block = cleaned[start:i+1]
                start = -1
                try:
                    obj = json.loads(block)
                    if isinstance(obj, dict):
                        results.append(obj)
                except json.JSONDecodeError:
                    pass
    return results


def generate_for_topic(topic: str, retries: int = 2) -> list[dict]:
    last_error = None
    for attempt in range(retries + 1):
        try:
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f'Aşağıdaki konuyla ilgili 5 adet Türkçe Linux/Pardus soru-cevap çifti üret:\n\nKonu: {topic}\n\nHer çift JSON formatında olsun. Sadece geçerli bir JSON dizisi döndür, başka metin yazma.'}
                ],
                "temperature": 0.7,
                "max_tokens": 4096,
            }

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            }

            resp = requests.post(API_URL, json=payload, headers=headers, timeout=120)
            data = resp.json()

            if not resp.ok:
                err = data.get("error", {}).get("message", str(resp.status_code))
                raise RuntimeError(f"API hatası: {err}")

            content = data["choices"][0]["message"]["content"]
            examples = extract_json_objects(content)

            if not examples:
                raise RuntimeError("JSON objesi bulunamadı")

            return examples

        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(3)
            continue

    raise RuntimeError(f"Tüm denemeler başarısız: {last_error}")


def main() -> None:
    out_path = Path("data/raw/tr_linux_instructions.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    for i, topic in enumerate(TOPICS, 1):
        print(f"[{i}/{len(TOPICS)}] {topic}...", end=" ", flush=True)
        try:
            examples = generate_for_topic(topic)
            with out_path.open("a", encoding="utf-8") as f:
                for ex in examples:
                    f.write(json.dumps(ex, ensure_ascii=False) + "\n")
            total += len(examples)
            print(f"{len(examples)} örnek")
        except Exception as e:
            print(f"HATA: {e}")
        time.sleep(1)

    print(f"\nToplam {total} örnek -> {out_path}")
    print(f"Komut: wc -l {out_path}")


if __name__ == "__main__":
    main()
