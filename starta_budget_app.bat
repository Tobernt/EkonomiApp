@echo off
echo Startar Budgethanteringssystemet...

REM Activate virtual environment (create if missing)
if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate

REM Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

REM Run the app with Waitress (production WSGI server)
python -m waitress --host=0.0.0.0 --port=8000 wsgi:app

pause
