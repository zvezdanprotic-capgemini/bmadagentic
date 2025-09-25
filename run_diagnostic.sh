#!/bin/zsh

# Script to run diagnostic tool with virtual environment
# Usage: ./run_diagnostic.sh

# Go to project root
cd "$(dirname "$0")/bmad-backend"

# Activate virtual environment
source venv/bin/activate

# Run the diagnostic script
python /Users/zvezdanprotic/Downloads/BMAD/bmad-backend/diagnostic.py