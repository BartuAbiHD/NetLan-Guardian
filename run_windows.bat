@echo off
REM DPI Bypass Tool - Windows Başlatıcı (Geliştirilmiş)
REM Bu script'i yönetici olarak çalıştırın

chcp 65001 > nul

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                  DPI BYPASS TOOL                            ║
echo ║          Windows Başlatıcı (Geliştirilmiş)                 ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Yönetici izni kontrolü
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Bu script yönetici izniyle çalıştırılmalıdır!
    echo    Sağ tıklayıp "Yönetici olarak çalıştır" seçeneğini kullanın.
    pause
    exit /b 1
)

echo ✅ Yönetici izni doğrulandı

REM Python kontrolü
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python kurulu değil veya PATH'de bulunamıyor!
    echo    https://python.org adresinden Python yükleyin.
    pause
    exit /b 1
)

echo ✅ Python doğrulandı

REM Virtual environment kontrolü ve aktivasyon
if not exist ".venv" (
    echo 🔧 Virtual environment oluşturuluyor...
    python -m venv .venv
)

echo 🔧 Virtual environment aktivasyonu...
call .venv\Scripts\activate.bat

REM Windows için özel gereksinimler yükle
echo 🔧 Windows uyumlu paketleri yükleniyor...
pip install --upgrade pip
pip install scapy psutil requests colorama pyyaml pywin32 wintun

echo.
echo 🚀 DPI Bypass Tool başlatılıyor...
echo.

REM Ana programı çalıştır
python main.py

echo.
echo 📄 Program sonlandı. Herhangi bir tuşa basarak çıkış yapabilirsiniz.
pause
