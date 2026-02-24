"""
Add pricing_variants to fsp_service_listings

Revision ID: 016_add_pricing_variants
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
    """Add pricing_variants JSONB column to fsp_service_listings table."""
    logger.info("Starting migration: Add pricing_variants to fsp_service_listings")
    
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
                WHERE table_name = 'fsp_service_listings'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            logger.info("Table 'fsp_service_listings' does not exist yet. Migration skipped.")
            return
            
        # Check if column exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'fsp_service_listings' AND column_name = 'pricing_variants'
            );
        """)
        column_exists = cursor.fetchone()[0]
        
        if column_exists:
            logger.info("Column 'pricing_variants' already exists in 'fsp_service_listings'.")
            return
            
        # Add column
        logger.info("Adding 'pricing_variants' JSONB column to 'fsp_service_listings'...")
        cursor.execute("""
            ALTER TABLE fsp_service_listings 
            ADD COLUMN pricing_variants JSONB DEFAULT '[]'::jsonb;
        """)
        
        logger.info("Migration completed successfully.")
        
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
