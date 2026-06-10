@echo off
setlocal

echo Gerando build do JuriScan...
call scripts\build_windows.bat

if errorlevel 1 (
    echo.
    echo ERRO: build do executavel falhou.
    pause
    exit /b 1
)

echo.
echo Criando pacote zip...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Compress-Archive -Path 'dist\JuriScan' -DestinationPath 'dist\JuriScan-portable.zip' -Force"

if errorlevel 1 (
    echo.
    echo ERRO: criacao do zip falhou.
    pause
    exit /b 1
)

echo.
echo Pacote criado:
echo dist\JuriScan-portable.zip

pause
endlocal