import sys
import os
from sqlalchemy import create_engine, text

# Add current dir to path to allow imports if needed
sys.path.append(os.getcwd())

from app.core.config import settings

def update_schema():
    print(f"Connecting to database...")
    # Masking password in logs potentially
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        trans = conn.begin()
        
        try:
            # 1. Add is_flagged_for_report to audit_response_photos
            print("Checking audit_response_photos...")
            conn.execute(text("ALTER TABLE audit_response_photos ADD COLUMN IF NOT EXISTS is_flagged_for_report BOOLEAN DEFAULT FALSE NOT NULL"))
            print("Added is_flagged_for_report to audit_response_photos")

            # 2. Add recommendation to audit_issues
            print("Checking audit_issues...")
            conn.execute(text("ALTER TABLE audit_issues ADD COLUMN IF NOT EXISTS recommendation TEXT"))
            print("Added recommendation to audit_issues")

            # 3. Create audit_recommendations table
            print("Creating audit_recommendations table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS audit_recommendations (
                    id UUID PRIMARY KEY,
                    audit_id UUID NOT NULL REFERENCES audits(id) ON DELETE CASCADE,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    created_by UUID REFERENCES users(id)
                )
            """))
            print("Created audit_recommendations table")
            
            trans.commit()
            print("Schema update completed successfully.")
        except Exception as e:
            trans.rollback()
            print(f"Error updating schema: {e}")
            raise

if __name__ == "__main__":
    update_schema()
