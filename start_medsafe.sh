#!/bin/bash

echo "========================================"
echo "   MedSafe - AI-Powered Prescription"
echo "   Verification System"
echo "========================================"
echo

# Check if virtual environment exists
if [ ! -d "medsafe-env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv medsafe-env
fi

# Activate virtual environment
echo "Activating virtual environment..."
source medsafe-env/bin/activate

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo
echo "========================================"
echo "Starting MedSafe Backend Server..."
echo "========================================"
echo
echo "The backend will be available at: http://localhost:8000"
echo
echo "Press Ctrl+C to stop the server"
echo

# Start the backend server
python start_backend.py
