"""
Verify sync_status enum fix
"""
from app.core.database import SessionLocal
from app.models.audit import Audit
from app.models.enums import SyncStatus, AuditStatus
from sqlalchemy import text
import uuid
from datetime import datetime

db = SessionLocal()

print("=" * 80)
print("VERIFYING SYNC STATUS ENUM FIX")
print("=" * 80)

try:
    # Test 1: Verify we can insert PENDING_SYNC (default)
    print("\nTest 1: Inserting audit with PENDING_SYNC...")
    
    audit_id_1 = uuid.uuid4()
    
    # Create raw record to bypass service complexity for this specific test
    # (Just testing the model/enum serialization)
    audit = Audit(
        id=audit_id_1,
        fsp_organization_id=uuid.UUID("5504357f-21a4-4877-b78e-37f8fe7dfec5"),
        farming_organization_id=uuid.UUID("5504357f-21a4-4877-b78e-37f8fe7dfec5"), # Using same for test
        crop_id=uuid.UUID("e8d15069-2c06-44b4-934c-687f21226154"), # Need a valid crop ID, using one from previous context if possible or dummy
        template_id=uuid.UUID("32ed7afe-093f-486a-91df-8dcf4c2f3996"), # Existing template
        name="Enum Test Pending",
        status=AuditStatus.DRAFT,
        sync_status=SyncStatus.PENDING_SYNC,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Note: We need valid foreign keys for this to work.
    # Let's try to find valid FKs first
    valid_org = db.execute(text("SELECT id FROM organizations LIMIT 1")).scalar()
    valid_crop = db.execute(text("SELECT id FROM crops LIMIT 1")).scalar()
    valid_template = db.execute(text("SELECT id FROM templates LIMIT 1")).scalar()
    
    if valid_org and valid_crop and valid_template:
        audit.fsp_organization_id = valid_org
        audit.farming_organization_id = valid_org
        audit.crop_id = valid_crop
        audit.template_id = valid_template
        
        db.add(audit)
        db.commit()
        print("✅ Test 1 Passed: Successfully inserted PENDING_SYNC")
    else:
        print("⚠️ Skipped Test 1: Could not find valid foreign keys to test insert")

    # Test 2: Verify we can insert SYNCED (legacy/other value)
    print("\nTest 2: Inserting audit with SYNCED...")
    
    audit_id_2 = uuid.uuid4()
    audit2 = Audit(
        id=audit_id_2,
        fsp_organization_id=valid_org,
        farming_organization_id=valid_org,
        crop_id=valid_crop,
        template_id=valid_template,
        name="Enum Test Synced",
        status=AuditStatus.DRAFT,
        sync_status=SyncStatus.SYNCED,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    if valid_org:
        db.add(audit2)
        db.commit()
        print("✅ Test 2 Passed: Successfully inserted SYNCED")
        
        # Verify what's in the DB
        result = db.execute(text(f"SELECT sync_status FROM audits WHERE id = '{audit_id_2}'")).scalar()
        print(f"   DB Value for SYNCED: '{result}' (Expected: 'synced')")
        
        if result == 'synced':
            print("✅ Data validation: Value is lowercase in DB")
        else:
            print(f"❌ Data validation: Expected 'synced', got '{result}'")

except Exception as e:
    db.rollback()
    print(f"\n❌ Test Failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Cleanup
    try:
        if 'audit_id_1' in locals():
            db.execute(text(f"DELETE FROM audits WHERE id = '{audit_id_1}'"))
        if 'audit_id_2' in locals():
            db.execute(text(f"DELETE FROM audits WHERE id = '{audit_id_2}'"))
        db.commit()
        print("\nCleanup completed.")
    except:
        pass
    db.close()
