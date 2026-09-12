@echo off
REM Quick demo script
REM Usage: demo.bat <video_file>

if "%1"==" " (
    echo Usage: demo.bat ^<video_file^>
    echo Example: demo.bat construction_footage.mp4
    pause
    exit /b 1
)

if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo.
echo Processing video: %1
echo Output will be saved to output/ directory
echo.

python demo.py --video "%1" --output output\annotated.mp4 --report-dir output

echo.
echo Demo complete! Results saved to output/
echo   - output\annotated.mp4 (annotated video)
echo   - output\events.csv (event log)
echo   - output\statistics.json (analytics)
echo.
pause
