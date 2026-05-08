@echo off

call .venv\Scripts\activate

uvicorn consulta_processos.api:app --reload

pause