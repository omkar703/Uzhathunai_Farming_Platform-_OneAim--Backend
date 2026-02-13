#!/usr/bin/env python3
"""
Run all pending migrations in order.
"""
import sys
import glob
import os
import subprocess

def run_migration(migration_file):
    """Run a migration file using subprocess."""
    print(f"\n{'='*60}")
    print(f"Running migration: {migration_file}")
    print(f"{'='*60}")
    
    # Run the migration script as a separate process
    result = subprocess.run([sys.executable, migration_file], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Migration failed: {migration_file}")
        print("Output:")
        print(result.stdout)
        print("Error:")
        print(result.stderr)
        return False
        
    print(result.stdout)
    return True

def main():
    # Find all migration files
    migration_files = glob.glob("migrations/*.py")
    
    # Filter out __init__.py if it exists
    migration_files = [f for f in migration_files if not f.endswith("__init__.py")]
    
    # Sort files to ensure order (001, 002, etc.)
    migration_files.sort()
    
    print("Starting database migrations...")
    print(f"Found {len(migration_files)} migration files.")
    
    for migration in migration_files:
        if not run_migration(migration):
            sys.exit(1)
    
    print(f"\n{'='*60}")
    print("✅ All migrations completed successfully!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
