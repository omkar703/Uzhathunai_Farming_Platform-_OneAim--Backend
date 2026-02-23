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
            # Add pricing_variants column to fsp_service_listings
            print("Checking fsp_service_listings...")
            conn.execute(text("ALTER TABLE fsp_service_listings ADD COLUMN IF NOT EXISTS pricing_variants JSONB DEFAULT '[]'::jsonb"))
            print("Added pricing_variants to fsp_service_listings")
            
            trans.commit()
            print("Schema update completed successfully.")
        except Exception as e:
            trans.rollback()
            print(f"Error updating schema: {e}")
            raise

if __name__ == "__main__":
    update_schema()
