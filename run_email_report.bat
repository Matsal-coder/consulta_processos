@echo off
cd /d "%~dp0"

call .venv\Scripts\activate.bat

python -m consulta_processos.jobs.email_monitorados_report

pause