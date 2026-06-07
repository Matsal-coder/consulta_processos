@echo off
set TASK_NAME=JuriScan Monitoramento
set BAT_PATH=%~dp0..\scripts\run_email_report.bat

echo Instalando tarefa agendada: %TASK_NAME%
echo Script: %BAT_PATH%

schtasks /Create ^
 /TN "%TASK_NAME%" ^
 /TR "\"%BAT_PATH%\"" ^
 /SC DAILY ^
 /ST 08:00 ^
 /F

echo.
echo Tarefa instalada.
pause