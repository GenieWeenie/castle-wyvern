#!/bin/bash
# Castle Wyvern Installation Script
# Phase 1: Dependency Management

set -e

echo "🏰 Castle Wyvern - Installation"
echo "================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "✗ pip3 not found. Please install pip3 first."
    exit 1
fi
echo "✓ pip3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "→ Creating virtual environment..."
    python3 -m venv venv
fi
echo "✓ Virtual environment ready"

# Activate virtual environment
echo "→ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "→ Upgrading pip..."
pip install --upgrade pip

# Install Castle Wyvern
echo "→ Installing Castle Wyvern..."
pip install -e .

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Copy environment template: cp .env.example .env"
echo "3. Edit .env with your API keys"
echo "4. Test the installation: python3 eyrie/phoenix_gate.py"
echo "5. Awaken the clan: python3 clan_wyvern.py"