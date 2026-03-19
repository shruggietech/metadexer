#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv"

if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at $VENV_DIR"
else
    python3 -m venv "$VENV_DIR"
    echo "Created virtual environment at $VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip --quiet
pip install -e ".[dev]" --quiet
echo "Development dependencies installed."
