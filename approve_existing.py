import sys
import os
from sqlalchemy import create_engine, text

# Add app directory to path
sys.path.append(os.getcwd())

from app.core.config import settings
from app.core.database import SessionLocal

def approve_pending_orgs():
    db = SessionLocal()
    try:
        print("Approving all NOT_STARTED organizations...")
        
        # Update organizations
        sql = text("UPDATE organizations SET status = 'ACTIVE' WHERE status = 'NOT_STARTED'")
        result = db.execute(sql)
        
        print(f"Updated {result.rowcount} organizations to ACTIVE.")
        
        db.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    approve_pending_orgs()
