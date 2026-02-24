@echo off
IF EXIST .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --app-dir backend
