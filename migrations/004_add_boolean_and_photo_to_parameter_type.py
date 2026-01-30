#!/usr/bin/env python3
"""
Migration script to add BOOLEAN and PHOTO values to parameter_type ENUM.
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
        conn.autocommit = True  # ALTER TYPE ... ADD VALUE cannot run in a transaction block
        cursor = conn.cursor()
        
        # Add BOOLEAN to enum
        print("Adding 'BOOLEAN' value to parameter_type enum...")
        try:
            cursor.execute("ALTER TYPE parameter_type ADD VALUE IF NOT EXISTS 'BOOLEAN';")
            print("✅ Added 'BOOLEAN' or it already exists.")
        except Exception as e:
            print(f"⚠️ Note on 'BOOLEAN': {e}")
        
        # Add PHOTO to enum
        print("Adding 'PHOTO' value to parameter_type enum...")
        try:
            cursor.execute("ALTER TYPE parameter_type ADD VALUE IF NOT EXISTS 'PHOTO';")
            print("✅ Added 'PHOTO' or it already exists.")
        except Exception as e:
            print(f"⚠️ Note on 'PHOTO': {e}")
            
        print("✅ Migration checks/updates completed successfully!")
        
        # Verify
        cursor.execute("""
            SELECT enumlabel 
            FROM pg_enum 
            JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
            WHERE pg_type.typname = 'parameter_type';
        """)
        results = [r[0] for r in cursor.fetchall()]
        print(f"Current enum values: {results}")
        
        if 'BOOLEAN' in results and 'PHOTO' in results:
            print("✅ Verification successful: Both 'BOOLEAN' and 'PHOTO' exist.")
        else:
            print(f"❌ Verification failed. Missing values. Found: {results}")
            return False

        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Error executing migration: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
