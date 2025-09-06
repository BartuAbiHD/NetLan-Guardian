#!/bin/bash

# DPI Bypass Tool - Linux/macOS Başlatıcı
# Bu script'i sudo ile çalıştırın

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  DPI BYPASS TOOL                            ║"
echo "║              Linux/macOS Başlatıcı                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Root izni kontrolü
if [[ $EUID -ne 0 ]]; then
    echo "❌ Bu script root izniyle çalıştırılmalıdır!"
    echo "   sudo ./run.sh komutuyla çalıştırın."
    exit 1
fi

echo "✅ Root izni doğrulandı"

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 kurulu değil!"
    echo "   Paket yöneticinizle Python3 yükleyin."
    exit 1
fi

echo "✅ Python3 doğrulandı"

# Virtual environment kontrolü ve oluşturma
if [ ! -d ".venv" ]; then
    echo "🔧 Virtual environment oluşturuluyor..."
    python3 -m venv .venv
fi

echo "🔧 Virtual environment aktivasyonu..."
source .venv/bin/activate

# Gereksinimleri yükle
echo "🔧 Gereksinimler kontrol ediliyor ve yükleniyor..."
pip install -r requirements.txt

echo ""
echo "🚀 DPI Bypass Tool başlatılıyor..."
echo ""

# Ana programı çalıştır
python main.py

echo ""
echo "📄 Program sonlandı."
