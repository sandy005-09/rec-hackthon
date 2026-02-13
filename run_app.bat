@echo off
echo ==================================================
echo      GenAI Financial Assistant - Launcher
echo ==================================================

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please download and install Python from: https://www.python.org/downloads/
    echo ensuring you check "Add Python to PATH" during installation.
    pause
    exit /b
)

:: Check for .env
if not exist .env (
    echo [WARNING] .env file not found! Creating one...
    echo GOOGLE_API_KEY=your_key_here > .env
    echo Please edit .env and add your valid GOOGLE_API_KEY.
    notepad .env
    pause
    exit /b
)

:: Check API Key (Simple check)
findstr "your_key_here" .env >nul
if %errorlevel% eq 0 (
    echo [WARNING] You still have the placeholder API Key.
    echo Please update the .env file with your actual Gemini API Key.
    notepad .env
    echo Press any key once you have saved the file...
    pause
)

:: Install Dependencies
echo.
echo [INFO] Installing required libraries...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b
)

:: Run Server
echo.
echo [SUCCESS] Starting the Financial Assistant Server...
echo Open your browser to: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server.
echo.
uvicorn main:app --reload

pause
