@echo off
echo ====================================
echo    DPI Program Build Script
echo ====================================
echo.

REM Proje dizinine git
cd "NetLan-Guardian-main"

REM Sanal ortamı aktif et (varsa)
if exist ".venv\Scripts\activate.bat" (
    echo Sanal ortam aktif ediliyor...
    call .venv\Scripts\activate.bat
) else (
    echo Uyari: Sanal ortam bulunamadi, sistem Python kullanilacak
)

echo.
echo ====================================
echo    EXE Build Baslatiliyor...
echo ====================================
echo.

REM build_exe.spec dosyasını build et
pyinstaller build_exe.spec --clean

if %ERRORLEVEL% NEQ 0 (
    echo HATA: EXE build islemi basarisiz!
    pause
    exit /b 1
)

echo.
echo ====================================
echo    Portable Build Baslatiliyor...
echo ====================================
echo.

REM build_portable.spec dosyasını build et
pyinstaller build_portable.spec --clean

if %ERRORLEVEL% NEQ 0 (
    echo HATA: Portable build islemi basarisiz!
    pause
    exit /b 1
)

echo.
echo ====================================
echo    Build Islemi Tamamlandi!
echo ====================================
echo.
echo Build dosyalari:
if exist "dist\NetLanGuardian.exe" (
    echo - EXE: dist\NetLanGuardian.exe
) else (
    echo - EXE build dosyasi bulunamadi!
)

if exist "dist\NetLanGuardian_Portable.exe" (
    echo - Portable: dist\NetLanGuardian_Portable.exe
) else (
    echo - Portable build dosyasi bulunamadi!
)

echo.
echo Build klasor yapisini gormek icin dist\ klasorune bakin.
echo.
pause
