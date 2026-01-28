import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta

from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.audit import Audit
from app.models.work_order import WorkOrder
from app.models.rbac import Role
from app.models.enums import (
    OrganizationType,
    OrganizationStatus,
    MemberStatus,
    AuditStatus,
    WorkOrderStatus,
    UserRoleScope
)

# Reusing fixtures definition style or assuming conftest handles them if shared.
# Since test_organization_api.py defined fixtures locally or they are in conftest?
# `test_organization_api.py` defined `owner_role` fixture. I should define it here too or move to conftest.
# I will define needed fixtures here to be safe.

@pytest.fixture
def owner_role(db: Session) -> Role:
    """Get or create OWNER role."""
    role = db.query(Role).filter(Role.code == 'OWNER').first()
    if not role:
        role = Role(
            code='OWNER',
            name='Owner',
            display_name='Organization Owner',
            scope=UserRoleScope.ORGANIZATION,
            description='Owner of farming organization',
            is_active=True
        )
        db.add(role)
        db.commit()
        db.refresh(role)
    return role

class TestOrganizationDetails:
    """Tests for GET /api/v1/organizations/{id} with detailed info."""

    def test_get_organization_details_full(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        owner_role: Role,
        db: Session
    ):
        """Test getting organization details includes members, audits, wos."""
        
        # 1. Create Organization
        org = Organization(
            name="Detailed Farm",
            organization_type=OrganizationType.FARMING,
            status=OrganizationStatus.ACTIVE,
            created_by=test_user.id
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        
        # 2. Add Member (Self as Owner)
        member = OrgMember(
            user_id=test_user.id,
            organization_id=org.id,
            status=MemberStatus.ACTIVE
        )
        db.add(member)
        db.commit()
        
        member_role = OrgMemberRole(
            user_id=test_user.id,
            organization_id=org.id,
            role_id=owner_role.id,
            is_primary=True
        )
        db.add(member_role)
        db.commit()

        # 3. Create Audit (associated with this org)
        # Assuming we need a template and crop, but for brevity/fk constraints, 
        # we might need to mock or create dependencies if strict.
        # Let's check dependencies for Audit: crop_id, template_id, fsp_org_id, farming_org_id.
        
        # Create Dummy Crop
        from app.models.crop import Crop
        crop = Crop(name="Test Crop", code="TEST001", scientific_name="T", created_by=test_user.id)
        db.add(crop)
        db.commit()
        
        # Create Dummy Template
        from app.models.template import Template
        template = Template(
            code="TEMP001",
            version=1,
            is_active=True,
            crop_type_id=None, # if nullable
            created_by=test_user.id
        )
        # Note: Template model might have non-null constraints.
        # Checking db schema/models... crop_type_id is nullable (from service check: data.crop_type_id if data... else source...)
        # Actually Template model has: crop_type_id = Column(UUID..., ForeignKey...)
        # Wait, I didn't verify crop_type_id nullability in Template model view.
        # Assuming it is nullable or I need a crop type.
        
        # To avoid complex setup, I will try to create minimal valid entities.
        # However, FK constraints are real in integration tests.
        
        # Skip complex Audit/WO creation if too hard, 
        # but the task IS to verify them.
        # I'll try to create bare minimum.
        
        # Create FSP Org for relationship
        fsp_org = Organization(
            name="Auditor FSP",
            organization_type=OrganizationType.FSP,
            status=OrganizationStatus.ACTIVE,
            created_by=test_user.id
        )
        db.add(fsp_org)
        db.commit()

        # Create Template
        template.owner_org_id = fsp_org.id # or None
        db.add(template)
        db.commit()
        
        audit = Audit(
            farming_organization_id=org.id,
            fsp_organization_id=fsp_org.id,
            crop_id=crop.id,
            template_id=template.id,
            name="Test Audit",
            status=AuditStatus.COMPLETED,
            created_by=test_user.id
        )
        db.add(audit)
        db.commit()
        
        # 4. Create Work Order
        wo = WorkOrder(
            farming_organization_id=org.id,
            fsp_organization_id=fsp_org.id,
            title="Test Service",
            status=WorkOrderStatus.ACTIVE,
            total_amount=1000.0,
            start_date=datetime.now().date(),
            created_by=test_user.id
        )
        db.add(wo)
        db.commit()
        
        # 5. Call API
        response = client.get(
            f"/api/v1/organizations/{org.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        details = data['data']
        
        # 6. Verify Extensions
        assert "members" in details
        assert len(details["members"]) == 1
        assert details["members"][0]["user_id"] == str(test_user.id)
        assert details["members"][0]["role"] == "Owner"
        
        assert "recent_audits" in details
        assert len(details["recent_audits"]) == 1
        assert details["recent_audits"][0]["id"] == str(audit.id)
        
        assert "recent_work_orders" in details
        assert len(details["recent_work_orders"]) == 1
        assert details["recent_work_orders"][0]["id"] == str(wo.id)
        
        assert "stats" in details
        assert details["stats"]["total_members"] == 1
        assert details["stats"]["total_audits"] == 1
        assert details["stats"]["active_work_orders"] == 1
