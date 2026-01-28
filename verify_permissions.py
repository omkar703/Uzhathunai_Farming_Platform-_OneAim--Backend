
import sys
import os
import uuid
from unittest.mock import MagicMock

# Add project root to sys.path
# sys.path.append("/home/gol-d-roger/onetech/Farm -Management -Main frontend /Uzhathunai_Farming_Platform-_OneAim--Backend")


from app.api.v1.farm_audit.sections import get_user_organization_id as get_section_org_id
from app.api.v1.farm_audit.parameters import get_user_organization_id as get_param_org_id
from app.models.user import User

def test_get_user_organization_id_super_admin():
    print("Testing get_user_organization_id for Super Admin...")
    
    # Mock DB Session
    db = MagicMock()
    user = User(id=uuid.uuid4(), email="admin@system.com")
    
    # Mock checks
    # db.query(OrgMemberRole).join(Role).filter(...).first() should return something
    mock_query = db.query.return_value
    mock_join = mock_query.join.return_value
    mock_filter = mock_join.filter.return_value
    mock_filter.first.return_value = "Found Role" # Simulate found
    
    # Test Section
    org_id_section = get_section_org_id(user, db)
    if org_id_section is None:
        print("SUCCESS: Section org_id is None for Super Admin")
    else:
        print(f"FAILURE: Section org_id should be None, got {org_id_section}")

    # Test Parameter
    org_id_param = get_param_org_id(user, db)
    if org_id_param is None:
        print("SUCCESS: Parameter org_id is None for Super Admin")
    else:
        print(f"FAILURE: Parameter org_id should be None, got {org_id_param}")

def test_get_user_organization_id_regular_user():
    print("\nTesting get_user_organization_id for Regular User...")
    
    # Mock DB Session
    db = MagicMock()
    user = User(id=uuid.uuid4(), email="user@org.com")
    fake_org_id = uuid.uuid4()
    
    # Mock checks
    # 1. Super Admin check -> Returns None
    mock_query = db.query.return_value
    mock_join = mock_query.join.return_value
    mock_filter = mock_join.filter.return_value
    
    # We need to distinguish calls. 
    # The first query is for Super Admin. We want it to return None.
    # The second query is for OrgMember. We want it to return membership.
    
    # This is tricky with simple mocks if calls are chained similarly.
    # Let's side_effect based on args if possible, or just build a chain that returns None then Something.
    
    # But db.query is called with different models.
    # db.query(OrgMemberRole) vs db.query(OrgMember)
    
    def side_effect(model):
        mock_obj = MagicMock()
        if "OrgMemberRole" in str(model):
            # Super Admin Check chain
            mock_obj.join.return_value.filter.return_value.first.return_value = None
        elif "OrgMember" in str(model):
            # Org Member Check chain
            membership = MagicMock()
            membership.organization_id = fake_org_id
            mock_obj.filter.return_value.first.return_value = membership
        return mock_obj

    db.query.side_effect = side_effect
    
    from app.core.exceptions import PermissionError
    
    try:
        # Test Section
        org_id_section = get_section_org_id(user, db)
        if org_id_section == fake_org_id:
            print("SUCCESS: Section org_id matches fake_org_id")
        else:
            print(f"FAILURE: Section org_id mismatch. Expected {fake_org_id}, got {org_id_section}")
            
        # Test Parameter
        org_id_param = get_param_org_id(user, db)
        if org_id_param == fake_org_id:
            print("SUCCESS: Parameter org_id matches fake_org_id")
        else:
            print(f"FAILURE: Parameter org_id mismatch. Expected {fake_org_id}, got {org_id_param}")
            
    except PermissionError as e:
        print(f"FAILURE: Unexpected PermissionError: {e}")

if __name__ == "__main__":
    try:
        test_get_user_organization_id_super_admin()
        test_get_user_organization_id_regular_user()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
