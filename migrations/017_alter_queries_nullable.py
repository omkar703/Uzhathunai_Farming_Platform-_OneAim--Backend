"""
Alter queries table to allow null fsp_organization_id and work_order_id

Revision ID: 017_alter_queries_nullable
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
    """Alter queries table to allow null in fsp_organization_id and work_order_id."""
    logger.info("Starting migration: Make fsp_organization_id and work_order_id nullable in queries")
    
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
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'queries'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            logger.info("Table 'queries' does not exist yet. Migration skipped.")
            return
            
        logger.info("Altering column 'fsp_organization_id' and 'work_order_id' to DROP NOT NULL constraint...")
        cursor.execute("""
            ALTER TABLE queries ALTER COLUMN fsp_organization_id DROP NOT NULL;
            ALTER TABLE queries ALTER COLUMN work_order_id DROP NOT NULL;
        """)
        
        logger.info("Migration 017 completed successfully.")
        
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
