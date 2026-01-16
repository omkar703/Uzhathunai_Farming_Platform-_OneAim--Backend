#!/bin/bash
set -e

echo "Starting Uzhathunai Backend Entrypoint..."

# Initialize Database
echo "Running Database Initialization (init_db.py)..."
python scripts/init_db.py

# Start the Server
echo "Initialization complete. Starting uvicorn..."
exec "$@"
