@echo off
echo ========================================
echo    AeroCraft Backend Startup
echo ========================================
echo.

cd backend

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.11+ from python.org
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo [1/5] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
    echo.
)

REM Activate virtual environment
echo [2/5] Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)
echo Virtual environment activated!
echo.

REM Check for .env file
if not exist .env (
    echo [3/5] Creating .env file from template...
    copy .env.example .env
    echo.
    echo ============================================
    echo IMPORTANT: ADD YOUR OPENAI API KEY!
    echo ============================================
    echo Edit backend\.env and add your OpenAI API key
    echo Then run this script again.
    echo.
    pause
    exit /b 0
)

REM Install dependencies
echo [4/5] Installing/Updating dependencies...
echo This may take 2-3 minutes on first run...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo.
echo Dependencies installed successfully!
echo.

REM Start the server
echo [5/5] Starting FastAPI server...
echo.
echo ========================================
echo Backend running at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

uvicorn app.main:app --reload --port 8000
