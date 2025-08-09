#!/usr/bin/env python3
"""
Setup script for Client Hunter Web Scraper
Run this script to set up the environment and install dependencies.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {command}")
            return True
        else:
            print(f"❌ {command}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running {command}: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = ['data', 'logs']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_requirements():
    """Install Python requirements."""
    print("📦 Installing Python requirements...")
    
    # Upgrade pip first
    run_command(f"{sys.executable} -m pip install --upgrade pip")
    
    # Install requirements
    if run_command(f"{sys.executable} -m pip install -r requirements.txt"):
        print("✅ Python requirements installed successfully")
        return True
    else:
        print("❌ Failed to install Python requirements")
        return False

def install_playwright():
    """Install Playwright browsers."""
    print("🎭 Installing Playwright browsers...")
    
    if run_command("playwright install chromium"):
        print("✅ Playwright browsers installed successfully")
        return True
    else:
        print("⚠️ Playwright browser installation failed (optional)")
        return False

def create_env_file():
    """Create .env file with default settings."""
    env_content = """# Client Hunter Configuration
# Database settings
DATABASE_PATH=data/businesses.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=data/scraping.log

# Scraping settings
DEFAULT_DELAY_MIN=1.0
DEFAULT_DELAY_MAX=3.0
MAX_RESULTS_PER_SOURCE=50

# Browser settings (for Google Maps scraping)
HEADLESS_BROWSER=true
BROWSER_TIMEOUT=30

# Geocoding
ENABLE_GEOCODING=true
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with default settings")

def main():
    """Main setup function."""
    print("🔍 Client Hunter - Setup Script")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Create .env file
    print("\n⚙️ Creating configuration...")
    create_env_file()
    
    # Install requirements
    print("\n📦 Installing dependencies...")
    if not install_requirements():
        print("❌ Setup failed - could not install requirements")
        sys.exit(1)
    
    # Install Playwright browsers (optional)
    print("\n🎭 Installing browser drivers...")
    install_playwright()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Review settings in config.py and .env")
    print("2. Run the application with: streamlit run app.py")
    print("3. Open http://localhost:8501 in your browser")
    print("\n💡 Tips:")
    print("- Start with 'Quick Scrape' mode for testing")
    print("- Enable Google Maps scraping only if needed (requires browser)")
    print("- Check data/ folder for exported results")

if __name__ == "__main__":
    main()
