@echo off

cd /d "%~dp0.."

call .venv\Scripts\activate.bat

uvicorn consulta_processos.api:app --reload

pause