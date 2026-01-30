#!/usr/bin/env python3
"""
Migration script to add default_unit_id column to input_items table.
"""
import psycopg2
import sys
import os

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('POSTGRES_SERVER', 'db'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'farm_db'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
}

def run_migration():
    """Execute the migration."""
    conn = None
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Add column to table if not exists
        print("Adding default_unit_id column to input_items table...")
        cursor.execute("""
            ALTER TABLE input_items 
            ADD COLUMN IF NOT EXISTS default_unit_id UUID REFERENCES measurement_units(id);
        """)
        
        conn.commit()
        print("✅ Migration checks/updates completed successfully!")
        
        # Verify
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = 'input_items' AND column_name = 'default_unit_id';
        """)
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Verified: Column '{result[0]}' exists with type '{result[1]}'")
        else:
            print("❌ Error: Column 'default_unit_id' NOT found after migration!")
            return False

        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Error executing migration: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
