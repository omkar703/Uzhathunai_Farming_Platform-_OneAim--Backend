import os
import sys
from uuid import UUID
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add app directory to path
sys.path.append(os.getcwd())

from app.services.dashboard_service import DashboardService
from app.models import Organization, OrgMember, User
from app.models.enums import OrganizationType, MemberStatus

# Database configuration (using internal docker address)
DATABASE_URL = "postgresql://postgres:postgres@db:5432/uzhathunai_db_v2"

def verify_dashboard():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Find an FSP organization
        fsp_org = db.query(Organization).filter(Organization.organization_type == OrganizationType.FSP).first()
        if not fsp_org:
            print("No FSP organization found for testing.")
            return

        # Find an active member of that org
        member = db.query(OrgMember).filter(
            OrgMember.organization_id == fsp_org.id,
            OrgMember.status == MemberStatus.ACTIVE
        ).first()

        if not member:
            print(f"No active member found for FSP org: {fsp_org.name}")
            return

        print(f"Verifying dashboard for FSP: {fsp_org.name} (ID: {fsp_org.id})")
        print(f"Using member User ID: {member.user_id}")

        service = DashboardService(db)
        dashboard_data = service.get_fsp_dashboard(user_id=member.user_id, org_id=fsp_org.id)

        # Check stats
        stats = dashboard_data.get('stats', {})
        expected_keys = [
            'activeClients', 'activeOrders', 'auditsInProgress', 
            'pendingQueries', 'activeTeam', 'totalRevenue', 'totalServices'
        ]
        
        print("\nStats Check:")
        for key in expected_keys:
            value = stats.get(key)
            print(f"  {key}: {value} ({type(value).__name__})")
            if value is None:
                print(f"  [Error] Key '{key}' is missing or None")

        # Check Recent Activity
        activities = dashboard_data.get('recentActivity', [])
        print(f"\nRecent Activity Check ({len(activities)} items):")
        for i, activity in enumerate(activities):
            print(f"  Item {i+1}:")
            print(f"    type: {activity.get('type')}")
            print(f"    description: {activity.get('description')}")
            print(f"    timestamp: {activity.get('timestamp')}")
            print(f"    metadata: {activity.get('metadata')}")
            
            # Verify required fields
            if not activity.get('type') or not activity.get('description') or not activity.get('timestamp'):
                print("    [Error] Missing required fields in activity item")

    except Exception as e:
        print(f"Error during verification: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_dashboard()
