@echo off
setlocal

echo Limpando builds anteriores...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo Gerando executavel JuriScan...
python -m PyInstaller JuriScan.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ERRO: build falhou.
    pause
    exit /b 1
)

echo.
echo Build finalizado.
echo Saida: dist\JuriScan\JuriScan.exe

pause
endlocal