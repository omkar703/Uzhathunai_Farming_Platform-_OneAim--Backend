
import sys
import os
import uuid
from sqlalchemy.orm import Session

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.organization import Organization
from app.models.enums import OrganizationType, OrganizationStatus
from app.models.user import User

def create_liomonk_org():
    db = SessionLocal()
    try:
        # Check if exists
        existing = db.query(Organization).filter(Organization.name.ilike("%LioMonk%")).first()
        if existing:
            print(f"Organization already exists: {existing.name}")
            return

        # Get a user to be the owner (e.g., fsp1@gmail.com created in previous seed)
        user = db.query(User).filter(User.email == "fsp1@gmail.com").first()
        if not user:
            print("User fsp1@gmail.com not found. Using first available user.")
            user = db.query(User).first()
            if not user:
                 print("No users found. Cannot create organization.")
                 return

        print(f"Creating LioMonk Org with owner: {user.email}")
        
        org = Organization(
            id=uuid.uuid4(),
            name="LioMonk FSP Services",
            organization_type=OrganizationType.FSP,
            status=OrganizationStatus.ACTIVE,
            created_by=user.id
        )
        db.add(org)
        db.commit()
        print(f"Created Organization: {org.name} ({org.id})")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_liomonk_org()
