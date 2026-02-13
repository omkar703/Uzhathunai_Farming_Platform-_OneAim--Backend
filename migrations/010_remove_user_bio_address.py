#!/usr/bin/env python3
"""
Migration script to remove bio and address columns from users table.
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
        
        print("Dropping bio and address columns from users table...")
        cursor.execute("""
            ALTER TABLE users 
            DROP COLUMN IF EXISTS bio,
            DROP COLUMN IF EXISTS address;
        """)
        
        conn.commit()
        print("✅ Migration checks/updates completed successfully!")
        
        # Verify
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns 
            WHERE table_name = 'users' AND (column_name = 'bio' OR column_name = 'address');
        """)
        results = cursor.fetchall()
        
        if not results:
            print(f"✅ Verified: Columns 'bio' and 'address' have been removed.")
        else:
            print(f"❌ Error: One or more columns still exist: {[r[0] for r in results]}")
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
