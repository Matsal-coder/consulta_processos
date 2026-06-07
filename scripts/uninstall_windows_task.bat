@echo off
set TASK_NAME=JuriScan Monitoramento

echo Removendo tarefa agendada: %TASK_NAME%

schtasks /Delete ^
 /TN "%TASK_NAME%" ^
 /F

echo.
echo Tarefa removida.
pause