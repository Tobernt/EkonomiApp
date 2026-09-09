@echo off
setlocal
cd /d "%~dp0"
echo Startar Budgethanteringssystemet...

if not exist .venv\Scripts\python.exe (
    python -m venv .venv
    if errorlevel 1 exit /b 1
)

.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe setup_local.py
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m waitress --host=localhost --port=8000 wsgi:app
