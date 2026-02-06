import os
import sys
from uuid import UUID
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

# Add app to path
sys.path.append(os.getcwd())

from app.models.audit import Audit, AuditResponse, AuditParameterInstance, AuditResponsePhoto
from app.core.config import settings

def test_queries():
    print("Testing DB connection...")
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("Fetching first audit...")
        audit = db.query(Audit).first()
        if not audit:
            print("No audits found.")
            return
        
        print(f"Testing queries for audit {audit.id}")
        
        # 1. Parameter Instances
        print("Querying AuditParameterInstance...")
        instances = db.query(AuditParameterInstance).filter(
            AuditParameterInstance.audit_id == audit.id
        ).all()
        print(f"Found {len(instances)} instances")
        
        # 2. Audit Responses
        print("Querying AuditResponse...")
        responses = db.query(AuditResponse).filter(
            AuditResponse.audit_id == audit.id
        ).all()
        print(f"Found {len(responses)} responses")
        
        # 3. Photo counts
        print("Querying photo counts...")
        photo_counts = db.query(
            AuditResponsePhoto.audit_response_id,
            func.count(AuditResponsePhoto.id)
        ).filter(
            AuditResponsePhoto.audit_id == audit.id,
            AuditResponsePhoto.audit_response_id.isnot(None)
        ).group_by(AuditResponsePhoto.audit_response_id).all()
        print(f"Found {len(photo_counts)} photo count rows")
        
        print("ALL QUERIES SUCCESSFUL")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_queries()
