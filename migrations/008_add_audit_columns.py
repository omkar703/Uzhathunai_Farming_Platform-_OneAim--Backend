"""
Add audit_id column to audit_response_photos and recommendation column to audit_issues.
"""
from sqlalchemy import text
from app.core.database import SessionLocal

def upgrade():
    db = SessionLocal()
    try:
        # Add audit_id to audit_response_photos
        db.execute(text("ALTER TABLE audit_response_photos ADD COLUMN IF NOT EXISTS audit_id UUID REFERENCES audits(id) ON DELETE CASCADE"))
        # Add recommendation to audit_issues  
        db.execute(text("ALTER TABLE audit_issues ADD COLUMN IF NOT EXISTS recommendation TEXT"))
        db.commit()
        print("Successfully added columns to audit tables.")
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    upgrade()
