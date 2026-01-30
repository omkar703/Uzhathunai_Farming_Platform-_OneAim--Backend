
import sys
import os

# Create a small script to verify that AuditResponsePhoto constructor works
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from uuid import uuid4

# Mocking the context or just trying to instantiate the model
sys.path.append(os.getcwd())
from app.models.audit import AuditResponsePhoto

def test_instantiation():
    print("Testing AuditResponsePhoto instantiation...")
    try:
        photo = AuditResponsePhoto(
            audit_response_id=uuid4(),
            file_url="https://example.com/photo.jpg",
            file_key="key",
            caption="test",
            uploaded_by=uuid4()
        )
        print("✅ Instantiation successful without audit_id/source_type")
    except TypeError as e:
        print(f"❌ Instantiation failed: {e}")
        sys.exit(1)

    try:
        print("Testing instantiation with legacy arguments (should fail now)...")
        AuditResponsePhoto(audit_id=uuid4())
        print("❌ Error: Instantiation with audit_id succeeded but should have failed!")
        sys.exit(1)
    except TypeError:
        print("✅ Correctly rejected audit_id")

if __name__ == "__main__":
    test_instantiation()
