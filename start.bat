@echo off
title Google Maps Business Scraper & WhatsApp Messenger
color 0A

echo.
echo ========================================
echo  Google Maps Business Scraper Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo [INFO] Python found
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo [INFO] Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install requirements
    pause
    exit /b 1
)

REM Create necessary directories
if not exist "csv_files" mkdir csv_files
if not exist "custom_searches" mkdir custom_searches

echo.
echo [SUCCESS] Setup completed!
echo [INFO] Starting application...
echo.
echo ========================================
echo  Application is starting...
echo  Open your browser and go to:
echo  http://localhost:8501
echo ========================================
echo.

REM Start the application
streamlit run app.py

pause