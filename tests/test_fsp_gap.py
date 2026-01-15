
import pytest
from uuid import uuid4, UUID
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization import Organization, OrgMember
from app.models.farm import Farm
from app.models.enums import OrganizationType, MemberStatus
from app.api.v1.farms import get_farm
from app.services.farm_service import FarmService
from app.core.exceptions import PermissionError, NotFoundError

class TestFSPAccessGap:
    """
    Verify if FSP users can access farms they have Work Orders for.
    Current assumption: They cannot, because logic restricts to own-org.
    """

    def test_fsp_cannot_access_client_farm(self):
        """
        Scenario:
        1. User belongs to FSP Org.
        2. Farm belongs to Farming Org.
        3. User tries to get Farm.
        4. Expected: Should succeed if logic handles Work Orders, but code suggests it fails.
        """
        # Mocks
        mock_db = MagicMock(spec=Session)
        
        # 1. FSP User
        fsp_user_id = uuid4()
        fsp_org_id = uuid4()
        fsp_user = Mock(spec=User)
        fsp_user.id = fsp_user_id
        
        # 2. Farming Org & Farm
        farming_org_id = uuid4()
        farm_id = uuid4()
        
        # Mock Membership Query (User is member of FSP Org)
        # The router does: membership = db.query(OrgMember).filter(user_id==current_user.id).first()
        fsp_membership = Mock(spec=OrgMember)
        fsp_membership.organization_id = fsp_org_id
        fsp_membership.status = MemberStatus.ACTIVE
        
        mock_db.query.return_value.filter.return_value.first.return_value = fsp_membership

        # execute the router function logic simulation or call service directly
        # calling router function `get_farm` is hard because of Depends, so let's call Service directly
        # BUT the router passes `membership.organization_id` to the service!
        
        # Router logic simulation:
        # service.get_farm_by_id(farm_id, membership.organization_id)
        # This passes FSP_ORG_ID.
        
        service = FarmService(mock_db)
        
        # Mock the DB query inside service to return None because Org ID doesn't match
        # Service query: filter(Farm.id == farm_id, Farm.organization_id == FSP_ORG_ID)
        # But Farm.organization_id is FARMING_ORG_ID. So it will return None.
        
        # We simulate the DB returning None
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = None

        # Verify it raises NotFoundError
        with pytest.raises(NotFoundError) as excinfo:
            service.get_farm_by_id(farm_id, fsp_org_id)
        
        assert "Farm" in str(excinfo.value)
        assert "not found" in str(excinfo.value)

        # This confirms the GAP: The service asks "Give me farm X owned by Org Y".
        # If Org Y is FSP, and Farm X is owned by Org Z, it returns Nothing.
