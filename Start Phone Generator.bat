@echo off
cd /d "%~dp0"
if exist "dist\PhoneNumberGenerator\PhoneNumberGenerator.exe" (
    start "" "dist\PhoneNumberGenerator\PhoneNumberGenerator.exe"
    exit /b
)
set "PYTHONPATH=%~dp0src"
python -m phone_generator
if errorlevel 1 (
    echo Install Python 3.11 or newer from python.org, including Tcl/Tk and Add to PATH.
    pause
)
