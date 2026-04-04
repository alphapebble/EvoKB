#!/bin/bash
# EvoKB CLI - Quick start script

echo "=========================================="
echo "EvoKB - Evolving Knowledge Base"
echo "=========================================="

# Check if virtualenv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtualenv
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e .

# Create directories
mkdir -p raw wiki clusters

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Commands:"
echo "  evokb              # Start the librarian"
echo "  evokb-api           # Start the API server"
echo "  python test_accuracy.py   # Run accuracy tests"
echo "  python run_autoreview.py   # Run autoreview loop"
echo ""
echo "Or use uv:"
echo "  uv pip install -e ."
echo ""
