@echo off
:: Kontrollera att Python är installerat
where python >nul 2>nul
if errorlevel 1 (
    echo Python finns inte installerat eller inte i PATH.
    pause
    exit /b
)

:: Installera krav (requirements)
echo Installerar beroenden...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

:: Kör lösenordsgeneratorn
echo Startar lösenordsgenerator...
python Losenord_generator.py

pause
