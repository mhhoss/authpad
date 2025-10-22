#!/bin/bash

echo "Setting up ☑️"
# vir env
python3 -m venv .venv
source .venv/bin/activate

echo "Install dependencies"
pip install --upgrade pip
pip install -r requirements.txt

echo "Running tests ☑️"
pytest -v --disable-warnings

echo "Setup complete ☑️"
