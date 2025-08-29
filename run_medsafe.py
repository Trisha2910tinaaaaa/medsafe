#!/usr/bin/env python3
"""
MedSafe Startup Script
Runs both the FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def run_backend():
    """Run the FastAPI backend"""
    print("🚀 Starting FastAPI Backend...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")
    except Exception as e:
        print(f"❌ Backend error: {e}")

def run_frontend():
    """Run the Streamlit frontend"""
    print("🌐 Starting Streamlit Frontend...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend.py", "--server.port", "8501"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped by user")
    except Exception as e:
        print(f"❌ Frontend error: {e}")

def main():
    print("💊 MedSafe - AI-Powered Prescription Verification System")
    print("=" * 60)
    
    # Check if required files exist
    required_files = ["main.py", "frontend.py", "requirements.txt"]
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return
    
    # Check if virtual environment exists
    venv_path = Path("medsafe-env")
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "medsafe-env"], check=True)
    
    # Install dependencies
    print("📦 Installing dependencies...")
    if os.name == 'nt':  # Windows
        pip_cmd = "medsafe-env\\Scripts\\pip"
    else:  # Unix/Linux/Mac
        pip_cmd = "medsafe-env/bin/pip"
    
    try:
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return
    
    print("\n🎯 Starting MedSafe System...")
    print("📋 Backend will run on: http://localhost:8000")
    print("🌐 Frontend will run on: http://localhost:8501")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("\n⏳ Starting services...")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend
    run_frontend()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 MedSafe stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
