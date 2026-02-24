#!/bin/bash
set -e

echo "Starting Uzhathunai Backend Entrypoint..."

# Initialize Database
echo "Running Database Initialization (init_db.py)..."
python scripts/init_db.py

# Run Python-based Migrations
echo "Running Python Migrations..."
python run_all_migrations.py

# Start the Server
echo "Initialization complete. Starting uvicorn..."
exec "$@"
