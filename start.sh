#!/bin/bash

echo "🔍 Client Hunter - Business Scraper"
echo "====================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required (found $python_version)"
    exit 1
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "⚠️ Dependencies not installed. Running setup..."
    python3 setup.py
    if [ $? -ne 0 ]; then
        echo "❌ Setup failed"
        exit 1
    fi
fi

# Create data directory
mkdir -p data

# Run tests
echo "🧪 Running quick tests..."
python3 test.py
if [ $? -ne 0 ]; then
    echo "⚠️ Some tests failed, but continuing..."
fi

echo
echo "🚀 Starting Client Hunter..."
echo
echo "💡 The application will open in your default browser"
echo "📍 URL: http://localhost:8501"
echo
echo "⏹️ Press Ctrl+C to stop the application"
echo

# Start Streamlit
streamlit run app.py
