"""
Add responder_role to query_responses

Revision ID: 018_add_responder_role
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
    """Add responder_role column to query_responses table."""
    logger.info("Starting migration: Add responder_role to query_responses")
    
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
                WHERE table_name = 'query_responses'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            logger.info("Table 'query_responses' does not exist yet. Migration skipped.")
            return
            
        # Check if column exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'query_responses' AND column_name = 'responder_role'
            );
        """)
        column_exists = cursor.fetchone()[0]
        
        if column_exists:
            logger.info("Column 'responder_role' already exists in 'query_responses'.")
            return
            
        # Add column
        logger.info("Adding 'responder_role' VARCHAR(20) column to 'query_responses'...")
        cursor.execute("""
            ALTER TABLE query_responses 
            ADD COLUMN responder_role VARCHAR(20);
        """)
        
        logger.info("Migration 018 completed successfully.")
        
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
