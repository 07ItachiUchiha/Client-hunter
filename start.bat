@echo off
echo 🔍 Client Hunter - Business Scraper
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
echo 📦 Checking dependencies...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Dependencies not installed. Running setup...
    python setup.py
    if errorlevel 1 (
        echo ❌ Setup failed
        pause
        exit /b 1
    )
)

REM Create data directory
if not exist "data" mkdir data

REM Run tests
echo 🧪 Running quick tests...
python test.py
if errorlevel 1 (
    echo ⚠️ Some tests failed, but continuing...
)

echo.
echo 🚀 Starting Client Hunter...
echo.
echo 💡 The application will open in your default browser
echo 📍 URL: http://localhost:8501
echo.
echo ⏹️ Press Ctrl+C in this window to stop the application
echo.

REM Start Streamlit
streamlit run app.py

pause
