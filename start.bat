@echo off
echo Starting Flask server...
echo.

python main.py

echo.
echo Flask server stopped or crashed.
echo Exit code: %ERRORLEVEL%
echo.

pause