@echo off
REM Syntax checking script
REM Validates Python code before deployment

echo Helmet Detection System - Code Quality Check
echo =====================================================
echo.

if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo [1/3] Checking Python syntax...
for /r backend %%f in (*.py) do (
    python -m py_compile "%%f"
    if errorlevel 1 (
        echo ERROR in %%f
        pause
        exit /b 1
    )
)
echo OK: All Python files have valid syntax
echo.

echo [2/3] Running Flake8 linter...
flake8 backend --max-line-length=120 --ignore=E501,W503
echo.

echo [3/3] Running Black formatter check...
black backend --check --line-length=120
echo.

echo =====================================================
echo Code quality check complete!
echo =====================================================
pause
