#!/bin/bash
# Price Tracker - Development Setup Script (Linux/Mac)
# Usage: ./scripts/setup.sh

set -e

echo "Setting up Price Tracker development environment..."

# Check Python version
python_version=$(python3 --version 2>/dev/null | awk '{print $2}' || echo "")
if [ -z "$python_version" ]; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi
echo "Python version: $python_version"

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Install Playwright browsers
echo "Installing Playwright Chromium..."
playwright install chromium

# Setup frontend
echo "Setting up frontend..."
cd frontend
npm install
cd ..

echo ""
echo "Setup complete!"
echo ""
echo "To start the backend:"
echo "  source .venv/bin/activate"
echo "  python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "To start the frontend (in another terminal):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Access points:"
echo "  Frontend: http://localhost:5173"
echo "  API Docs: http://localhost:8000/docs"
