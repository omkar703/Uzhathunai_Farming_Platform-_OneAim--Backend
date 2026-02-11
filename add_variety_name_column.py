import sys
import os
from sqlalchemy import create_engine, text

# Add current dir to path to allow imports if needed
sys.path.append(os.getcwd())

from app.core.config import settings

def update_schema():
    print(f"Connecting to database...")
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        trans = conn.begin()
        
        try:
            print("Checking crops table...")
            # Add variety_name column to crops table
            conn.execute(text("ALTER TABLE crops ADD COLUMN IF NOT EXISTS variety_name VARCHAR(200)"))
            print("Added variety_name to crops table")
            
            trans.commit()
            print("Schema update completed successfully.")
        except Exception as e:
            trans.rollback()
            print(f"Error updating schema: {e}")
            raise

if __name__ == "__main__":
    update_schema()
