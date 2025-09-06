@echo off
REM DPI Bypass Tool - Windows Başlatıcı
REM Bu script'i yönetici olarak çalıştırın

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                  DPI BYPASS TOOL                            ║
echo ║              Windows Başlatıcı                              ║
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

REM Gereksinimleri yükle
echo 🔧 Gereksinimler kontrol ediliyor ve yükleniyor...
pip install -r requirements.txt

echo.
echo 🚀 DPI Bypass Tool başlatılıyor...
echo.

REM Ana programı çalıştır
python main.py

echo.
echo 📄 Program sonlandı. Herhangi bir tuşa basarak çıkış yapabilirsiniz.
pause
