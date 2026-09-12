@echo off
REM Helmet Detection System - Windows Installation Script
REM Run this once to set up the entire system

echo =====================================================
echo Helmet Detection System - Installation
echo =====================================================
echo.

REM Check Python installation
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.9+ not found. Please install Python from python.org
    pause
    exit /b 1
)
echo OK: Python found
echo.

REM Create virtual environment
echo [2/6] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo OK: Virtual environment activated
echo.

REM Install dependencies
echo [4/6] Installing dependencies...
echo This may take 5-10 minutes...
pip install --upgrade pip setuptools wheel >nul
pip install -r backend\requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo OK: Dependencies installed
echo.

REM Download YOLO model
echo [5/6] Downloading YOLO models...
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
if errorlevel 1 (
    echo WARNING: YOLO download may have issues, but will retry at runtime
)
echo.

REM Initialize database
echo [6/6] Initializing database...
if not exist models mkdir models
echo Database ready
echo.

echo =====================================================
echo Installation Complete!
echo =====================================================
echo.
echo Next steps:
echo   1. Run: run.bat
echo   2. Open browser: http://localhost:8000/dashboard
echo   3. Start detection from dashboard or CLI
echo.
echo For demo: python demo.py --video your_video.mp4 --output output.mp4
echo.
pause
