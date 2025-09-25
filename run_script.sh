#!/bin/zsh

# Script to run Python modules from the project root with virtual environment
# Usage: ./run_script.sh app.graphs.team_graph

# Go to project root
cd "$(dirname "$0")/bmad-backend"

# Activate virtual environment
source venv/bin/activate

# Run the module specified by the first argument
python -m "$1"