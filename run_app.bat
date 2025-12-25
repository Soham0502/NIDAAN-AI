@echo off
:: FORCE script to run from its own folder (Fixes "file not found" error)
cd /d "%~dp0"

echo ========================================================
echo   STARTING NIDAAN-AI SYSTEM
echo ========================================================

:: 1. Start the Backend in a new separate window
echo Starting Python Backend Server...
start "NIDAAN Backend" cmd /k "uvicorn main:app --reload"

:: 2. Wait 5 seconds (Using ping hack because timeout fails in some terminals)
echo Waiting for server to wake up...
ping 127.0.0.1 -n 6 > nul

:: 3. Open the Frontend
echo Opening Frontend...
if exist index.html (
    start index.html
) else (
    echo.
    echo [ERROR] Could not find index.html!
    echo Please make sure index.html is in this folder:
    echo %CD%
    echo.
    echo Trying to open chat.html instead...
    if exist chat.html start chat.html
)

echo.
echo ========================================================
echo   SYSTEM RUNNING
echo   - Backend: http://127.0.0.1:8000
echo   - Frontend: Check your browser
echo ========================================================
pause