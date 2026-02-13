#!/usr/bin/env python3
"""
Migration script to add specialization column to organizations table.
"""
import psycopg2
import sys
import os

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('POSTGRES_SERVER', 'aggroconnect_db'),
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
        
        print("Adding specialization column to organizations table...")
        cursor.execute("""
            ALTER TABLE organizations 
            ADD COLUMN IF NOT EXISTS specialization VARCHAR(200);
        """)
        
        conn.commit()
        print("✅ Migration checks/updates completed successfully!")
        
        # Verify
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'organizations' AND column_name = 'specialization';
        """)
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Verified: Column '{result[0]}' exists with type '{result[1]}({result[2]})'")
        else:
            print("❌ Error: Column 'specialization' NOT found after migration!")
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
