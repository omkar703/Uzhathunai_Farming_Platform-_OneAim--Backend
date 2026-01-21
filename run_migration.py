#!/usr/bin/env python3
"""
Quick migration script to add the city column to farms table.
This script connects to the database and runs the migration.
"""
import psycopg2
import os

# Database connection parameters (from docker-compose.yml)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'aggroconnect',
    'user': 'postgres',
    'password': 'postgres123'
}

def run_migration():
    """Execute the migration to add city column."""
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Execute migration
        print("Executing migration: Adding city column to farms table...")
        cursor.execute("ALTER TABLE farms ADD COLUMN IF NOT EXISTS city VARCHAR(100);")
        
        # Commit changes
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # Verify the column was added
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'farms' AND column_name = 'city';
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"✅ Verified: Column '{result[0]}' added with type '{result[1]}({result[2]})'")
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
