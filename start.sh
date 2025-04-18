#!/bin/bash
# VibeProto Startup Script for macOS/Linux

# Activate Python virtual environment
echo "Activating Python virtual environment..."
source .venv/bin/activate

# Start Flask backend (in a separate process)
echo "Starting Flask backend server..."
python backend/app.py &

# Store the PID of the Flask process
FLASK_PID=$!

# Start Node.js server
echo "Starting Node.js server..."
npm start

# When npm is terminated, also terminate the Flask process
kill $FLASK_PID 