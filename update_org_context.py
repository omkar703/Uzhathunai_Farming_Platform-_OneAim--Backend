"""
Batch update script to replace .first() organization lookups with helper function.
Run this script to update all API endpoints to use organization context from JWT.
"""
import re
import os
from pathlib import Path

# Pattern to match the old organization lookup code
OLD_PATTERN = r"""    # Get user's current organization
    from app\.models\.organization import OrgMember
    from app\.models\.enums import MemberStatus
    
    membership = db\.query\(OrgMember\)\.filter\(
        OrgMember\.user_id == current_user\.id,
        OrgMember\.status == MemberStatus\.ACTIVE
    \)\.first\(\)
    
    if not membership:
        from app\.core\.exceptions import PermissionError
        raise PermissionError\(
            message="User is not a member of any organization",
            error_code="NO_ORGANIZATION_MEMBERSHIP"
        \)"""

# New code to replace with
NEW_CODE = """    from app.core.organization_context import get_organization_id
    
    # Get organization ID from JWT token
    org_id = get_organization_id(current_user, db)"""

# Pattern to replace membership.organization_id with org_id
MEMBERSHIP_ORG_PATTERN = r"membership\.organization_id"

def update_file(filepath):
    """Update a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Replace the organization lookup pattern
    content = re.sub(OLD_PATTERN, NEW_CODE, content, flags=re.MULTILINE)
    
    # Replace membership.organization_id with org_id
    content = re.sub(MEMBERSHIP_ORG_PATTERN, "org_id", content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Update all API endpoint files."""
    api_dir = Path("/home/gol-d-roger/onetech/Farm -Management -Main frontend /Uzhathunai_Farming_Platform-_OneAim--Backend/app/api/v1")
    
    updated_files = []
    
    # Find all Python files
    for py_file in api_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        
        if update_file(py_file):
            updated_files.append(str(py_file.relative_to(api_dir.parent.parent)))
    
    print(f"Updated {len(updated_files)} files:")
    for f in updated_files:
        print(f"  - {f}")

if __name__ == "__main__":
    main()
