"""
Fix postgres enums and update column limits

Revision ID: 019_fix_enums_and_limits
"""
import os
import sys
import logging
import psycopg2
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Add REJECTED to organization_status and update schedule_templates.code limit."""
    logger.info("Starting migration: 019_fix_enums_and_limits")
    
    # Get database URL from environment
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL environment variable is not set.")
        sys.exit(1)
        
    try:
        # Parse connection URL
        result = urlparse(db_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        
        # Connect to DB
        logger.info(f"Connecting to database {database} at {hostname}:{port}")
        conn = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=hostname,
            port=port
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 1. Add REJECTED to organization_status
        # Check if REJECTED already exists
        cursor.execute("""
            SELECT 1 FROM pg_enum
            WHERE enumlabel = 'REJECTED' AND enumtypid = (
                SELECT oid FROM pg_type WHERE typname = 'organization_status'
            )
        """)
        
        if cursor.fetchone():
            logger.info("Enum literal 'REJECTED' already exists in type 'organization_status'")
        else:
            logger.info("Adding 'REJECTED' to 'organization_status'")
            cursor.execute("ALTER TYPE organization_status ADD VALUE 'REJECTED'")
            
        # 2. Update schedule_templates code character limit to 100
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'schedule_templates'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            logger.info("Updating 'code' VARCHAR(100) on 'schedule_templates'...")
            cursor.execute("""
                ALTER TABLE schedule_templates 
                ALTER COLUMN code TYPE VARCHAR(100);
            """)
        else:
            logger.info("Table 'schedule_templates' does not exist yet. Code limit change skipped.")
            
        logger.info("Migration 019 completed successfully.")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration()
