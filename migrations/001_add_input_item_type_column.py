#!/usr/bin/env python3
"""
Migration script to add input_item_type enum and type column to input_items table.
"""
import psycopg2
import sys

# Database connection parameters (matching run_migration.py)
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
        
        # 1. Create Enum Type if not exists
        print("Checking/Creating input_item_type ENUM...")
        cursor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'input_item_type') THEN
                    CREATE TYPE input_item_type AS ENUM ('FERTILIZER', 'PESTICIDE', 'OTHER');
                    RAISE NOTICE 'Created input_item_type ENUM';
                ELSE
                    RAISE NOTICE 'input_item_type ENUM already exists';
                END IF;
            END$$;
        """)
        
        # 2. Add column to table if not exists
        print("Adding type column to input_items table...")
        cursor.execute("""
            ALTER TABLE input_items 
            ADD COLUMN IF NOT EXISTS type input_item_type;
        """)
        
        conn.commit()
        print("✅ Migration checks/updates completed successfully!")
        
        # Verify
        cursor.execute("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns 
            WHERE table_name = 'input_items' AND column_name = 'type';
        """)
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Verified: Column '{result[0]}' exists with type '{result[2]}'")
        else:
            print("❌ Error: Column 'type' NOT found after migration!")
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
