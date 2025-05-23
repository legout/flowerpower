#!/usr/bin/env python3
"""
Startup script for FlowerPower Web UI
"""

import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'sanic',
        'htpy', 
        'datastar_py'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install dependencies with:")
        print("   pip install -r requirements.txt")
        print("   # or with uv:")
        print("   uv pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def main():
    """Main startup function"""
    print("🌸 FlowerPower Web UI Startup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Error: app.py not found")
        print("💡 Make sure you're running this from the web_ui directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start the application
    print("\n🚀 Starting FlowerPower Web UI...")
    print("📍 URL: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop\n")
    
    try:
        from app import app
        app.run(host="0.0.0.0", port=8000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 FlowerPower Web UI stopped")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()