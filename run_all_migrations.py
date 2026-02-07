#!/usr/bin/env python3
"""
Run all pending migrations in order.
"""
import sys
import importlib.util

def run_migration(migration_file):
    """Load and run a migration file."""
    print(f"\n{'='*60}")
    print(f"Running migration: {migration_file}")
    print(f"{'='*60}")
    
    spec = importlib.util.spec_from_file_location("migration", migration_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if hasattr(module, 'upgrade'):
        module.upgrade()
    else:
        print(f"Warning: No upgrade() function found in {migration_file}")

def main():
    migrations = [
        "migrations/006_add_work_order_completion_fields.py",
        "migrations/007_add_schedule_task_columns.py",
    ]
    
    print("Starting database migrations...")
    print(f"Total migrations to run: {len(migrations)}")
    
    for migration in migrations:
        try:
            run_migration(migration)
        except Exception as e:
            print(f"\n❌ Migration failed: {migration}")
            print(f"Error: {e}")
            sys.exit(1)
    
    print(f"\n{'='*60}")
    print("✅ All migrations completed successfully!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
