@echo off
REM Helmet Detection System - Windows Run Script
REM Execute this to start the system

echo =====================================================
echo Helmet Detection System - Starting Backend
echo =====================================================
echo.

REM Activate virtual environment
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo.
echo Starting FastAPI server...
echo Access dashboard at: http://localhost:8000/dashboard
echo Press Ctrl+C to stop
echo.

cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

pause
