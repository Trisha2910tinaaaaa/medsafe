@echo off
echo 💊 MedSafe - AI-Powered Prescription Verification System
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Create virtual environment if it doesn't exist
if not exist "medsafe-env" (
    echo 📦 Creating virtual environment...
    python -m venv medsafe-env
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo 📦 Installing dependencies...
call medsafe-env\Scripts\activate
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo 🎯 Starting MedSafe System...
echo 📋 Backend will run on: http://localhost:8000
echo 🌐 Frontend will run on: http://localhost:8501
echo 📖 API Documentation: http://localhost:8000/docs
echo.
echo ⏳ Starting services...
echo.

REM Start the system
python run_medsafe.py

pause
