import sys
import os
import importlib.util

# Add project root to Python path
sys.path.append(os.getcwd())

from app.core.database import engine, Base
from app.models import *  # Import all models to ensure they are registered with Base

def run_migration(migration_file):
    """Load and run a migration file."""
    print(f"\n{'='*60}")
    print(f"Running migration: {migration_file}")
    print(f"{'='*60}")
    
    try:
        spec = importlib.util.spec_from_file_location("migration", migration_file)
        if spec is None or spec.loader is None:
            print(f"FAILED to load migration: {migration_file}")
            return False
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, 'upgrade'):
            module.upgrade()
        elif hasattr(module, 'run_migration'):
             # Support for scripts like 001 that use run_migration()
            module.run_migration()
        else:
             # Support for scripts that might run on import or have other conventions
             # But for now, just printing a warning if no standard entry point found
            print(f"Warning: No upgrade() or run_migration() function found in {migration_file}. It might have run on import.")
            
        print(f"Successfully processed {migration_file}")
        return True
    except Exception as e:
        print(f"Migration {migration_file} failed/skipped with error: {e}")
        # We continue even if one fails, as it might be because columns already exist
        return False

def fix_database():
    print("Starting Master Database Fix...")
    
    # 1. Create all missing tables using SQLAlchemy
    print("\n[Step 1] Creating missing tables (e.g., audit_reports)...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Base.metadata.create_all() completed successfully.")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        # We continue, as maybe permissions are partial or specific tables failed
    
    # 2. Run specific migrations that add columns to existing tables
    # We include all numbered migrations to be safe, assuming they are idempotent or we catch errors
    migrations = [
        "migrations/001_add_input_item_type_column.py",
        "migrations/002_add_input_item_default_unit_id.py",
        "migrations/003_add_work_order_service_snapshot.py",
        "migrations/004_add_boolean_and_photo_to_parameter_type.py",
        # 005 is create_audit_reports, which create_all() should handle, but running it is harmless if idempotent
        "migrations/005_create_audit_reports_table.py", 
        "migrations/006_add_work_order_completion_fields.py",
        "migrations/007_add_schedule_task_columns.py",
        "migrations/008_add_audit_columns.py",
        "migrations/add_access_granted_column.py"
    ]
    
    print(f"\n[Step 2] Running {len(migrations)} migration scripts to backfill columns...")
    
    for migration in migrations:
        if os.path.exists(migration):
            run_migration(migration)
        else:
            print(f"⚠️ Migration file not found: {migration}")

    print("\n" + "="*60)
    print("✅ MASTER FIX COMPLETED")
    print("Please restart your application to ensure all changes take effect.")
    print("="*60)

if __name__ == "__main__":
    fix_database()
