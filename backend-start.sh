#!/bin/bash
cd "/Users/fddiferd/GitHub/wristband/wb-python-fastapi-accelerator/backend"
echo "Installing backend dependencies..."
poetry install
echo "Starting backend server..."
poetry run uvicorn app:app --host 0.0.0.0 --port 8080 --reload
