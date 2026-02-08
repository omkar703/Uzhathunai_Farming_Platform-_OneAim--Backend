#!/usr/bin/env python3
"""
Migration script to add access_granted column to work_orders table.
"""
import psycopg2
import os

# Database connection parameters
# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('POSTGRES_SERVER', 'db'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'farm_db'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
}

def run_migration():
    """Execute the migration to add access_granted column."""
    try:
        # Connect to database
        print(f"Connecting to database {DB_CONFIG['database']} on {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Execute migration
        print("Executing migration: Adding access_granted column to work_orders table...")
        
        # Add column with default TRUE
        cursor.execute("ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS access_granted BOOLEAN DEFAULT TRUE;")
        
        # Commit changes
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # Verify the column was added
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'work_orders' AND column_name = 'access_granted';
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"✅ Verified: Column '{result[0]}' added with type '{result[1]}'")
        else:
            print("⚠️  Warning: Could not verify column was added")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
