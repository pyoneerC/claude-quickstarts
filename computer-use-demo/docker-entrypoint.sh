#!/bin/bash

# Start all desktop services
./start_all.sh &

# Wait for X server to be ready
echo "Waiting for X server..."
sleep 3

# Start FastAPI backend
cd /home/computeruse
echo "Starting FastAPI backend..."
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
